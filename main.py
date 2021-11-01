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
    refresh_interval = config['main']['refresh_interval']
    return crypto_list, fiat_currency, refresh_interval

def fetch_prices():
    cg = CoinGeckoAPI()
    crypto_list_config, fiat_currency, refresh_interval = read_config()
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
    return crypto_list, crypto_price_list, crypto_price_change_24h, crypto_percentage_24h, fiat_currency, refresh_interval

def set_font_size(font_size):
    logging.debug(f"Loading font with font size {font_size}...")
    return ImageFont.truetype(f"{basedir.joinpath('CascadiaCode.ttf').resolve()}", font_size)

def welcome_screen():
    cg = CoinGeckoAPI()
    logging.info("Starting...")
    epd = epd2in13_V2.EPD()
    logging.info("Initialize and clear...")
    epd.init(epd.FULL_UPDATE)
    epd.Clear(0xFF)
    logging.info("Initialize fonts...")
    cascadia64 = set_font_size(64)
    cascadia36 = set_font_size(36)
    cascadia32 = set_font_size(32)
    cascadia24 = set_font_size(24)
    cascadia22 = set_font_size(22)
    cascadia18 = set_font_size(18)
    cascadia16 = set_font_size(16)
    cascadia15 = set_font_size(15)
    cascadia12 = set_font_size(12)
    logging.info("Welcome screen...")
    image = Image.new('1', (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(image)
    jpg = Image.open(basedir.joinpath("img", "bitcoin.jpg"))
    image.paste(jpg, (0,0))
    image = image.rotate(180)
    epd.display(epd.getbuffer(image))
    time.sleep(1)
    logging.info("Ping test...")
    ping = cg.ping()
    logging.info(ping)
    image = Image.new('1', (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(image)
    draw.text((0, 60), f'{ping}', font = cascadia12, fill = 0)
    image = image.rotate(180)
    epd.display(epd.getbuffer(image))
    time.sleep(4)

def main():
    cg = CoinGeckoAPI()
    logging.info("Starting...")
    epd = epd2in13_V2.EPD()
    logging.info("Initialize and clear...")
    epd.init(epd.FULL_UPDATE)
    epd.Clear(0xFF)

    logging.info("Initialize fonts...")
    cascadia64 = set_font_size(64)
    cascadia36 = set_font_size(36)
    cascadia32 = set_font_size(32)
    cascadia28 = set_font_size(28)
    cascadia26 = set_font_size(26)
    cascadia24 = set_font_size(24)
    cascadia22 = set_font_size(22)
    cascadia18 = set_font_size(18)
    cascadia16 = set_font_size(16)
    cascadia15 = set_font_size(15)
    cascadia12 = set_font_size(12)
    
    logging.info(f"Creating canvas - height: {epd.height}, width: {epd.width}")
    while True:
        try:
            image = Image.new('1', (epd.height, epd.width), 255)
            draw = ImageDraw.Draw(image)
            epd.displayPartBaseImage(epd.getbuffer(image))
            epd.init(epd.PART_UPDATE)

            crypto_list, crypto_price_list, crypto_price_change_24h, crypto_percentage_24h, fiat_currency, refresh_interval = fetch_prices()
            fiat = CurrencySymbols.get_symbol(fiat_currency.upper())
            draw.rectangle((0, 0, 250, 250), fill = 255)
            # Limits are 140, 95
            draw.text((0, 0), f'{crypto_list[0]}/{fiat}{crypto_price_list[0]}', font = cascadia24, fill = 0)
            draw.text((0, 20), f'{crypto_percentage_24h[0]}%/{fiat}{crypto_price_change_24h[0]}', font = cascadia16, fill = 0)
            draw.text((0, 40), f'{crypto_list[1]}/{fiat}{crypto_price_list[1]}', font = cascadia24, fill = 0)
            draw.text((0, 60), f'{crypto_percentage_24h[1]}%/{fiat}{crypto_price_change_24h[1]}', font = cascadia16, fill = 0)
            draw.text((0, 80), f'{crypto_list[2]}/{fiat}{crypto_price_list[2]}', font = cascadia24, fill = 0)
            draw.text((0, 100), f'{crypto_percentage_24h[2]}%/{fiat}{crypto_price_change_24h[2]}', font = cascadia16, fill = 0)
            logging.debug(crypto_list)
            logging.debug(crypto_price_list)
            image = image.rotate(180)
            epd.displayPartial(epd.getbuffer(image))   
            time.sleep(int(refresh_interval)) 
        except KeyboardInterrupt:
            logging.info("Caught Ctrl + C. Exiting...")
            epd.init(epd.FULL_UPDATE)
            epd.Clear(0xFF)
            epd.sleep()
            exit()
        except IOError as e:
            logging.info(e)
        except IndexError as e:
            epd.Clear(0xFF)
            logging.info(e)
            draw.text((30, 40), f'config error:', font = cascadia24, fill = 0)
            draw.text((30, 60), f'coin', font = cascadia24, fill = 0)
            image = image.rotate(180)
            epd.displayPartBaseImage(epd.getbuffer(image))
            epd.init(epd.PART_UPDATE)
            epd.displayPartial(epd.getbuffer(image))
            logging.info("Please fix your config, this program will restart in 10 seconds.")
            time.sleep(10)
            epd.Clear(0xFF)
        except ValueError as e:
            epd.Clear(0xFF)
            logging.info(e)
            draw.text((30, 40), f'config error:', font = cascadia24, fill = 0)
            draw.text((30, 60), f'fiat', font = cascadia24, fill = 0)
            image = image.rotate(180)
            epd.displayPartBaseImage(epd.getbuffer(image))
            epd.init(epd.PART_UPDATE)
            epd.displayPartial(epd.getbuffer(image))
            logging.info("Please fix your config, this program will restart in 10 seconds.")
            time.sleep(10)
            epd.Clear(0xFF)

        
logging.info("Running welcome screen...")
welcome_screen()
logging.info("Looping main function...")
while True:
    try:
        main()
    except IndexError:
        main()
