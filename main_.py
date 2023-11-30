import json
import re
import asyncio
import httpx
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from security.oauth import TokenData, get_current_user
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

symbols = ['AAPL', 'AMZN', 'GOOGL', 'MSFT', 'TSLA', 'GOOG', 'NVDA', 'BA', 'NFLX']

async def fetch_data(client, semaphore, stock, data):

    async with semaphore:
        ua = UserAgent()
        headers = {'User-Agent': ua.random}
        url = f'https://www.google.com/finance/quote/{stock}:NASDAQ'

        response = await client.get(url, headers=headers)

        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, 'lxml')
            targetDiv = soup.find('div', class_='YMlKec fxKbKc')

            if targetDiv:
                stockPrice = float(targetDiv.text.strip()[1:])
                pageTitle = soup.title.text
                stockName = pageTitle.split('Stock')[0].strip()
                stockSymbolShort = re.search(r'\((.*?)\)', stockName).group(1)
                data[stockSymbolShort] = stockPrice
            return data
        else:
            print(f'Failed to retrieve the page for {stock}. Status code: {response.status_code}')

async def fetch_all_stocks(stock_symbols):
    data = {}
    semaphore = asyncio.Semaphore(8)
    async with httpx.AsyncClient() as client:
        tasks = [fetch_data(client, semaphore, stock, data.copy()) for stock in stock_symbols]
        results = await asyncio.gather(*tasks)
    findata = {}
    for result in results:
        findata.update(result)
    return findata

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/favicon.ico")
async def favicon(request: Request):
    return "No Favicon"

@app.get("/stock_data_generator")
async def stock_data_generator(request: Request, current_user: TokenData = Depends(get_current_user)):
    async def generate():
        while True:
            result_var = await fetch_all_stocks(symbols)
            stock_prices = json.dumps(result_var)
            yield f"data: {stock_prices}\n\n"
            await asyncio.sleep(1)

    return StreamingResponse(generate(), media_type="text/event-stream")