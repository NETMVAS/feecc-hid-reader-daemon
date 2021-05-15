#!/bin/bash

sudo systemctl daemon-reload
sudo systemctl stop EventToInternet.service
sudo systemctl disable EventToInternet.service
sudo systemctl daemon-reload
