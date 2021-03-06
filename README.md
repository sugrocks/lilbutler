# Li'l Butler
[![PEP8](https://img.shields.io/badge/code%20style-pep8-green.svg)](https://www.python.org/dev/peps/pep-0008/)
[![Gitlab Build Status](https://gitlab.com/ctoon/sug/lilbutler/badges/master/build.svg)](https://gitlab.com/ctoon/sug/lilbutler/commits/master)
[![Travis Build Status](https://travis-ci.org/sugrocks/lilbutler.svg?branch=master)](https://travis-ci.org/sugrocks/lilbutler)
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgitlab.com%2Fctoon%2Fsug%2Flilbutler.svg?type=shield)](https://app.fossa.io/projects/git%2Bgitlab.com%2Fctoon%2Fsug%2Flilbutler?ref=badge_shield)

> _Oh, you're the butler who touches our hearts._
> "You people have too much money!"

Just a discord bot. It has some commands and it deletes links to other servers.


## Requirements
- Python 3.6
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
pip install -r requirements.txt -U
cp config.ini.dist config.ini
nano config.ini  # see Config below
python bot.py
```


## Config
- `bot.token`: the discord bot token (needed to login to Discord)
- `bot.owner_id`: the ID of the owner (needed to stop the bot remotly)
- `bot.whitelist` list of ids (delemited by a comma without spaces) of servers the bot can be in
- `automute`: list of `<server id> = <role id>` where the role id is a mute role, given to people in discord bans
- `birthday`: list of `<server id> = <role id>` where the role id is a birthday role
- `joinlogs`: list of `<server id> = <channel id>` where joins/leaves/bans logs are going to be posted
- `msglogs: list of `<server id> = <channel id>` where deleted message are logged
- `cleantemp`: list of channels to clean after 100 messages or a week. Put whatever you want as value, only the key counts
- `savepics`: list of `<channel id> = <path>` where pics sent in the channel are saved to a local path

**Some examples:**
```ini
[bot]
token = woa_there
owner_id = 81293337012744192
whitelist = 274151655795064832,199198145811447808

[joinlogs]
; server id = join/part/ban logs channel id
199198145811447808 = 428171700132118538

[msglogs]
; server id = deleted/edit messages logs channel id
199198145811447808 = 428171700132118538

[cleantemp]
; channel id
274153487359672320 = True
274153638002294784 = sure
274153443675996160 = whatever
274153469827350528 = yes, like that
```


## Commands
_(`*` means the user needs the `kick` role in the channel, `^` for owner)_

- `~countdown`: Time until next SU episode.
    + Will return a countdown.
- `~cn`: Get Cartoon Network's schedule
    + Ask using the date in this format: YYYY-MM-DD
- `~pick`: Pick an element, delimited by "or".
    + Example: `pizza or taco or burger`.
- `~howlong`: Get when you joined the server.
    + Add a name/mention as a parameter to know for someone else.
- `~bumps`: See how many times you bumped the server.
    + Getting successfully bumps from ServerHound increment your score.
- `~ping`: PONG!
    + Just to test if you're still there.
- `*` `~birthday`: Happy Birthday!
    + Toggle the birthday role, if available.
- `*` `~clean`: The bot deletes is own messages.
    + In case the bot went crazy...
- `*` `~nuke <n|50>`: Delete a number of messages. (`n` is optional)
    + Specify a number or it will clean the last 50 messages.
- `^` `~sleep`: Stops the bot.
    + But it might come back! (If you put it in a loop or something)
- `~help <command|category>`: Display the help message
