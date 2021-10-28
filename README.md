# rpi-btc-ticker

rpi-btc-ticker is a Python-based Raspberry Pi cryptocurrency ticker using a 2.13" e-Ink display. 

This program is geared towards ease-of-use. It is not a finished product and there are more features to be added. A section in this README on how you can customize the display will be made eventually.

## Installation

First, clone the repository:
```bash
git clone https://github.com/nickshanks347/rpi-btc-ticker.git
```

Install dependencies:
```bash
sudo apt update
sudo apt install wiringpi python3-pip python3-pil python3-numpy
```

Install BCM2835 drivers:
```bash
wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.70.tar.gz
tar zxvf bcm2835-1.70.tar.gz
cd bcm2835-1.70/
sudo ./configure
sudo make
sudo make check
sudo make install
```

Turn on SPI via `sudo raspi-config` (reboot after doing this step):
```
Interfacing Options -> SPI
```

Now `cd` to `rpi-btc-ticker` and install the pip requirements:
```bash
cd rpi-btc-ticker
pip3 install -r requirements.txt
pip3 install ./e-Paper/RaspberryPi_JetsonNano/python/
```

## Usage


Included in the repository is a `config.cfg` file. It has this format:
```
[main]
coin: bitcoin,litecoin,ethereum
fiat: gbp
```
`coin` specifies which three cryptocurrencies you would like displayed. The order entered in the config file will be the order they appear on the display. Please ensure to keep the same format, and only include commas (no spaces) between each coin.

-   The coin terms entered in the config file are used by the program and sent directly to an API. If you would like to know what to put for a certain coin then go to [CoinGecko](https://coingecko.com) and search for your coin in the top right. Under the `Info` section, you'll see an entry for `API id`. Copy this ID and enter this in the config file. 
-   Example: Ethereum Classic (https://www.coingecko.com/en/coins/ethereum-classic) has an `API id` of `ethereum-classic`.

`fiat` specifies which fiat currency you would like the program to display. Example: if you have `fiat` set to `gbp` in the config file, the program will display what 1 BTC is equal to in £.

```bash
python3 main.py
```

This will launch the Python program. After a few seconds, you will see the e-Ink display update with your chosen cryptos.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[Apache](http://www.apache.org/licenses/LICENSE-2.0)