# kasa_server_any_ip.py
import asyncio
from kasa import IotPlug
from aiohttp import web

async def toggle_plug(ip: str):
    """Toggle the plug at the given IP."""
    try:
        plug = IotPlug(ip)
        await plug.update()  # fetch device info
        await plug.toggle()   # toggle on/off
        print(f"✅ Toggled {ip}")
        return True
    except Exception as e:
        print(f"⚠️ Error toggling {ip}: {e}")
        return False

async def handle_toggle(request):
    """HTTP handler to toggle a plug."""
    ip = request.query.get("ip")
    if not ip:
        return web.json_response({"status": "error", "message": "No IP provided"}, status=400)

    print(f"🌀 Received toggle request for {ip}")
    success = await toggle_plug(ip)

    if success:
        feedback = f"Plug {ip} toggled!"
        print(feedback)
        return web.json_response({"status": "success", "ip": ip, "message": feedback})
    else:
        feedback = f"Failed to toggle {ip}"
        print(feedback)
        return web.json_response({"status": "error", "ip": ip, "message": feedback}, status=500)

async def init_app():
    app = web.Application()
    app.router.add_get("/toggle", handle_toggle)
    return app

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init_app())
    print("Server running on http://0.0.0.0:5000")
    web.run_app(app, host="0.0.0.0", port=5000)
