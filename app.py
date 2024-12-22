from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import psutil
import pyautogui
import screen_brightness_control as sbc
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import socket
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
import os.path
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_gmail_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)

def send_startup_email():
    try:
        service = get_gmail_service()
        ip_address = get_local_ip()
        port = 3000

        message = MIMEMultipart()
        message["From"] = "botasuszen@gmail.com"
        message["To"] = "botasuszen@gmail.com"
        message["Subject"] = "Laptop Control Server Started"

        body = f"Server is running at: http://{ip_address}:{port}"
        message.attach(MIMEText(body, "plain"))

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

        service.users().messages().send(
            userId="me",
            body={"raw": raw}
        ).execute()

    except Exception as e:
        print(f"Failed to send email: {e}")

# Setup logging
if not os.path.exists('logs'):
    os.makedirs('logs')
file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Application startup')

# Command Execution Functions
def execute_command(command, value=None):
    try:
        if command == "system_info":
            cpu = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            battery = psutil.sensors_battery()

            return {
                "status": "success",
                "data": {
                    "cpu": round(cpu, 1),
                    "memory": round(memory.percent, 1),
                    "battery": round(battery.percent, 1) if battery else "N/A",
                    "memory_total": f"{memory.total / (1024**3):.1f}GB",
                    "memory_used": f"{memory.used / (1024**3):.1f}GB"
                }
            }

        # Media Controls
        elif command == "media_play":
            pyautogui.press('playpause')
            return "Media played/paused"
        elif command == "media_next":
            pyautogui.press('nexttrack')
            return "Next track"
        elif command == "media_prev":
            pyautogui.press('prevtrack')
            return "Previous track"

        # Screen Controls
        elif command == "brightness":
            sbc.set_brightness(int(value))
            return f"Brightness set to {value}%"

        # Existing commands...
        elif command == "shutdown":
            os.system("shutdown /s /t 1")  # Shut down immediately
            return "Shutting down..."
        elif command == "sleep":
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")  # Sleep
            return "Going to sleep..."
        elif command == "lock":
            os.system("rundll32.exe user32.dll,LockWorkStation")  # Lock Workstation
            return "Workstation locked."
        elif command == "restart":
            os.system("shutdown /r /t 1")  # Restart immediately
            return "Restarting..."
        elif command == "hibernate":
            os.system("shutdown /h")  # Hibernate
            return "Hibernating..."
        elif command == "logoff":
            os.system("shutdown /l")  # Log off
            return "Logging off..."
        else:
            return f"Unknown command: {command}"
    except Exception as e:
        app.logger.error(f"Error executing command '{command}': {e}", exc_info=True)
        return {"status": "error", "message": f"Error executing command: {e}"}

# Route to handle the command requests
@app.route('/command', methods=['GET'])
def command():
    cmd = request.args.get('cmd')
    value = request.args.get('value')
    if not cmd:
        app.logger.error('No command specified')
        return jsonify({"status": "error", "message": "No command specified"}), 400

    response = execute_command(cmd, value)
    if isinstance(response, str):
        app.logger.info(f'Command executed: {cmd}, Response: {response}')
        return jsonify({"status": "success", "message": response})
    else:
        app.logger.info(f'Command executed: {cmd}, Response: {response}')
        return jsonify(response)

# Serve the control page
@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        app.logger.error(f"Error rendering index.html: {e}", exc_info=True)
        return jsonify({"status": "error", "message": "Internal Server Error"}), 500

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"Unhandled Exception: {e}", exc_info=True)
    return jsonify({"status": "error", "message": "Internal Server Error"}), 500

if __name__ == '__main__':
    send_startup_email()
    print("Starting now")
    app.run(host='0.0.0.0', port=3000)  # Listen on all network interfaces
