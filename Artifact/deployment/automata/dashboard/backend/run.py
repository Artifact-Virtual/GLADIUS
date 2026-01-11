import os
import sys

# Ensure the project root is on sys.path so the `automata` package can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from automata.dashboard.backend.app import app, socketio

if __name__ == '__main__':
    # For local development and testing we allow Werkzeug. In production use a real WSGI server.
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
