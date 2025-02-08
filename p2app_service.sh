#!/bin/bash

#MW0LGE (c)2025
#Covered by the GNU GENERAL PUBLIC LICENSE v2. See the LICENSE file

SERVICE_NAME="p2app"
SERVICE_PATH="/etc/systemd/system/$SERVICE_NAME.service"

echo "Checking for existing service..."

# If the service exists, stop it before making changes
if [ -f "$SERVICE_PATH" ]; then
    echo "Service file exists. Stopping service before updating..."
    sudo systemctl stop $SERVICE_NAME
else
    echo "Service file does not exist. Creating it..."
fi

echo "Writing service file..."
sudo tee $SERVICE_PATH > /dev/null <<EOL
[Unit]
Description=$SERVICE_NAME
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
#ExecStart=/home/pi/github/Saturn/sw_projects/P2_app/p2app -p
ExecStart=/home/pi/github/Saturn/sw_projects/P2_app/p2app
Restart=always
User=pi
Group=pi
WorkingDirectory=/home/pi/github/Saturn/sw_projects/P2_app
StandardOutput=null
StandardError=null
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
Environment="LD_LIBRARY_PATH=/usr/local/lib:/usr/lib:/lib"

[Install]
WantedBy=multi-user.target
EOL

echo "Setting correct permissions..."
sudo chmod 644 $SERVICE_PATH
sudo chown root:root $SERVICE_PATH

echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "Enabling the $SERVICE_NAME service to start at boot..."
sudo systemctl enable $SERVICE_NAME

echo "Starting the $SERVICE_NAME service..."
sudo systemctl start $SERVICE_NAME

echo "Done! Service is now running."
