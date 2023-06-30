# NadeBot (Public / v1.4.9)



Discord open source bot for server [**&lt;Підвал Нейда>**](https://discord.gg/nadecgt)

[Українська версія](https://github.com/Beengoo/nade-bot/blob/master/README.md)

## Features
*This version is public and may differ substantially from the original on [server](https://discord.gg/nadecgt)*

### Commands
- `/alert` - The command is implemented on the basis of the API [alerts.com.ua](https://alerts.com.ua), all it does is send an airborne alarm map.
- `/dontpingme` - Configuration command for the function, when you ping the bot, it will respond with a random text (or a picture as a link).
- `/war-states` - Implemented on the basis of [russianwarship.rip](https://russianwarship.rip), it displays the number of losses of the russian army in Ukraine.
- `/help` - Bot commands list.
- `/top` - Top 50 rank leaders.
- `/cmgr` - Cogs manager command
- `/ctxmgr` - Context menu manage command (raw)
- `/exp` - Change the number of exp for server members.
- `/levelrole` - Set rewards for reaching a certain level.
- `/ytdl` - Download videos from YouTube
- `/lock_channel` and `/unlock_channel` - Lock channels for an individual role/member

### Functions
 
- `DontPingMe` - Sends a random text, picture or video (if configured in `/dontpingme`)
- `ChannelFilter` - (unfortunately, it can be configured only by the developer in the configuration files) Does not allow members in certain channels to send messages without links or attachments.
- `Rank` - A ranking system that also works in voice channels (partially configured in the configuration files)
- `Counting` - (currently in the migration phase, saved as a draft) Checks in a specific channel for iteration compliance.

## Instalation

1. Copy all the code using a method convenient for you (here we will use [git](https://git-scm.com/downloads) and also use Windows Powershell)
  ```bash
  cd Your_dir
  git clone https://github.com/Beengoo/nade-bot.git
  cd nade-bot-master
  ```
2. Go to the config.json file and insert your bot's token into the `botToken` value.
3. To access the developer commands (such as `/cmgr`), you need to insert your Discord account id into the `devIds` list.
4. Also **MUST** specify the id of the target guild (the bot is designed for one guild).
5. Now return to the command line and write the following commands (from the bot root directory)
  ```bash
  python -m venv venv
  .\venv\Scripts\activate.ps1
  pip install -r requirements.txt
  ```
6. Finally, we run the bot with the `python main.py` command!

## Help with setting up

If the bot fails to launch, the problem is most likely an incomplete bot configuration.

The settings of individual functionality are always located in the `assets/configs` folder for details, please contact `beengoo.ua` on the server [**Підвал Нейда**](https://discord.gg/nadecgt)


## in future

- Configuration command for ChannelFilter (currently only possible via configs)
