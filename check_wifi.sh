#!/bin/bash

# WiFi network name (SSID)
WIFI_SSID="SpectrumSetup-28"

# Ping address to verify internet connection (Google's DNS server)
PING_ADDRESS="8.8.8.8"

IWGETID_CMD="/sbin/iwgetid"
PING_CMD="/bin/ping"

# Function to check if Wi-Fi is connected
check_wifi() {
    if $IWGETID_CMD -r | grep -q "$WIFI_SSID"; then
        return 0
    else
        return 1
    fi
}

# Function to check if internet connection is available
check_internet() {
    if $PING_CMD -q -c 1 -W 1 "$PING_ADDRESS" > /dev/null; then
        return 0
    else
        return 1
    fi
}

echo "Checking Wi-Fi connection to $WIFI_SSID..."

# Loop until Wi-Fi is connected
until check_wifi; do
    echo "Wi-Fi not connected. Retrying..."
    sleep 60
done

echo "Wi-Fi connected to $WIFI_SSID."

echo "Checking internet connection..."

# Loop until internet connection is available
until check_internet; do
    echo "Internet not available. Retrying..."
    sleep 60
done

echo "Internet connection verified. Script complete."
