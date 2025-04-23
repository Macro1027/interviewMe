# websocket_server.py (Example server)
import asyncio
import websockets
import logging
import os
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Directory to save audio files
AUDIO_DIR = "received_audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

async def audio_handler(websocket, path):
    client_addr = websocket.remote_address
    client_id = f"{client_addr[0]}_{client_addr[1]}"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3] # YYYYMMDD_HHMMSS_ms
    output_filename = os.path.join(AUDIO_DIR, f"audio_{client_id}_{timestamp}.mp3")

    logging.info(f"Client {client_id} connected.")
    logging.info(f"Will save audio to: {output_filename}")

    try:
        chunk_count = 0
        # Open the file in binary write mode
        with open(output_filename, "wb") as f:
             async for message in websocket:
                if isinstance(message, bytes):
                    f.write(message)
                    chunk_count += 1
                    # logging.debug(f"Received chunk {chunk_count} ({len(message)} bytes) from {client_id}")
                else:
                    logging.warning(f"Received non-binary message from {client_id}: {message}")
        logging.info(f"Finished receiving {chunk_count} chunks from {client_id}. Saved to {output_filename}")

    except websockets.exceptions.ConnectionClosedOK:
        logging.info(f"Client {client_id} disconnected normally.")
    except websockets.exceptions.ConnectionClosedError as e:
        logging.error(f"Client {client_id} disconnected with error: {e}")
    except Exception as e:
        logging.exception(f"Error handling client {client_id}: {e}")
        # Clean up partially saved file on error?
        # if os.path.exists(output_filename):
        #     try:
        #         os.remove(output_filename)
        #         logging.info(f"Removed partially saved file: {output_filename}")
        #     except OSError as remove_err:
        #         logging.error(f"Error removing partial file {output_filename}: {remove_err}")

async def main():
    host = "localhost"
    port = 8765 # Default WebSocket port
    async with websockets.serve(audio_handler, host, port):
        logging.info(f"WebSocket server started on ws://{host}:{port}")
        logging.info(f"Saving received audio files to ./{AUDIO_DIR}/")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("WebSocket server stopped.")
    except Exception as e:
        logging.exception("WebSocket server failed to start:") 