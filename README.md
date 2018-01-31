[![Build Status](https://travis-ci.org/Faxn/Faxn-Cogs.svg?branch=master)](https://travis-ci.org/Faxn/Faxn-Cogs)

A set of experimental and messy cogs for (https://github.com/Cog-Creators/Red-DiscordBot).

## Adding these cogs to Red

Chat to your friendly local red bot(assuming that you are it's owner.)

`!cog repo add Faxn-Cogs https://github.com/Faxn/Faxn-Cogs`

Then list the cogs with:

`!cog list Faxn-Cogs`


## Running the devbot
This repository contains a simple discord bot that loads all the cogs in this repository for testing purposes.

Optionally setup a virtualenv to keep packages separate from system packages.

`
python3 -m venv create env
source env/bin/activate
`

Install requirements (Requires root if not using virtualenv).

`
pip install -r requirements.txt
`

Run the bot and follow the instructions to connect it to your discord server.

`
source env/bin/activate
./bot.py
`
