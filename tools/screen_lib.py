from PIL import ImageGrab, Image
from io import BytesIO
import base64

def capture_screenshot():
    print("Creating screenshot...")
    screenshot = ImageGrab.grab()
    screenshot = screenshot.resize((screenshot.width // 2, screenshot.height // 2), Image.LANCZOS)
    buffered = BytesIO()
    screenshot.save(buffered, format="PNG")
    screenshot_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    print("Screenshot successfully created and converted to base64.")
    return screenshot_b64
