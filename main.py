import asyncio
import logging
import json

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

logging.basicConfig(filename='error.log', level=logging.ERROR)

app.mount("/static", StaticFiles(directory="./static"), name="static")

def get_stock_prices():
    symbols = ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA", "GOOG", "FB", "NVDA", "BA", "NFLX"]
    stock_data = {}

    for symbol in symbols:
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period="1d")
            last_price = round(data["Close"].iloc[-1], 2)
            history = [round(price, 2) for price in data["Close"].tolist()]
            stock_data[symbol] = {
                "symbol": symbol,
                "price": last_price,
                "history": history,
            }
        except Exception as e:
            logging.error(f"Error fetching data for {symbol}: {e}")
                