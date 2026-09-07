# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/go/dockerfile-reference/

# Want to help us make this template better? Share your feedback here: https://forms.gle/ybq9Krt8jtBL3iCk7

#execute this after docker compose down


#cleanup file does not require nodejs
FROM alpine:latest

# Use production node environment by default.
ENV NODE_ENV production

# Default working directory
WORKDIR /usr/src/app

RUN apk add --no-cache rsync

RUN apk add --no-cache flock

# Makes userdata folder that will be saved to volume
RUN mkdir -p userdata

# Makes share folder that will have file sync commands executed on the start and end of the program
RUN mkdir -p shareddata

# Makes share folder that will have file sync commands executed on the start and end of the program
RUN mkdir -p backupdata

# prevents errors on a fresh docker volume
RUN mkdir -p backupdata/Data/

# Enable write permissions
RUN chmod -R a+rw userdata

RUN chmod -R a+rw shareddata

RUN chmod -R a+rw backupdata

# sync data without deleting new worlds or addons etc
# then removes any admin password that anyone might've set so that nobody is locked out of the server panel
# encourage use of passwords in campaign instead
# restore from shadow copy backup still needs to be implemented, as of now it's just there so that if there is any data loss
# manual intervention can restore in future
# deletes will have to call a sysadmin
CMD flock -w 60 backupdata/Data/ -c "rsync -a userdata/Data/ backupdata/Data/" ; flock -w 60 shareddata/Data/ -c "rsync -av  --delete --filter='protect worlds/*/' --filter='protect modules/*/' --filter='protect systems/*/' --filter='protect assets/*/' userdata/Data/ shareddata/Data/"  ; rm userdata/Config/admin.txt






