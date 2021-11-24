# Li'l Butler
[![PEP8](https://img.shields.io/badge/code%20style-pep8-green.svg)](https://www.python.org/dev/peps/pep-0008/)

> _Oh, you're the butler who touches our hearts._
> "You people have too much money!"

Just a discord bot. It has some commands and it deletes links to other servers.


**NOTE FOR UPGRADES FROM `discord.py` TO `novus`:** Please run this to remove the previous libraries.
```
pip uninstall discord.py
pip uninstall discord-py-slash-command
```


## Requirements
- Python 3.8+
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
- `birthday`: list of `<server id> = <role id>` where the role id is a birthday role
- `joinlogs`: list of `<server id> = <channel id>` where joins/leaves/bans logs are going to be posted
- `msglogs`: list of `<server id> = <channel id>` where deleted message are logged
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

[savepics]
; channel id = path to folder/
274153487359672320 = /opt/archives/
```


## Commands
_(`*` means the user needs the `kick` role in the channel, `^` for owner)_

Use the slash commands or prepend everything with `lil!`

- `cn <YYYY-MM-DD>`: Get Cartoon Network's schedule
    + Ask schedule for a specific day.
- `pick`: Pick an element, delimited by ",".
    + Example: `pizza, taco, burger`.
- `howlong [@user]`: Get when you joined the server.
    + Add a name/mention as a parameter to know for someone else.
- `ping`: PONG!
    + Just to test if you're still there.
- `*` `birthday <@user>`: Happy Birthday!
    + Toggle the birthday role, if available.
- `*` `clean`: The bot deletes is own messages.
    + In case the bot went crazy...
- `*` `nuke <n|50>`: Delete a number of messages. (`n` is optional)
    + Specify a number or it will remove the last 50 messages.
- `^` `sleep`: Stops the bot.
    + But it might come back! (If you put it in a loop or something.)
- `~help <command|category>`: Display the help message
