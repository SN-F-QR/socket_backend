import asyncio
import websockets
import webbrowser

connected_devices = set()

async def handler(websocket):
    connected_devices.add(websocket)
    print(f"Device connected from {websocket.remote_address}, Total: {len(connected_devices)}")

    try:
        async for message in websocket:
            print(f"Received: {message}")
            await websocket.send(f"Echo: {message}")
            webbrowser.open_new_tab(message)
    except websockets.exceptions.ConnectionClosed:
        print(f"Device disconnected: {websocket.remote_address}")
    finally:
        connected_devices.remove(websocket)
        print(f"Remaining Devices: {len(connected_devices)}")

async def main():
    server = await websockets.serve(handler, "0.0.0.0", 12345)
    print("WebSocket server running on ws://0.0.0.0:12345")
    await server.wait_closed()

asyncio.run(main())

