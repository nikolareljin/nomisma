from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import cv2
import os
from datetime import datetime
from uuid import uuid4

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
    image_type: str = "scan"
):
    """Capture an image from the microscope"""
    try:
        # Generate unique filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"capture_{timestamp}_{uuid4().hex[:8]}.jpg"
        
        # Create temp directory
        temp_dir = os.path.join(IMAGES_PATH, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        save_path = os.path.join(temp_dir, filename)
        
        # Open camera if needed
        if not microscope_service.current_camera or not microscope_service.current_camera.isOpened():
            if not microscope_service.open_camera(camera_index):
                raise HTTPException(status_code=500, detail="Failed to open camera")
        
        # Capture image
        success, result = microscope_service.capture_image(save_path)
        
        if not success:
            raise HTTPException(status_code=500, detail=result)
        
        return {
            "success": True,
            "file_path": f"temp/{filename}",
            "url": f"/images/temp/{filename}",
            "timestamp": timestamp
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/preview")
async def get_preview(
    camera_index: str = "0"
):
    """Get a preview frame from the microscope"""
    try:
        # Open camera if needed
        if not microscope_service.current_camera or not microscope_service.current_camera.isOpened():
            if not microscope_service.open_camera(camera_index):
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
