"""
Stock Swift

This FastAPI-based web application provides real-time and historical stock data through various endpoints,
including a WebSocket connection for dynamic updates.

Modules and Libraries:
- asyncio: Asynchronous programming to handle WebSocket connections.
- logging: Configured to record errors in 'error.log'.
- json: Used for JSON serialization.
- yfinance: Library for fetching stock data.
- FastAPI: Modern, fast (high-performance), web framework for building APIs.
- CORSMiddleware: Middleware for Cross-Origin Resource Sharing.
- StaticFiles: Middleware to serve static files.
- HTMLResponse: FastAPI response class for serving HTML content.

Application Structure:
- FastAPI instance: The main application instance for defining routes and handling requests.
- CORSMiddleware: Middleware configured to handle Cross-Origin Resource Sharing.
- StaticFiles: Middleware for serving static files such as HTML pages.
- 'get_stock_prices': Function to retrieve the latest stock prices and historical data.
- '/': Route serving the static HTML index page.
- '/data': Route providing the latest stock prices and historical data.
- '/favicon.ico': Route for favicon (not necessary).
- '/ws': WebSocket endpoint for real-time stock data updates.

Please note that this application uses the 'yfinance' library to fetch stock data.
For WebSocket connections, the server sends stock updates every 5 seconds to connected clients.

Author: Anamol Dhakal
Date: 2023-11-16
"""

import asyncio
import logging
import json
import yfinance as yf

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

# FastAPI application instance
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
    """
    Handles WebSocket connections to provide real-time stock data updates.

    Establishes a WebSocket connection and periodically sends real-time stock updates to the client.

    Args:
        websocket: The WebSocket connection object.
    """
    try:
        await websocket.accept()
        # Initialize variables to track stock prices
        last_stock_prices = None
        # Define an asynchronous task to send stock updates periodically
        async def send_stock_prices():
            nonlocal last_stock_prices
            while True:
                # Fetch the latest stock prices
                stock_prices = get_stock_prices()
                if stock_prices != last_stock_prices:
                    # Convert stock prices to JSON format
                    await websocket.send_text(json.dumps(stock_prices))
                    # Update last stock prices to avoid sending duplicate updates
                    last_stock_prices = stock_prices
                await asyncio.sleep(5)
        # Create a task to run the send_stock_prices function
        task = asyncio.create_task(send_stock_prices())
        try:
            # Keep the connection open until the client closes it or an error occurs
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            # If the task is cancelled, pass silently
            pass
        finally:
            # Cancel the task to stop sending stock updates
            task.cancel()

    except Exception as e:
        # If an error occurs, log the error and close the connection
        logging.error(f"WebSocket connection error: {e}")
        raise
"""

Instructions:
    - Ensure that all necessary dependencies are installed (use requirements.txt or similar).
    - Start the FastAPI application using the following command:
        uvicorn your_module_name:app --reload
    - Access the API documentation at http://127.0.0.1:8000/docs for interactive documentation.
    - Visit http://127.0.0.1:8000/ in your browser to access the main application.

"""