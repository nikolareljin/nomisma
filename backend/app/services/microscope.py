import cv2
import os
import glob
from typing import List, Optional, Tuple, Union
from datetime import datetime
import numpy as np

class MicroscopeService:
    """Service for interacting with digital microscope via OpenCV"""
    
    def __init__(self):
        self.current_camera = None
        self.camera_index: Union[int, str] = 0

    def _select_backend(self) -> int:
        if os.name == "posix" and hasattr(cv2, "CAP_V4L2"):
            return cv2.CAP_V4L2
        return cv2.CAP_ANY

    def _normalize_camera_index(self, camera_index: Union[int, str]) -> Tuple[str, Union[int, str]]:
        if isinstance(camera_index, int):
            return ("index", camera_index)
        if isinstance(camera_index, str) and camera_index.isdigit():
            return ("index", int(camera_index))
        return ("path", str(camera_index))

    def _camera_matches(self, camera_index: Union[int, str]) -> bool:
        return self._normalize_camera_index(self.camera_index) == self._normalize_camera_index(camera_index)

    def _open_capture(self, camera_index: Union[int, str]) -> Optional[cv2.VideoCapture]:
        backend = self._select_backend()
        candidates: List[Union[int, str]] = []
        if isinstance(camera_index, str):
            if camera_index:
                candidates.append(camera_index)
            if camera_index.isdigit():
                candidates.append(int(camera_index))
        else:
            candidates.append(camera_index)

        for target in candidates:
            cap = cv2.VideoCapture(target, backend)
            if cap.isOpened():
                return cap
            cap.release()

        if backend != cv2.CAP_ANY:
            for target in candidates:
                cap = cv2.VideoCapture(target, cv2.CAP_ANY)
                if cap.isOpened():
                    return cap
                cap.release()

        return None

    def _configure_camera(self, cap: cv2.VideoCapture) -> None:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        if hasattr(cv2, "CAP_PROP_FOURCC"):
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        if hasattr(cv2, "CAP_PROP_BUFFERSIZE"):
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    def _read_frame(self) -> Optional[np.ndarray]:
        if self.current_camera is None or not self.current_camera.isOpened():
            return None
        frame = None
        for _ in range(5):
            ret, frame = self.current_camera.read()
            if ret:
                return frame
        return None

    def _read_frame_from(self, cap: cv2.VideoCapture) -> Optional[np.ndarray]:
        frame = None
        for _ in range(5):
            ret, frame = cap.read()
            if ret:
                return frame
        return None

    def _probe_device(self, device_path: Union[int, str]) -> Tuple[bool, Optional[int], Optional[int], Optional[int]]:
        cap = self._open_capture(device_path)
        if not cap or not cap.isOpened():
            if cap:
                cap.release()
            return False, None, None, None
        self._configure_camera(cap)
        frame = self._read_frame_from(cap)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        cap.release()
        return frame is not None, width, height, fps
        
    def list_available_cameras(self) -> List[dict]:
        """List all available camera devices"""
        cameras = []
        # Prefer Linux device nodes when available.
        linux_devices = sorted(glob.glob("/dev/video*"))
        linux_media_devices = sorted(glob.glob("/dev/media*"))
        if linux_devices:
            for device_path in linux_devices:
                device_name = os.path.basename(device_path)
                index = int(device_name.replace("video", "")) if device_name.startswith("video") else None
                label = f"Camera {index}" if index is not None else device_name

                sys_name_path = f"/sys/class/video4linux/{device_name}/name"
                if os.path.exists(sys_name_path):
                    try:
                        with open(sys_name_path, "r", encoding="utf-8") as handle:
                            sys_label = handle.read().strip()
                            if sys_label:
                                label = sys_label
                    except OSError:
                        pass

                available, width, height, fps = self._probe_device(device_path)

                cameras.append({
                    "index": index if index is not None else device_path,
                    "name": label,
                    "resolution": f"{width}x{height}" if width and height else "unknown",
                    "fps": fps or 0,
                    "device": device_path,
                    "available": available,
                })
            for media_path in linux_media_devices:
                media_name = os.path.basename(media_path)
                label = f"Media {media_name}"
                linked_nodes = self._linked_video_nodes(media_path)
                linked_video = None
                available = False
                width = height = fps = None
                for node in linked_nodes:
                    ok, node_w, node_h, node_fps = self._probe_device(node)
                    if ok:
                        linked_video = node
                        available = True
                        width, height, fps = node_w, node_h, node_fps
                        break
                cameras.append({
                    "index": media_path,
                    "name": label,
                    "resolution": f"{width}x{height}" if width and height else "unknown",
                    "fps": fps or 0,
                    "device": media_path,
                    "linked_video": linked_video,
                    "linked_video_nodes": linked_nodes,
                    "available": available,
                })
        else:
            # Fallback: check first 10 indexes for non-Linux environments.
            for i in range(10):
                ok, width, height, fps = self._probe_device(i)
                if ok:
                    cameras.append({
                        "index": i,
                        "name": f"Camera {i}",
                        "resolution": f"{width}x{height}",
                        "fps": fps,
                        "device": f"index:{i}",
                        "available": True,
                    })
        
        return cameras
    
    def open_camera(self, camera_index: Union[int, str] = 0) -> bool:
        """Open a specific camera device"""
        if self.current_camera is not None:
            self.current_camera.release()

        targets: List[Union[int, str]] = []
        if isinstance(camera_index, str):
            if camera_index.startswith("/dev/media"):
                targets = self._linked_video_nodes(camera_index)
                if not targets:
                    targets = [camera_index]
            elif camera_index.startswith("/dev/video"):
                targets = [camera_index]
                media_path = self._media_for_video(camera_index)
                if media_path:
                    for node in self._linked_video_nodes(media_path):
                        if node not in targets:
                            targets.append(node)
            else:
                targets = [camera_index]
        else:
            targets = [camera_index]

        for target in targets:
            cap = self._open_capture(target)
            if not cap or not cap.isOpened():
                if cap:
                    cap.release()
                continue
            self._configure_camera(cap)
            if self._read_frame_from(cap) is not None:
                self.current_camera = cap
                self.camera_index = camera_index
                return True
            cap.release()

        self.current_camera = None
        return False

    def ensure_camera(self, camera_index: Union[int, str] = 0) -> bool:
        """Ensure the requested camera is open and active."""
        if (
            self.current_camera is None
            or not self.current_camera.isOpened()
            or not self._camera_matches(camera_index)
        ):
            return self.open_camera(camera_index)
        return True

    def _resolve_media_device(self, media_path: str) -> Optional[str]:
        for node in self._linked_video_nodes(media_path):
            return node
        return None

    def _linked_video_nodes(self, media_path: str) -> List[str]:
        media_name = os.path.basename(media_path)
        media_device_path = os.path.join("/sys/class/media", media_name, "device")
        if not os.path.exists(media_device_path):
            return []
        media_real = os.path.realpath(media_device_path)
        nodes = []
        for video_device in sorted(glob.glob("/sys/class/video4linux/video*")):
            video_real = os.path.realpath(os.path.join(video_device, "device"))
            if not media_real or not video_real:
                continue
            if media_real == video_real or video_real.startswith(media_real) or media_real.startswith(video_real):
                nodes.append(os.path.join("/dev", os.path.basename(video_device)))
        return nodes

    def _media_for_video(self, video_path: str) -> Optional[str]:
        video_name = os.path.basename(video_path)
        video_device_path = os.path.join("/sys/class/video4linux", video_name, "device")
        if not os.path.exists(video_device_path):
            return None
        video_real = os.path.realpath(video_device_path)
        for media_device in sorted(glob.glob("/sys/class/media/media*")):
            media_real = os.path.realpath(os.path.join(media_device, "device"))
            if not media_real or not video_real:
                continue
            if media_real == video_real or video_real.startswith(media_real) or media_real.startswith(video_real):
                return os.path.join("/dev", os.path.basename(media_device))
        return None
    
    def capture_image(self, save_path: str) -> Tuple[bool, Optional[str]]:
        """Capture an image from the microscope"""
        if self.current_camera is None or not self.current_camera.isOpened():
            if not self.open_camera(self.camera_index):
                return False, "Failed to open camera"
        
        # Capture frame
        frame = self._read_frame()
        if frame is None:
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
        
        return self._read_frame()
    
    def close_camera(self):
        """Release the camera"""
        if self.current_camera is not None:
            self.current_camera.release()
            self.current_camera = None

# Global instance
microscope_service = MicroscopeService()
