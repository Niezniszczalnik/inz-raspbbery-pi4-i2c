#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: WebSocket client receiving JSON data from a sensor on Raspberry Pi.
"""
import websocket
import json
import time
import logging

# Basic logging configuration – INFO level, with timestamps
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# WebSocket server URL (local Raspberry Pi)
WS_SERVER_URL = "ws://192.168.100.234:8765"
# WS_SERVER_URL = "ws://localhost:8765"  # Alternative if server listens on localhost

def on_message(ws, message):
    """Callback triggered when a message is received from the server."""
    try:
        data = json.loads(message)
        logging.info(f"Received JSON data: {json.dumps(data)}")
    except json.JSONDecodeError:
        logging.info(f"Received message: {message}")

def on_error(ws, error):
    """Callback triggered when an error occurs during communication."""
    logging.error(f"Connection error: {error}")

def on_close(ws, close_status_code, close_msg):
    """Callback triggered when the connection is closed."""
    logging.warning(f"Connection closed (code: {close_status_code}, message: {close_msg})")

def on_open(ws):
    """Callback triggered upon successfully establishing a connection."""
    logging.info("Connected to WebSocket server.")

if __name__ == "__main__":
    logging.info(f"Starting client and connecting to {WS_SERVER_URL}...")
    while True:
        try:
            ws_app = websocket.WebSocketApp(WS_SERVER_URL,
                                            on_open=on_open,
                                            on_message=on_message,
                                            on_error=on_error,
                                            on_close=on_close)
            ws_app.run_forever()  # Blocks until the connection is disrupted
        except KeyboardInterrupt:
            logging.info("WebSocket client interrupted by user.")
            break
        except Exception as e:
            logging.exception(f"Unexpected client error: {e}")
        logging.info("Reconnecting in 5 seconds...")
        time.sleep(5)
    logging.info("WebSocket client terminated.")
