import asyncio
import socket
from datetime import datetime, timedelta

UDP_PORT = 12345  # 服务器监听的 UDP 端口
udp_clients = {}  # 存储 HoloLens 客户端 { (ip, port): last_seen_time }

# 创建 UDP 套接字
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(("0.0.0.0", UDP_PORT))  # 监听所有 IP 地址

print(f"✅ UDP Server listening on port {UDP_PORT}...")

async def udp_heartbeat_checker():
    """每 15 秒检查 UDP 客户端是否存活"""
    while True:
        now = datetime.now()
        disconnected = []

        for addr, last_ping in list(udp_clients.items()):
            if now - last_ping > timedelta(seconds=15):  # 超过 15 秒无响应
                print(f"⚠️ UDP Client {addr} timed out.")
                disconnected.append(addr)

        for addr in disconnected:
            del udp_clients[addr]

        await asyncio.sleep(15)

async def send_udp_message(message, addr):
    """发送 UDP 消息到指定地址"""
    server.sendto(message.encode(), addr)
    print(f"📤 Sent to {addr}: {message}")

async def handle_udp():
    """处理 UDP 消息"""
    while True:
        data, addr = server.recvfrom(1024)
        message = data.decode().strip()
        print(f"📩 Received from {addr}: {message}")

        # 如果是 ping，则记录 HoloLens 地址
        if message == "ping":
            udp_clients[addr] = datetime.now()
            await send_udp_message("pong", addr)  # 发送响应

        # 如果服务器要主动给 HoloLens 发送消息
        if udp_clients:
            for client_addr in udp_clients.keys():
                await send_udp_message("Hello HoloLens!", client_addr)

async def start():
    """启动 UDP 服务器"""
    asyncio.create_task(udp_heartbeat_checker())  # UDP 设备心跳检测
    await handle_udp()

if __name__ == "__main__":
    asyncio.run(start())