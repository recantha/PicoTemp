# PicoTemp
Micropython temperature sensor code for PicoW linked to io.adafruit.com

## Hardware
* Raspberry Pi PicoW (moo!).
* Adafruit (or other) AHT20 (or 10) temperature/humidity sensor.

## Config
You will need a config.py to specify a feed "prefix" that you will use when creating
your MQTT "feeds" in io.adafruit.com.

## Register an account with Adafruit
Go to https://io.adafruit.com/ and create yourself an account.
You will need two feeds prefixed with the feed_prefix value in config.py.
The two feeds should be called <prefix>_temperature and <prefix>_humidity.

## Secrets
You will need to create a secrets.py file (excluded from this repository) similar to sample_secrets.py.
In there, you place your credentials and account name for io.adafruit.com.
