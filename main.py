import os, json, asyncio, websockets
from telegram import Bot

DERIV_TOKEN = os.getenv("DERIV_TOKEN")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SYMBOL = os.getenv("SYMBOL", "R_100")
STAKE = float(os.getenv("STAKE", "1"))
TARGET_DIGIT = os.getenv("TARGET_DIGIT", "2")

async def run():
    bot = Bot(token=BOT_TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text="✅ Bot LIVE - Digit Sniper Started")
    async with websockets.connect("wss://ws.binaryws.com/websockets/v3?app_id=1089") as ws:
        await ws.send(json.dumps({"authorize": DERIV_TOKEN}))
        await ws.recv()
        await ws.send(json.dumps({"ticks": SYMBOL}))
        async for msg in ws:
            data = json.loads(msg)
            if "tick" in data:
                price = str(data["tick"]["quote"])
                last_digit = price[-1]
                if last_digit == TARGET_DIGIT:
                    await ws.send(json.dumps({
                        "buy": 1,
                        "price": STAKE,
                        "parameters": {
                            "amount": STAKE,
                            "basis": "stake",
                            "contract_type": "DIGITOVER",
                            "currency": "USD",
                            "duration": 1,
                            "duration_unit": "t",
                            "symbol": SYMBOL,
                            "barrier": TARGET_DIGIT
                        }
                    }))
                    await bot.send_message(chat_id=CHAT_ID, text=f"🎯 TRADE: {SYMBOL} Price {price} Digit {last_digit}")

asyncio.run(run())
