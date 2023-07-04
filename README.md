# Discord Bot

# Table of Contents
1. [Features](#features) 
2. [Prerequisites](#prerequisites)
3. [Getting Started](#getting-started)

# Features
- [Play Music from YouTube and Spotify](#play-music-from-youtube-and-spotify)
- [Get CS:GO Lineups](#get-csgo-lineups)
- [Get Counters for a Leauge of Legend Champion](#get-counter-for-a-leauge-of-legends-champion)

## Play Music from YouTube and Spotify
![](img/cmd_play.png)

## Get CS:GO Lineups
![](img/cmd_lineups.png)

## Get Counter for a Leauge of Legends Champion
![](img/cmd_counter.png)


# Prerequisites
1. [Create a Discord Bot Account and invite the bot to your server](https://discordpy.readthedocs.io/en/stable/discord.html)
2. Install Python3 and Pip3
    ```
    sudo apt install python3 && sudo apt install python3-pip
    ```
3. Install FFmpeg
    ```
    sudo apt install ffmpeg
    ```

## Getting Started
1. Create a virtual environment
    ```
    python3 -m venv venv
    ```
2. Activate the virtual environment
    ```
    source venv/bin/activate
    ```
3. Install dependencies
    ```
    pip3 install -r requirements.txt
    ```
4. Create .env file with the following content:
    ```
    DISCORD_TOKEN = <your discord token>
    SPOTIFY_CLIENT_ID = <your spotify client id>
    SPOTIFY_CLIENT_SECRET = <your spotify client secret>
    ```
5. Run the bot
    ```
    python3 src/bot.py
    ```
