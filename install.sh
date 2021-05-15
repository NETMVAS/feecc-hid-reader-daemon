#!/bin/bash

sudo systemctl daemon-reload
sudo systemctl stop EventToInternet.service
sudo systemctl disable EventToInternet.service
sudo git pull --force
sudo cp -f /etc/systemd/system/EventToInternet/EventToInternet.service /etc/systemd/system/EventToInternet.service
sudo systemctl daemon-reload
sudo systemctl enable EventToInternet.service
sudo systemctl start EventToInternet.service
sudo systemctl status EventToInternet.service
