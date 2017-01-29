# Li'l Butler
[![PEP8](https://img.shields.io/badge/code%20style-pep8-green.svg)](https://www.python.org/dev/peps/pep-0008/)
[![Gitgud Build Status](https://gitgud.io/sug/lilbutler/badges/master/build.svg)](https://gitgud.io/sug/lilbutler/commits/master)
[![Travis Build Status](https://travis-ci.org/sugrocks/lilbutler.svg?branch=master)](https://travis-ci.org/sugrocks/lilbutler)

> _Oh, you're the butler who touches our hearts._
> _"You people have too much money!"_

Just a discord bot. It has some commands and it deletes links to other servers.


## Requirements
- I'd recommand you to have python 3.5+. 3.6 is the best idea.
    + pip
- A Discord bot created. Head over there: https://discordapp.com/developers/applications/me
    + Create an app
    + Then convert it to a bot account
    + Copy the `Client ID` and `Token` for later use
+ Add the discord bot to your server
    + Go to `https://discordapp.com/oauth2/authorize?client_id=[client id]&scope=bot` (replace `[client id]` with your own)
    + Select your server and accept
    + Give proper permissions to the bot in your server


## Install

```
pip3.6 install -r requirements.txt
cp config.ini.dist config.ini
nano config.ini  # see Config bellow
tmux
    python3.6 bot.py
```


## Config
- `bot.token`: the discord bot token
- `cleantemp`: list of channels to clean after 100 messages. Put whatever you want as value, only the key counts

**Example:**
```
[bot]
token = youputhereyourverysecrettokenthatyoushouldnotshare

[cleantemp]
274153487359672320 = True
274153638002294784 = sure
274153443675996160 = whatever
274153469827350528 = yes, like that
```

## Commands
_(`*` means the user needs the `kick` role in the channel, `^` for server admin)_

- `!countdown`: Time until next SU episode.  
    + Will return a countdown.
- `!pick`: Pick an element, delimited by "or".
    + Example: `pizza or taco or burger`
- `!ping`: PONG!
    + Just to test if you're still there.
- `*` `!clean`: The bot deletes is own messages.
    + Specify a number or it will clean the last 50 messages.
- `*` `!nuke <n>`: Delete a number of messages.
    + In case the bot went crazy...
- `^` `!sleep`: Stops the bot.
    + But it might come back! (If you put it in a loop or something)
- `!help <command|category>`: Display the help message
