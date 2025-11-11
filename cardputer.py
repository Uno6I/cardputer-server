import asyncio
import os
os.environ['TZ'] = 'America/Los_Angeles'  # replace with your timezone
import time
time.tzset()  # Apply the timezone
from kasa import SmartPlug

SERVER_IP = "0.0.0.0"
SERVER_PORT = 5000

PLUGS = {}  # Cache SmartPlug objects

async def toggle_plug(ip):
    try:
        if ip not in PLUGS:
            PLUGS[ip] = SmartPlug(ip)
        plug = PLUGS[ip]
        await plug.update()  # Must await
        if plug.is_on:
            await plug.turn_off()
        else:
            await plug.turn_on()
        print(f"Toggled {ip}")
    except Exception as e:
        print(f"Error toggling {ip}: {e}")

async def handle_client(reader, writer):
    try:
        data = await reader.readline()
        plug_ip = data.decode().strip()
        print(f"Received toggle request for {plug_ip}")
        await toggle_plug(plug_ip)
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        writer.close()
        await writer.wait_closed()

async def main():
    server = await asyncio.start_server(handle_client, SERVER_IP, SERVER_PORT)
    print(f"Server listening on {SERVER_IP}:{SERVER_PORT}")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())

