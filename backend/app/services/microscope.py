import cv2
import os
from typing import List, Optional, Tuple
from datetime import datetime
import numpy as np

class MicroscopeService:
    """Service for interacting with digital microscope via OpenCV"""
    
    def __init__(self):
        self.current_camera = None
        self.camera_index = 0
        
    def list_available_cameras(self) -> List[dict]:
        """List all available camera devices"""
        cameras = []
        # Check first 5 video devices
        for i in range(5):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                # Get camera properties
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = int(cap.get(cv2.CAP_PROP_FPS))
                
                cameras.append({
                    "index": i,
                    "name": f"Camera {i}",
                    "resolution": f"{width}x{height}",
                    "fps": fps,
                    "device": f"/dev/video{i}"
                })
                cap.release()
        
        return cameras
    
    def open_camera(self, camera_index: int = 0) -> bool:
        """Open a specific camera device"""
        if self.current_camera is not None:
            self.current_camera.release()
        
        self.current_camera = cv2.VideoCapture(camera_index)
        self.camera_index = camera_index
        
        if self.current_camera.isOpened():
            # Set high resolution for microscope
            self.current_camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            self.current_camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            return True
        return False
    
    def capture_image(self, save_path: str) -> Tuple[bool, Optional[str]]:
        """Capture an image from the microscope"""
        if self.current_camera is None or not self.current_camera.isOpened():
            if not self.open_camera(self.camera_index):
                return False, "Failed to open camera"
        
        # Capture frame
        ret, frame = self.current_camera.read()
        
        if not ret:
            return False, "Failed to capture image"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Save image
        success = cv2.imwrite(save_path, frame)
        
        if success:
            return True, save_path
        else:
            return False, "Failed to save image"
    
    def get_frame(self) -> Optional[np.ndarray]:
        """Get a single frame for preview"""
        if self.current_camera is None or not self.current_camera.isOpened():
            if not self.open_camera(self.camera_index):
                return None
        
        ret, frame = self.current_camera.read()
        if ret:
            return frame
        return None
    
    def close_camera(self):
        """Release the camera"""
        if self.current_camera is not None:
            self.current_camera.release()
            self.current_camera = None

# Global instance
microscope_service = MicroscopeService()
