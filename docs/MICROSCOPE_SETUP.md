# Digital Microscope Setup Guide

This guide will help you set up and configure your digital microscope with Nomisma.

## Supported Microscopes

Nomisma is designed to work with USB digital microscopes that support the UVC (USB Video Class) protocol. The default recommended model is:

- **DM7-Z01C 4.3 inch Digital Microscope**

However, most USB microscopes should work, including:
- Jiusion Digital Microscope
- Plugable USB Digital Microscope
- AmScope Digital Microscope
- Any UVC-compatible USB camera/microscope

## Hardware Setup

### 1. Physical Connection

1. Connect the microscope to your computer via USB
2. On Linux, the device should appear as `/dev/video0` (or `/dev/video1`, `/dev/video2`, etc.)
3. Verify the connection:
   ```bash
   ls -l /dev/video*
   ```

### 2. Permissions (Linux)

If you encounter permission errors, add your user to the `video` group:

```bash
sudo usermod -a -G video $USER
```

Then log out and log back in for changes to take effect.

### 3. Test the Camera

Test if the camera works with:

```bash
# Install v4l-utils if not already installed
sudo apt-get install v4l-utils

# List video devices
v4l2-ctl --list-devices

# Test camera
ffplay /dev/video0
```

## Docker Configuration

Microscope access is enabled via the optional `docker-compose.microscope.yml` override file:

```yaml
services:
  backend:
    devices:
      - /dev/video0:/dev/video0
    privileged: true
```

Start with the override:

```bash
docker compose -f docker-compose.yml -f docker-compose.microscope.yml up -d
```

### Multiple Cameras

If you have multiple cameras or the microscope is not `/dev/video0`, update `docker-compose.microscope.yml`:

```yaml
services:
  backend:
    devices:
      - /dev/video1:/dev/video1  # Change to your device
```

## Application Setup

### 1. Start the Application

```bash
./start
```

### 2. Navigate to Scan Coin Page

Open http://localhost:3000/scan in your browser.

### 3. Select Camera

The application will automatically detect available cameras. Select your microscope from the dropdown.

### 4. Adjust Focus and Lighting

- Position the coin under the microscope
- Adjust the microscope's focus wheel for a clear image
- Ensure adequate lighting (most microscopes have built-in LED lights)

### 5. Capture Image

Click the "Capture Image" button to take a photo of the coin.

## Optimal Image Capture

For best AI analysis results:

### Lighting
- Use the microscope's built-in LED lights
- Ensure even lighting across the coin surface
- Avoid harsh shadows or glare

### Focus
- Adjust focus until details are sharp
- Capture the entire coin face in the frame
- Ensure text and design elements are clearly visible

### Positioning
- Center the coin in the frame
- Keep the coin flat and parallel to the lens
- Capture both obverse (front) and reverse (back) separately

### Resolution
- The application automatically sets the camera to maximum resolution
- Typical resolution: 1920x1080 or higher
- Higher resolution = better AI analysis

## Troubleshooting

### Camera Not Detected

**Problem:** No cameras appear in the dropdown

**Solutions:**
1. Check USB connection
2. Verify device appears in `/dev/video*`
3. Restart Docker containers:
   ```bash
   docker-compose restart backend
   ```
4. Check Docker logs:
   ```bash
   docker-compose logs backend
   ```

### Permission Denied

**Problem:** "Permission denied" error when accessing camera

**Solutions:**
1. Add user to video group (see above)
2. Check device permissions:
   ```bash
   ls -l /dev/video0
   ```
3. Ensure Docker has privileged access (set in `docker-compose.microscope.yml`)

### Poor Image Quality

**Problem:** Blurry or dark images

**Solutions:**
1. Clean the microscope lens
2. Adjust focus manually
3. Increase LED brightness
4. Ensure coin surface is clean
5. Try different camera settings in the application

### Camera Already in Use

**Problem:** "Camera is already in use" error

**Solutions:**
1. Close other applications using the camera
2. Restart the backend container:
   ```bash
   docker-compose restart backend
   ```

### Wrong Camera Selected

**Problem:** Laptop webcam selected instead of microscope

**Solutions:**
1. Use the camera dropdown to select the correct device
2. Disconnect other cameras if possible
3. Check camera index in the application

## Advanced Configuration

### Custom Resolution

To set a custom resolution, modify `backend/app/services/microscope.py`:

```python
def open_camera(self, camera_index: int = 0) -> bool:
    # ...
    self.current_camera.set(cv2.CAP_PROP_FRAME_WIDTH, 2592)  # Your width
    self.current_camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1944)  # Your height
```

### Frame Rate

Adjust FPS if needed:

```python
self.current_camera.set(cv2.CAP_PROP_FPS, 30)
```

### Camera Properties

List all available camera properties:

```bash
v4l2-ctl -d /dev/video0 --list-ctrls
```

## Recommended Workflow

1. **Setup**: Position microscope and coin
2. **Focus**: Adjust focus for clarity
3. **Light**: Ensure even, bright lighting
4. **Preview**: Use live preview to check framing
5. **Capture**: Take the photo
6. **Review**: Check image quality before proceeding
7. **Repeat**: Capture multiple angles if needed

## Tips for Best Results

- **Clean coins**: Gently clean coins before scanning (if appropriate for the coin type)
- **Stable surface**: Use a stable surface to avoid camera shake
- **Multiple images**: Capture obverse, reverse, and edge views
- **Detail shots**: Take close-ups of interesting features or defects
- **Consistent lighting**: Use the same lighting setup for all coins
- **Regular calibration**: Periodically check focus and alignment

## Support

If you continue to experience issues:

1. Check the main [README.md](../README.md) troubleshooting section
2. Review Docker logs: `docker-compose logs backend`
3. Test camera outside Docker: `ffplay /dev/video0`
4. Verify OpenCV installation: `docker-compose exec backend python -c "import cv2; print(cv2.__version__)"`

For hardware-specific issues, consult your microscope's manual or manufacturer support.
