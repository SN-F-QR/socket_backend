import websockets
import asyncio
import pandas as pd
import json


async def connect(message):
    async with websockets.connect("ws://localhost:12345") as ws:
        await ws.send(message)
        async for message in ws:
            print(f"Received: {message}")


if __name__ == "__main__":
    test_case = pd.read_csv("test_case.csv", index_col=0)
    case = test_case.loc["restaurant", "content"]
    print(case)

    asyncio.run(
        connect(json.dumps({"type": "open", "value": "https://www.bilibili.com/"}))
    )
