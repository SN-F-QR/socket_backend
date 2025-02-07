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

async def send_message(message):

    while True:
        if connected_devices:
            # 遍历所有已连接的客户端发送消息
            for ws in connected_devices.copy():
                try:
                    await ws.send(message)
                    print(f"已发送给 {ws.remote_address}: {message}")
                except websockets.exceptions.ConnectionClosed:
                    print(f"发送失败，设备已断开: {ws.remote_address}")
        else:
            print("当前没有连接的设备。")

async def main():
    server = await websockets.serve(handler, "0.0.0.0", 12345)
    print("WebSocket server running on ws://0.0.0.0:12345")
    await server.wait_closed()

asyncio.run(main())

