import json
import random
import time
import sys
import os
import traceback
import logging
import configparser

from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from datetime import datetime, timezone, timedelta
from pycoingecko import CoinGeckoAPI
from currency_symbols import CurrencySymbols
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
from waveshare_epd import epd2in13_V2

logging.basicConfig(level=logging.INFO)

logging.info("Imported and started logging")
basedir = Path(__file__).parent
waveshare_base = basedir.joinpath('e-Paper', 'RaspberrPi_JetsonNano','Python')
libdir = waveshare_base.joinpath('lib')
logging.info("Init functions...")

def read_config():
    config = configparser.ConfigParser()
    config.read('config.cfg')
    fiat_currency = config['main']['fiat']
    crypto_list = config['main']['coin'].split(',')
    return crypto_list, fiat_currency

def fetch_prices():
    cg = CoinGeckoAPI()
    crypto_list_config, fiat_currency = read_config()
    crypto_list = []
    crypto_price_list = []
    crypto_price_change_24h = []
    crypto_percentage_24h = []
    for coin in crypto_list_config:
        get_coins = cg.get_coins_markets(ids=coin, vs_currency=fiat_currency)[0]
        coin_name = get_coins['symbol'].upper()
        coin_current_price = get_coins['current_price']
        coin_price_change_24h = get_coins['price_change_24h']
        coin_percentage_24h = get_coins['price_change_percentage_24h']

        coin_current_price = str(round(coin_current_price, 2))
        coin_price_change_24h = str(round(coin_price_change_24h, 2))
        coin_percentage_24h = str(round(coin_percentage_24h, 2))

        crypto_list.append(coin_name)
        crypto_price_list.append(coin_current_price)
        crypto_price_change_24h.append(coin_price_change_24h)
        crypto_percentage_24h.append(coin_percentage_24h)
    return crypto_list, crypto_price_list, crypto_price_change_24h, crypto_percentage_24h, fiat_currency

def set_font_size(font_size):
    logging.info(f"Loading font with font size {font_size}...")
    return ImageFont.truetype(f"{basedir.joinpath('CascadiaCode.ttf').resolve()}", font_size)

def main():
    logging.info("Starting...")
    epd = epd2in13_V2.EPD()
    logging.info("Initialize and clear...")
    epd.init(epd.FULL_UPDATE)
    epd.Clear(0xFF)
    logging.info("Welcome screen...")
    image = Image.new('1', (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(image)
    jpg = Image.open(basedir.joinpath("img", "bitcoin.jpg"))
    image.paste(jpg, (0,0))
    image = image.rotate(180)
    epd.display(epd.getbuffer(image))
    logging.info(f"Creating canvas - height: {epd.height}, width: {epd.width}")
    image = Image.new('1', (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(image)
    cascadia64 = set_font_size(64)
    cascadia36 = set_font_size(36)
    cascadia32 = set_font_size(32)
    cascadia24 = set_font_size(24)
    cascadia22 = set_font_size(22)
    cascadia18 = set_font_size(18)
    cascadia16 = set_font_size(16)
    cascadia15 = set_font_size(15)
    cascadia12 = set_font_size(12)
    epd.init(epd.FULL_UPDATE)
    epd.displayPartBaseImage(epd.getbuffer(image))
    epd.init(epd.PART_UPDATE)
    try:
        while True:
            crypto_list, crypto_price_list, crypto_price_change_24h, crypto_percentage_24h, fiat_currency = fetch_prices()
            fiat = CurrencySymbols.get_symbol(fiat_currency.upper())
            draw.rectangle((0, 0, 250, 250), fill = 255)
            # Limits are 140, 95
            draw.text((0, 0), f'{crypto_list[0]} = {fiat}{crypto_price_list[0]}', font = cascadia24, fill = 0)
            draw.text((0, 20), f'24h = {crypto_percentage_24h[0]}%/{fiat}{crypto_price_change_24h[0]}', font = cascadia16, fill = 0)
            draw.text((0, 40), f'{crypto_list[1]} = {fiat}{crypto_price_list[1]}', font = cascadia24, fill = 0)
            draw.text((0, 60), f'24h = {crypto_percentage_24h[1]}%/{fiat}{crypto_price_change_24h[1]}', font = cascadia16, fill = 0)
            draw.text((0, 80), f'{crypto_list[2]} = {fiat}{crypto_price_list[2]}', font = cascadia24, fill = 0)
            draw.text((0, 100), f'24h = {crypto_percentage_24h[2]}%/{fiat}{crypto_price_change_24h[2]}', font = cascadia16, fill = 0)
            image_rotated = image.rotate(180)
            logging.debug(crypto_list)
            logging.debug(crypto_price_list)
            epd.displayPartial(epd.getbuffer(image_rotated))   
            time.sleep(1) 
    except KeyboardInterrupt:
        logging.info("Caught Ctrl + C. Exiting...")
        epd.init(epd.FULL_UPDATE)
        epd.Clear(0xFF)
        epd.sleep()
        exit()
    except IOError as e:
        logging.info(e)
    
logging.info("Running main function...")
main()