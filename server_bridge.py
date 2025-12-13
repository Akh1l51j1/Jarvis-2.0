import logging
import threading
from flask import Flask
from flask_socketio import SocketIO

# 1. Silence the noisy server logs
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

# 2. THE CRITICAL BRIDGE SETUP
# async_mode='threading' prevents the "Greenlet" crash you had earlier.
# cors_allowed_origins="*" lets the UI connect from ANY folder.
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

class UIBridge:
    def start(self):
        # Starts the "Radio Station" on Port 5000
        thread = threading.Thread(target=lambda: socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True))
        thread.daemon = True
        thread.start()
        print(">> [Bridge] UI Server Online (Port 5000)")

    def update_status(self, status, message):
        try:
            socketio.emit('ui_update', {'status': status, 'message': message})
        except: pass

    def log(self, text):
        try:
            socketio.emit('terminal_log', {'log': text})
        except: pass

# Create the global instance that main.py will use
bridge = UIBridge()