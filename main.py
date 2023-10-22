import asyncio
import websockets
import json


async def main():
    async with websockets.connect("wss://test.deribit.com/ws/api/v2") as websocket:
        msg = {
            "method": "public/get_instruments",
            "params": {"currency": "BTC", "kind": "option"},
            "jsonrpc": "2.0",
            "id": 1,
        }
        await websocket.send(json.dumps(msg))
        response = await websocket.recv()
        response = json.loads(response)
        try:
            tickers = [
                t["instrument_name"]
                for t in response["result"]
                if t["instrument_name"].endswith("C")
            ]
        except KeyError as k:
            print(k)
            tickers = []
        channels = [f"ticker.{t}.100ms" for t in tickers]
        msg = {
            "jsonrpc": "2.0",
            "method": "public/subscribe",
            "id": 42,
            "params": {"channels": channels},
        }
        await websocket.send(json.dumps(msg))
        while websocket.open:
            response = await websocket.recv()
            response = json.loads(response)
            try:
                data = response["params"]["data"]
                print(
                    f"ticker: {data['instrument_name']}, "
                    f"last_price: {data['last_price']}, "
                    f"greeks: {data['greeks']}"
                )
            except KeyError as k:
                print(k)


if __name__ == "__main__":
    asyncio.run(main())
