import pyautogui
import pyperclip
import time

def send_whatsapp_message(contact_name, message):
    # 1. Open WhatsApp Desktop
    pyautogui.hotkey("win", "s")
    time.sleep(1)
    pyperclip.copy("WhatsApp")
    pyautogui.hotkey("ctrl", "v")
    pyautogui.press("enter")
    time.sleep(3)

    # 2. Search for contact
    pyautogui.hotkey("ctrl", "f")
    time.sleep(1)
    pyperclip.copy(contact_name)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(1)
    pyautogui.press("enter")   # ✅ first Enter selects
    time.sleep(1)
    pyautogui.press("enter")   # ✅ second Enter opens chat
    time.sleep(2)

    # 3. Click in the message box (adjust coordinates if needed)
    screen_width, screen_height = pyautogui.size()
    pyautogui.click(1629,1764)
  # bottom middle
    time.sleep(1)

    # 4. Type & send the message
    pyperclip.copy(message)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(1)
    pyautogui.press("enter")

    print(f"✅ Message sent to {contact_name}: {message}")


# Example usage
send_whatsapp_message("Maa", "Hi! This is an automated test message only through contact name successfully completed 🚀")





