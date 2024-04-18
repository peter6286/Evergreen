from picamera import PiCamera
from time import sleep
import datetime

def capture_image():
    camera = PiCamera()
    try:
        # Start the camera preview
        camera.start_preview()
        # Camera warm-up time
        sleep(2)
        # Generate timestamped filename
        filename = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S.jpg")
        # Capture the image to a file
        camera.capture('/home/pi/images/' + filename)
        print(f"Image captured: {filename}")
        return '/home/pi/images/' + filename
    finally:
        # Stop the camera preview
        camera.stop_preview()
        # Release the camera resources
        camera.close()
