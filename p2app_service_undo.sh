#!/bin/bash

#MW0LGE (c)2025
#Covered by the GNU GENERAL PUBLIC LICENSE v2. See the LICENSE file

SERVICE_NAME="p2app"
SERVICE_PATH="/etc/systemd/system/$SERVICE_NAME.service"

echo "Checking if the service exists..."

# If the service exists, stop and disable it
if [ -f "$SERVICE_PATH" ]; then
    echo "Service file found. Stopping and disabling service..."
    sudo systemctl stop $SERVICE_NAME
    sudo systemctl disable $SERVICE_NAME
else
    echo "Service file does not exist. Nothing to stop or disable."
fi

# Remove the service file if it exists
if [ -f "$SERVICE_PATH" ]; then
    echo "Removing service file..."
    sudo rm $SERVICE_PATH
else
    echo "Service file already removed."
fi

echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "Checking if service still exists..."
if systemctl list-units --type=service | grep -q $SERVICE_NAME; then
    echo "Warning: The service may still be active!"
else
    echo "Service successfully removed."
fi

echo "Done!"
