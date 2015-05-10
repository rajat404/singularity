#!/bin/sh
LIST_OF_APPS_NONSTANDARD="mongodb-org"
echo 'deb http://downloads-distro.mongodb.org/repo/debian-sysvinit dist 10gen' | sudo tee /etc/apt/sources.list.d/mongodb.list
apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10
apt-get update
apt-get install -y $LIST_OF_APPS_NONSTANDARD
