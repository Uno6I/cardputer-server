import asyncio
from kasa import SmartPlug
from aiohttp import web
from gpiozero import AngularServo
from time import sleep

# --- SERVO SETUP ---
servo = AngularServo(13, min_angle=0, max_angle=180)  # change pin if needed
servo_state = False


async def toggle_servo():
    global servo_state

    if servo_state:
        servo.angle = 0
    else:
        servo.angle = 25

    servo_state = not servo_state
    print("🔧 Servo toggled")


async def toggle_plug(ip: str):
    """Toggle the plug at the given IP using SmartPlug."""
    try:
        plug = SmartPlug(ip)
        await plug.update()

        if plug.is_on:
            await plug.turn_off()
        else:
            await plug.turn_on()

        print(f"✅ Toggled {ip}")
        return True

    except Exception as e:
        print(f"⚠️ Error toggling {ip}: {e}")
        return False


async def handle_toggle(request):
    """HTTP handler to toggle plug OR servo."""
    ip = request.query.get("ip")

    if not ip:
        return web.json_response(
            {"status": "error", "message": "No IP provided"},
            status=400
        )

    print(f"Received toggle request for {ip}")

    # --- CHECK IF LETTERS ONLY ---
    if ip.isalpha():
        await toggle_servo()

        return web.json_response({
            "status": "success",
            "device": "servo",
            "message": "Servo toggled"
        })

    # --- OTHERWISE TOGGLE SMART PLUG ---
    success = await toggle_plug(ip)

    if success:
        return web.json_response({
            "status": "success",
            "ip": ip,
            "message": f"Plug {ip} toggled!"
        })
    else:
        return web.json_response({
            "status": "error",
            "ip": ip,
            "message": f"Failed to toggle {ip}"
        }, status=500)


async def init_app():
    app = web.Application()
    app.router.add_get("/toggle", handle_toggle)
    return app


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init_app())

    print("Server running on http://0.0.0.0:5000")
    web.run_app(app, host="0.0.0.0", port=5000)
