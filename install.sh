#!/bin/bash

sudo cp -fv EventToInternet.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable EventToInternet.service
sudo systemctl start EventToInternet.service
sudo systemctl status EventToInternet.service
