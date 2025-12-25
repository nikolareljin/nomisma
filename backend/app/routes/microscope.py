from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import cv2
import os
from datetime import datetime
from uuid import uuid4
from typing import Optional

from ..services.microscope import microscope_service
router = APIRouter()

IMAGES_PATH = os.getenv("IMAGES_PATH", "/app/images")

@router.get("/devices")
async def list_devices():
    """List available camera devices"""
    try:
        cameras = microscope_service.list_available_cameras()
        return {
            "success": True,
            "cameras": cameras,
            "count": len(cameras)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/capture")
async def capture_image(
    camera_index: str = "0",
    image_type: str = "scan",
    side_hint: Optional[str] = None
):
    """Capture an image from the microscope"""
    try:
        # Open selected camera if needed
        if not microscope_service.ensure_camera(camera_index):
            raise HTTPException(status_code=500, detail="Failed to open camera")

        frame = microscope_service.get_frame()
        if frame is None:
            raise HTTPException(status_code=500, detail="Failed to capture image")

        quality_metrics = microscope_service.evaluate_frame_quality(frame)
        blur_score = quality_metrics["blur_score"]
        brightness = quality_metrics["brightness"]
        quality = {
            "blur_score": blur_score,
            "brightness": brightness,
            "is_blurry": blur_score < 120.0,
            "is_dark": brightness < 50.0,
            "is_bright": brightness > 205.0,
        }
        quality["ok"] = not (quality["is_blurry"] or quality["is_dark"] or quality["is_bright"])

        side_detection = microscope_service.detect_coin_side(frame)
        detected_label = side_detection.get("label") or "unknown"
        detected_confidence = side_detection.get("confidence") or 0.0

        normalized_hint = side_hint.lower().strip() if side_hint else ""
        if normalized_hint in ("obverse", "reverse"):
            side_label = normalized_hint
        elif detected_confidence >= 0.6:
            side_label = detected_label
        else:
            side_label = "unknown"

        # Generate unique filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"capture_{side_label}_{timestamp}_{uuid4().hex[:8]}.jpg"
        
        # Create temp directory
        temp_dir = os.path.join(IMAGES_PATH, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        save_path = os.path.join(temp_dir, filename)
        
        saved = microscope_service.save_frame(frame, save_path)
        if not saved:
            raise HTTPException(status_code=500, detail="Failed to save image")
        
        return {
            "success": True,
            "file_path": f"temp/{filename}",
            "url": f"/images/temp/{filename}",
            "timestamp": timestamp,
            "side": {
                "label": side_label,
                "detected_label": detected_label,
                "confidence": detected_confidence
            },
            "quality": quality
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/preview")
async def get_preview(
    camera_index: str = "0"
):
    """Get a preview frame from the microscope"""
    try:
        # Open selected camera if needed
        if not microscope_service.ensure_camera(camera_index):
            raise HTTPException(status_code=500, detail="Failed to open camera")
        
        # Get frame
        frame = microscope_service.get_frame()
        
        if frame is None:
            raise HTTPException(status_code=500, detail="Failed to capture frame")
        
        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            raise HTTPException(status_code=500, detail="Failed to encode frame")
        
        # Return as streaming response
        return StreamingResponse(
            iter([buffer.tobytes()]),
            media_type="image/jpeg"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/camera/{camera_index}/open")
async def open_camera(
    camera_index: str
):
    """Open a specific camera"""
    try:
        success = microscope_service.open_camera(camera_index)
        if success:
            return {
                "success": True,
                "camera_index": camera_index,
                "message": "Camera opened successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to open camera")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/camera/close")
async def close_camera():
    """Close the current camera"""
    try:
        microscope_service.close_camera()
        return {
            "success": True,
            "message": "Camera closed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
