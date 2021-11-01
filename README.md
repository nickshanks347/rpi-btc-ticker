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
refresh_interval: 1
```
`coin` specifies which three cryptocurrencies you would like displayed. The order entered in the config file will be the order they appear on the display. Please ensure to keep the same format, and only include commas (no spaces) between each coin.

-   The coin terms entered in the config file are used by the program and sent directly to an API. If you would like to know what to put for a certain coin then go to [CoinGecko](https://coingecko.com) and search for your coin in the top right. Under the `Info` section, you'll see an entry for `API id`. Copy this ID and enter this in the config file. 
-   Example: Ethereum Classic (https://www.coingecko.com/en/coins/ethereum-classic) has an `API id` of `ethereum-classic`.

`fiat` specifies which fiat currency you would like the program to display. Example: if you have `fiat` set to `gbp` in the config file, the program will display what 1 BTC is equal to in £.

`refresh_interval` is the time between refreshes of the coin prices and any changes to the config file. The unit is seconds, so for 10 minutes you'd write 600. 

The config file is read dynamically (it is not loaded into memory). If you want to change the coins/fiat shown, or the refresh interval then you can do so and it'll be re-read at the next refresh time without having to restart the program.

---
To launch within your terminal window type: 
```
python3 main.py
```

To launch the service type: 
```
sudo service crypto-ticker start
```

This will launch the Python program. After a few seconds, you will see the e-Ink display update with your chosen cryptos.

## Starting automatically at boot (`systemd integration`)

We'll utilise `systemd` to automatically start our service at boot. 

First, type `sudo nano /etc/systemd/system/crypto-ticker.service` and paste the service definition below:
```bash
 [Unit]
 Description=crypto-ticker
 After=network.target

 [Service]
 ExecStart=/usr/bin/python3 -u main.py
 WorkingDirectory=/home/pi/rpi-btc-ticker
 StandardOutput=inherit
 StandardError=inherit
 KillSignal=SIGINT
 Restart=always
 User=pi
 Restart=on-failure

 [Install]
 WantedBy=multi-user.target
 ```
Please note the `ExecStart` and `WorkingDirectory`, change these as needed if you cloned to a different directory.

Now reload systemctl daemon (this is only needed if we're interacting with systemctl, which we're not, but it's good to run anyway):
```bash
sudo systemctl daemon-reload
```

Now the service is set up, but it's not running. You can run: `sudo service crypto-ticker <option>`, replacing `<option>` with either `start`, `stop`, `restart`, `disable`, `enable` and `status`.

To start the program at boot, run `sudo service crypto-ticker enable`. Run the command with `disable` to disable at boot. 

If you're having issues then run `sudo service crypto-ticker restart`.

The `status` option is quite useful as it shows the services status and the last few log entries. 


## Known Issues

The program rounds the price of each crypto currency to the nearest 2 decimal places. Ultimately this can be turned off but it might cause issues where digits overflow off of the screen. A fix will be found.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[Apache](http://www.apache.org/licenses/LICENSE-2.0)