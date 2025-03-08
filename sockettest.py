import asyncio
import websockets
import webbrowser
import re
import json

from dotenv import load_dotenv
from asyncio import create_task
from utility import save_note

connected_devices = set()
# ws_loop = None  # 全局变量，用于保存后台线程的事件循环
video_callback = None  # handle time change
rec_callback = None  # call normal recommender
serp_callback = None  # call serp api
serper_callback = None  # call serper api
# action_callback = None  # handle action


async def handler(websocket):
    connected_devices.add(websocket)
    print(
        f"Device connected from {websocket.remote_address}, Total: {len(connected_devices)}"
    )
    try:
        websocket.ping_interval = 20  # Seconds between pings
        websocket.ping_timeout = 15  # Seconds to wait for pong response
        async for message in websocket:
            print(f"Received: {message}")
            data = json.loads(message)
            message_id = data["id"] if "id" in data else "no_id"
            if "id" in data:
                await websocket.send(
                    json.dumps({"id": message_id, "type": "echo", "value": message})
                )
            else:
                await websocket.send(json.dumps({"echo": message}))

            # TODO: set the proper format for links
            if data["type"] == "open":
                webbrowser.open_new_tab(data["value"]) if data["value"] else None
            elif data["type"] == "video":
                result = await video_callback(data["value"])
                result["id"] = message_id
                create_task(send_message_once(json.dumps(result)))
            elif data["type"] == "recommend":
                tasks = [
                    rec_callback(data["value"]),
                    serp_callback(data["value"]),
                    serper_callback(data["value"]),
                ]
                for future in asyncio.as_completed(tasks):
                    result = await future
                    result["id"] = message_id
                    create_task(send_message_once(json.dumps(result)))
            elif data["type"] == "save":
                save_note(data["value"])

    except websockets.exceptions.ConnectionClosed:
        print(f"Device disconnected: {websocket.remote_address}")
    finally:
        connected_devices.remove(websocket)
        print(f"Remaining Devices: {len(connected_devices)}")


async def send_message_once(message, type=None, target=""):
    """
    Broadcast a message to all connected devices
    type: type of message
    target: target for defined objects
    """
    print("send_message_once() called")  # 新增调试打印
    format_message = (
        json.dumps({"type": type, "target": target, "value": message})
        if type
        else message
    )

    if connected_devices:
        disconnected = set()
        for ws in connected_devices.copy():
            try:
                await ws.send(format_message)
                print(f"Successfully sent to {ws.remote_address}: {format_message}")
            except websockets.exceptions.ConnectionClosed:
                print(f"Connection lost, device disconnected: {ws.remote_address}")
                disconnected.add(ws)
            except Exception as e:
                print(f"Error sending to {ws.remote_address}: {e}")
                disconnected.add(ws)

        for ws in disconnected:
            if ws in connected_devices:
                connected_devices.remove(ws)
    else:
        print("No connected devices.")


async def periodic_sender():
    while True:
        await send_message_once("Hello from server")
        await asyncio.sleep(10)  # 每 10 秒尝试发送一次


async def heartbeat():
    while True:
        if connected_devices:
            disconnected = set()
            for ws in connected_devices.copy():
                try:
                    # Send a ping message
                    pong_waiter = await ws.ping()
                    await asyncio.wait_for(
                        pong_waiter, timeout=5
                    )  # Wait for a pong within 5 seconds
                    print(f"Ping successful to {ws.remote_address}")
                except asyncio.TimeoutError:
                    print(f"No pong received, device disconnected: {ws.remote_address}")
                    disconnected.add(ws)
                except websockets.exceptions.ConnectionClosed:
                    print(
                        f"Connection closed, device disconnected: {ws.remote_address}"
                    )
                    disconnected.add(ws)
                except Exception as e:
                    print(f"Error during heartbeat with {ws.remote_address}: {e}")
                    disconnected.add(ws)

            # Remove disconnected devices
            for ws in disconnected:
                if ws in connected_devices:
                    connected_devices.remove(ws)

        await asyncio.sleep(10)  # Send heartbeat every 10 seconds


async def start():
    load_dotenv("key.env")
    while True:  # Continuous server operation
        try:
            server = await websockets.serve(
                handler,
                "0.0.0.0",
                12345,
                ping_interval=20,
                ping_timeout=15,
                close_timeout=10,
            )
            print("WebSocket server running on ws://0.0.0.0:12345")
            asyncio.create_task(heartbeat())
            # asyncio.create_task(periodic_sender())
            await server.wait_closed()
        except Exception as e:
            print(f"Server error: {e}")
            await asyncio.sleep(5)


# def run_ws_server():
#     global ws_loop
#     ws_loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(ws_loop)
#     ws_loop.create_task(start())
#     ws_loop.run_forever()
if __name__ == "__main__":
    asyncio.run(start())
