This is the Discord Bot that launches multiple licensed Foundry VTT instances designed for the Western Association of Roleplayers club at the University of Western Ontario.
Completely rewritten in Python instead of the old Spring Java setup for the bot. Docker files mostly remain the same with the addition of shadow copying.
Requires the NodeJS portable version of Foundry Virtual Tabletop. Rename that folder to foundryapp and place it in the folder alongside the Python scripts and Docker files.
Preset passcode is 'admin' in adminpass. Passcodes can be created by downloading the admin.txt on a live docker container

Packages required for this to work:
- Python on Whales
- Discord.py
- Docker

Docker Volumes you need to create for this to work:

- userdata_fserv_backup
- userdata_fserv_share
- userdata_fserv_slot_(0-3)

Files you need to create:

- token.txt - discord bot token
- url.txt - url
- port.txt - first port in range
- admin_user.txt - discord id of user
- channelID.txt - channel id of bot channel

