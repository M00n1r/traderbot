import requests
import threading
import time
import json
import sys
import socket

from datetime import datetime
from twython import Twython
from keys import (
    TAAPI_key,
    API_key,
    API_secret_key,
    access_token,
    access_token_secret
)
 
#Function for Pulling Price from Binance
def get_price(symbol):

  binance_api = 'https://api.binance.com/api/v3/ticker/price?symbol='
  response = requests.get(binance_api + symbol)
  if response.status_code == 200:
    data = json.loads(response.content.decode('utf-8'))
    return data['price']

    
#Function for Calculating RSI
def get_rsi(symbol, interval):

    api_url = f"https://api.binance.com/api/v1/klines?symbol={symbol}&interval={interval}&limit=14"
    response = requests.get(api_url)
    data = response.json()

    # Calculate delta, 1-period RSI
    delta = []
    up = 0
    down = 0
    for i in range(1, len(data)):
        delta.append(float(data[i][4]) - float(data[i-1][4]))
        if delta[i-1] > 0:
            up += delta[i-1]
        else:
            down += abs(delta[i-1])
    avg_up = up/14
    avg_down = down/14
    rsi = 100 - (100/(1+(avg_up/avg_down)))
    return rsi
 
 
#Function for Calculating Bollinger bands 
def get_bollinger(symbol, interval):

    # Get Bollinger Band data from Binance API
    api_url = f"https://api.binance.com/api/v1/klines?symbol={symbol}&interval={interval}"
    response = requests.get(api_url)
    data = json.loads(response.text)

    # Calculate Bollinger Bands
    bb = []
    for index in range(len(data)):
        # Calculate 20-day SMA
        sma = 0
        for i in range(20):
            sma += float(data[index-i][4])
        sma /= 20

        # Calculate Standard Deviation
        sd = 0
        for i in range(20):
            sd += (float(data[index-i][4]) - sma)**2
        sd = (sd / 20)**0.5

        # Calculate Upper Band, Middle Band and Lower Band
        upper_band = sma + 2*sd
        middle_band = sma
        lower_band = sma - 2*sd

        bb.append([upper_band, middle_band, lower_band])

    return bb


# Main thread
def analysePrice():
    
    short = 0
    long = 0
    
    while True:
    try:
        # var declaration
        #symbol = "BTCUSDT"
        #interval = "1d"
        now = datetime.now()
        date_time = now.strftime("%d/%m/%Y %H:%M:%S")
        symbol = sys.argv[1]
        interval = sys.argv[2]
        bb = get_bollinger(symbol, interval)
        
        # Extract data in json format
        rsi = round(float(get_rsi (symbol, interval)),2)
        bbandsUP, bbandsMID, bbandsLOW = bb[-1]
        bbandsUP = round(float(bbandsUP),2)
        bbandsMID = round(float(bbandsMID),2)
        bbandsLOW = round(float(bbandsLOW),2)
        price = round(float(get_price (symbol)),2)

        twitter = Twython(
            API_key,
            API_secret_key,
            access_token,
            access_token_secret
        )
        print("================= "+date_time+" =====================")
        print(f" {symbol}: ${price} \n Timeframe: {interval}\n RSI: {rsi} \n Bbands UP: {bbandsUP} \t Mid: {bbandsMID} \t Low: {bbandsLOW} \n")


        if (long == 0 and rsi <= 30 and price <= bbandsLOW):
              message = date_time+ f"\n LONG  {symbol} at: ${price} \n Timeframe : {interval} \n PUMP IT !!!"
              twitter.update_status(status=message)
              print(f"Tweeted: "+message)
              long = 1
              short = 0
        elif (short == 0 and rsi >= 70 and price <= bbandsUP):
              message = date_time+ f"\n SHORT {symbol} at: ${price} \n Timeframe : {interval} \n DUMP IT !!!"
              twitter.update_status(status=message)
              print("Tweeted: "+message)
              short = 1
              long = 0

        time.sleep(60)
        
    except requests.exceptions.RequestsException as e:
        print("RequestsException : ", e)    
    except MemoryError as e:
        print("MemoryError : ", e)    
    except Exception as e:
        print("Error : ", e)

t1 = threading.Thread(target=analysePrice)
t1.start()
