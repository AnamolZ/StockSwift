import asyncio
import logging
import json
import yfinance as yf

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

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
    """
    Retrieves the latest stock prices and historical data for a list of symbols.

    Returns:
        A dictionary containing stock data for each symbol.
    """
    symbols = ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA", "GOOG", "FB", "NVDA", "BA", "NFLX"]
    stock_data = {}
    for symbol in symbols:
        try:
            # Fetch stock data using yfinance
            stock = yf.Ticker(symbol)
            data = stock.history(period="1d")
            # Extract relevant data from the historical data
            last_price = round(data["Close"].iloc[-1], 2)
            history = [round(price, 2) for price in data["Close"].tolist()]
            # Create a dictionary with stock information
            stock_data[symbol] = {
                "symbol": symbol,
                "price": last_price,
                "history": history,
            }
        except Exception as e:
            logging.error(f"Error fetching data for {symbol}: {e}")
    return stock_data

# Route to serve HTML content at root endpoint
@app.get("/", response_class=HTMLResponse)
async def read_root():
    """
    Serves the static HTML index page.

    Returns:
        An HTMLResponse containing the index page content.
    """
    index_path = "./static/index.html"
    with open(index_path, "r", encoding="utf-8") as file:
        content = file.read()
    return HTMLResponse(content)

@app.get("/data")
async def read_root():
    """
    Provides the latest stock prices and historical data for the specified symbols.

    Returns:
        A JSON response containing stock data for each symbol.
    """
    stock_prices = get_stock_prices()
    return {
        "message": "Welcome to the Stock Data API",
        "stock_data": stock_prices
    }

# Route for favicon (!NOT NECESSARY)
@app.get("/favicon.ico")
async def get_favicon():
    return {"message": "No favicon here"}

# Endpoint to provide (RT) stock data
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
        # Create a task to run the send_stock_prices function
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
