import pyautogui
import time

print("👉 Move your mouse to the WhatsApp message box within 5 seconds...")
time.sleep(5)  # gives you time to place the cursor
x, y = pyautogui.position()
print(f"✅ Mouse position captured: {x}, {y}")


