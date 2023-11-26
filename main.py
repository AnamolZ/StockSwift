import asyncio
import logging
import json
import yfinance as yf

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from random import randint

app = FastAPI()

# Configure Cross-Origin Resource Sharing (CORS) middleware to handle web security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Configure logging to record errors in a designated file
logging.basicConfig(filename='error.log', level=logging.ERROR)

# Mount the '/static' directory for serving static files
app.mount("/static", StaticFiles(directory="./static"), name="static")

def get_stock_prices():
    symbols = ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA", "GOOG", "FB", "NVDA", "BA", "NFLX"]
    stock_data = {}
    for symbol in symbols:
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period="1d")
            last_price = round(data["Close"].iloc[-1], 2)
            # last_price = min(round(data["Close"].iloc[-1], 2) * randint(1, 3) -152, 400) #For Demo Purpose
            stock_data[symbol] = {
                "symbol": symbol,
                "price": last_price,
            }
        except Exception as e:
            logging.error(f"Error fetching data for {symbol}: {e}")
    print(stock_data)
    return stock_data

@app.get("/", response_class=HTMLResponse)
async def read_root():
    index_path = "./static/index.html"
    with open(index_path, "r", encoding="utf-8") as file:
        content = file.read()
    return HTMLResponse(content)

@app.get("/data")
async def read_root():
    stock_prices = get_stock_prices()
    return {
        "message": "Welcome to the Stock Data API",
        "stock_data": stock_prices
    }

# Route for favicon (!NOT NECESSARY)
@app.get("/favicon.ico")
async def get_favicon():
    return {"message": "No favicon here"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()
        last_stock_prices = None
        async def send_stock_prices():
            nonlocal last_stock_prices
            while True:
                stock_prices = get_stock_prices()
                if stock_prices != last_stock_prices:
                    await websocket.send_text(json.dumps(stock_prices))
                    last_stock_prices = stock_prices
                await asyncio.sleep(5)
        task = asyncio.create_task(send_stock_prices())
        try:
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
        finally:
            task.cancel()

    except Exception as e:
        logging.error(f"WebSocket connection error: {e}")
        raise