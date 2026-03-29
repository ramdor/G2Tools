#!/bin/bash

set -e

if [ "$(id -u)" -ne 0 ]; then
    exec sudo "$0" "$@"
fi

real_user="${SUDO_USER:-$USER}"
user_home="$(getent passwd "$real_user" | cut -d: -f6)"

system_file="/etc/xdg/autostart/pwrkey.desktop"
system_disabled="/etc/xdg/autostart/pwrkey.desktop.disabled"
user_file="$user_home/.config/autostart/pwrkey.desktop"
user_disabled="$user_home/.config/autostart/pwrkey.desktop.disabled"

popup_enabled=false
force_mode=""

if [ -f "$system_file" ] || [ -f "$user_file" ]; then
    popup_enabled=true
fi

if [ $# -ge 1 ]; then
    case "$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]')" in
        enable|on|true|1)
            force_mode="enable"
            ;;
        disable|off|false|0)
            force_mode="disable"
            ;;
        *)
            echo "Usage: $0 [enable|disable]"
            exit 1
            ;;
    esac
fi

if [ -n "$force_mode" ]; then
    if [ "$force_mode" = "enable" ]; then
        changed=false

        if [ -f "$system_disabled" ]; then
            mv "$system_disabled" "$system_file"
            changed=true
        fi

        if [ -f "$user_disabled" ]; then
            mkdir -p "$user_home/.config/autostart"
            mv "$user_disabled" "$user_file"
            changed=true
        fi

        if [ -f "$system_file" ] || [ -f "$user_file" ]; then
            echo "Popup Enabled - reboot to take effect."
        else
            if [ "$changed" = true ]; then
                echo "Popup Enabled - reboot to take effect."
            else
                echo "No pwrkey.desktop.disabled files found in either location."
            fi
        fi
    else
        changed=false

        if [ -f "$system_file" ]; then
            mv "$system_file" "$system_disabled"
            changed=true
        fi

        if [ -f "$user_file" ]; then
            mv "$user_file" "$user_disabled"
            changed=true
        fi

        if [ -f "$system_disabled" ] || [ -f "$user_disabled" ]; then
            echo "Popup Disabled - reboot to take effect."
        else
            if [ "$changed" = true ]; then
                echo "Popup Disabled - reboot to take effect."
            else
                echo "No pwrkey.desktop files found in either location."
            fi
        fi
    fi

    exit 0
fi

if [ "$popup_enabled" = true ]; then
    if [ -f "$system_file" ]; then
        mv "$system_file" "$system_disabled"
    fi

    if [ -f "$user_file" ]; then
        mv "$user_file" "$user_disabled"
    fi

    echo "Popup Disabled - reboot to take effect."
else
    changed=false

    if [ -f "$system_disabled" ]; then
        mv "$system_disabled" "$system_file"
        changed=true
    fi

    if [ -f "$user_disabled" ]; then
        mkdir -p "$user_home/.config/autostart"
        mv "$user_disabled" "$user_file"
        changed=true
    fi

    if [ "$changed" = true ]; then
        echo "Popup Enabled - reboot to take effect."
    else
        echo "No pwrkey.desktop or pwrkey.desktop.disabled files found in either location."
    fi
fi
