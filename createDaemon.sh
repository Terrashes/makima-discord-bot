#!/bin/bash

touch /etc/systemd/system/Makima-Bot.service

cat > /etc/systemd/system/Makima-Bot.service <<EOF 
[Unit]
Description="Best bot 4ever!"

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/Makima-Bot
VIRTUAL_ENV=/home/ubuntu/Makima-Bot/venv
Environment=PATH=$VIRTUAL_ENV/bin:$PATH
ExecStart=/home/ubuntu/Makima-Bot/venv/bin/python main.py

[Install]
WantedBy=multi-user.target
EOF


python3 -m venv venv
python3 -m venv venv
./venv/bin/python -m pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

systemctl daemon-reload
systemctl start Makima-Bot.service
systemctl enable Makima-Bot.service
systemctl status Makima-Bot.service