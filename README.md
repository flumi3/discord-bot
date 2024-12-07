# Discord Bot

# Table of Contents

1. [Features](#features)
2. [Prerequisites](#prerequisites)
3. [Getting Started](#getting-started)

# Features

- [Music Player](#music-player)
- [CS:GO Buddy](#csgo-buddy)
- [LoL Buddy](#lol-buddy)

## Music Player

![](docs/img/cmd_play.png)

## CS:GO Buddy

### Get lineups for a map

![](docs/img/cmd_lineups.png)

### Get callouts for a map

![](docs/img/cmd_callouts.png)

### Get the jumpthrow bind that you can paste into your console

![](docs/img/cmd_jumpthrow.png)

### Get the practice config that you can paste into your console

![](docs/img/cmd_practice.png)

## LoL Buddy

### Get counter champions for a League of Legends champion

![](docs/img/cmd_counter.png)

# Getting Started

## Prerequisites

> :memo: **Note:** This project uses Poetry for
simple and consistent dependency management. If you want to learn more about
Poetry see their [Introduction](https://python-poetry.org/docs/) or
[Basic usage](https://python-poetry.org/docs/basic-usage/) documentation.

1. [Create a Discord Bot Account and invite the bot to your server](https://discordpy.readthedocs.io/en/stable/discord.html)

2. Create .env file with the following content:

    ```bash
    DISCORD_TOKEN = <your discord token>
    SPOTIFY_CLIENT_ID = <your spotify client id>
    SPOTIFY_CLIENT_SECRET = <your spotify client secret>
    ```

3. Install [FFmpeg](https://www.ffmpeg.org/)

    ```bash
    sudo apt update
    sudo apt install ffmpeg
    ```

4. Install Python and [pipx](https://github.com/pypa/pipx)

    ```bash
    sudo apt install python3
    sudo apt install pipx
    ```

5. Install [Poetry](https://python-poetry.org/docs/)

    ```bash
    pipx install poetry
    ```

6. Install project dependencies

    ```bash
    poetry install
    ```

## Running the project

1. Activate the Poetry shell

    ```bash
    poetry shell
    ```

2. Run the discord bot

    ```bash
    poetry run python discord_bot/bot.py
    ```

### Create Cron Job

If you want to run the discord bot on a server (e.g. a Oracle cloud free tier VM running Ubuntu) you can create a cron
job that will automatically start the Discord bot upon each reboot.

1. Edit your crontab file with `crontab -e`
2. Add `@reboot python3 /home/ubuntu/discord-bot/src/bot.py &` to the bottom of the configuration
