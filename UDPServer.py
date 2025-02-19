import asyncio
import socket
from datetime import datetime, timedelta

UDP_PORT = 12345  # Server UDP port
udp_clients = {}  # Store HoloLens clients { (ip, port): last_seen_time }

# Create UDP socket
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(("0.0.0.0", UDP_PORT))
server.setblocking(False)  # Set socket to non-blocking

print(f"✅ UDP Server listening on port {UDP_PORT}...")

async def udp_heartbeat_checker():
    """Check every 15 seconds if UDP clients are alive."""
    while True:
        now = datetime.now()
        print(now)
        disconnected = []

        for addr, last_ping in list(udp_clients.items()):
            if now - last_ping > timedelta(seconds=15):  # 15 sec timeout
                print(f"⚠️ UDP Client {addr} timed out.")
                disconnected.append(addr)

        for addr in disconnected:
            del udp_clients[addr]

        await asyncio.sleep(15)

async def send_udp_message(message, addr):
    """Send UDP message to specified address."""
    server.sendto(message.encode(), addr)
    print(f"📤 Sent to {addr}: {message}")

async def handle_udp():
    """Handle UDP messages."""
    loop = asyncio.get_running_loop()
    while True:
        # Use the loop's asynchronous sock_recvfrom to avoid blocking
        data, addr = await loop.sock_recvfrom(server, 1024)
        message = data.decode().strip()
        print(f"📩 Received from {addr}: {message}")
        if message == "Hello Server":
            # Record (or update) client information
            udp_clients[addr] = datetime.now()
            print(f"Updated last_ping for {addr}: {udp_clients[addr]}")
            await send_udp_message("Hello from server!", addr)
        if message == "ping":
            udp_clients[addr] = datetime.now()
            print(f"Updated last_ping for {addr}: {udp_clients[addr]}")
            await send_udp_message("pong", addr)

        if udp_clients:
            for client_addr in udp_clients.keys():
                await send_udp_message("Hello HoloLens!", client_addr)

async def start():
    """Start the UDP server."""
    asyncio.create_task(udp_heartbeat_checker())  # Start heartbeat checker
    await handle_udp()

if __name__ == "__main__":
    asyncio.run(start())
