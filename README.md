This is the Discord Bot that launches multiple licensed Foundry VTT instances designed for the Western Association of Roleplayers.
Version 4. Completely rewritten in Python instead of the old Spring Java setup for the bot. Docker files mostly remain the same with the addition of shadow copying.
Requires the NodeJS portable version of Foundry Virtual Tabletop. Rename that folder to foundryapp and place it in the folder alongside the Python scripts and Docker files.
Preset passcode is 'admin' in adminpass.

Packages required for this to work
Python on Whales
Discord.py
Docker

Volumes you need to create for this to work
userdata_fserv_backup
userdata_fserv_share
userdata_fserv_slot_(0-3)
