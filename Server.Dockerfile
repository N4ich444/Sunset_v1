# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/go/dockerfile-reference/

# Want to help us make this template better? Share your feedback here: https://forms.gle/ybq9Krt8jtBL3iCk7


ARG NODE_VERSION=26

# Nodejs is preinstalled in this alpine image, and npm install causes issues because it reads package.json and breaks, 
# because it thinks github is the npm database and 404s
FROM node:${NODE_VERSION}-alpine

# Use production node environment by default.
ENV NODE_ENV production

# Default working directory
WORKDIR /usr/src/app

# Adds openssl prerequesite for Foundry VTT
RUN apk add --no-cache openssl

# rsync for file sync
RUN apk add --no-cache rsync

# flock for mutexing shared directories
RUN apk add --no-cache flock

# Makes userdata folder that will be saved to volume
RUN mkdir -p userdata

# Makes data folder for sharedata if it doesn't exist to prevent rsync from erroring in a fresh install
RUN mkdir -p shareddata/Data/

# Enable write permissions
RUN chmod -R a+rw userdata

RUN chmod -R a+rw shareddata



# sync data directory add delete once up and running
#RUN rsync -a --quiet shareddata/Data userdata/Data

# Run the application as a non-root user.
USER node

# Copy the rest of the source files into the image.
COPY . .

# Expose the port that the application listens on.
EXPOSE 8080

# Bash script for shutdown
# replaced by cleanup service

# Run the application.
# copies group/default admin password in adminpass directory
# lock waits for 60 seconds before timing out
CMD cp adminpass/admin.txt userdata/Config/admin.txt; flock -w 60 shareddata/Data/ -c  "rsync -av --delete shareddata/Data/ userdata/Data/" ; node foundryapp/main.js --dataPath=userdata --port=8080




