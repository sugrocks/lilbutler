# Li'l Butler
[![PEP8](https://img.shields.io/badge/code%20style-pep8-green.svg)](https://www.python.org/dev/peps/pep-0008/)
[![Gitgud Build Status](https://gitgud.io/sug/lilbutler/badges/master/build.svg)](https://gitgud.io/sug/lilbutler/commits/master)
[![Travis Build Status](https://travis-ci.org/sugrocks/lilbutler.svg?branch=master)](https://travis-ci.org/sugrocks/lilbutler)

> _Oh, you're the butler who touches our hearts._  
> "You people have too much money!"

Just a discord bot. It has some commands and it deletes links to other servers.


## Requirements
- Python 3.6
    + [pipenv](https://github.com/kennethreitz/pipenv)
- A Discord bot created. Head over there: https://discordapp.com/developers/applications/me
    + Create an app
    + Then convert it to a bot account
    + Copy the `Client ID` and `Token` for later use
+ Add the discord bot to your server
    + Go to `https://discordapp.com/oauth2/authorize?client_id=[client id]&scope=bot` (replace `[client id]` with your own)
    + Select your server and accept
    + Give proper permissions to the bot in your server


## Install

```bash
pipenv install --python $(which python3.6)
cp config.ini.dist config.ini
nano config.ini  # see Config below
tmux
    pipenv run python bot.py
```


## Config
- `bot.token`: the discord bot token (needed to login to Discord)
- `bot.owner_id`: the ID of the owner (needed to stop the bot remotly)
- `modlogs`: list of `<server id> = <channel id>` where join/leave/ban logs are going to be posted
- `cleantemp`: list of channels to clean after 100 messages. Put whatever you want as value, only the key counts

**Example:**
```ini
[bot]
token = youputhereyourverysecrettokenthatyoushouldnotshare
owner_id = 81293337012744192

[modlogs]
274151655795064832 = 274156905080029196

[cleantemp]
274153487359672320 = True
274153638002294784 = sure
274153443675996160 = whatever
274153469827350528 = yes, like that
```


## Commands
_(`*` means the user needs the `kick` role in the channel, `^` for owner)_

- `~bumps`: See how many times you bumped the server
    + Getting successfully bumps from ServerHound increment your score.
- `~countdown`: Time until next SU episode.
    + Will return a countdown.
- `~pick`: Pick an element, delimited by "or".
    + Example: `pizza or taco or burger`
- `~ping`: PONG!
    + Just to test if you're still there.
- `*` `~clean`: The bot deletes is own messages.
    + In case the bot went crazy...
- `*` `~nuke <n|50>`: Delete a number of messages. (`n` is optional)
    + Specify a number or it will clean the last 50 messages.
- `^` `~sleep`: Stops the bot.
    + But it might come back! (If you put it in a loop or something)
- `~help <command|category>`: Display the help message
