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

force_mode=""

write_desktop_entry() {
    local target_path="$1"
    local owner_name="${2:-}"

    mkdir -p "$(dirname "$target_path")"

    cat > "$target_path" <<'EOF'
[Desktop Entry]
Name=Power Key Inhibit
Comment=Inhibit the power key while desktop runs
Exec=systemd-inhibit --what=handle-power-key gtk-nop
Terminal=false
Type=Application
NoDisplay=true
EOF

    chmod 644 "$target_path"

    if [ -n "$owner_name" ]; then
        chown "$owner_name:$owner_name" "$target_path"
    fi
}

set_popup_state() {
    local target_state="$1"

    if [ "$target_state" = "enable" ]; then
        rm -f "$system_disabled" "$user_disabled"
        write_desktop_entry "$system_file"
        write_desktop_entry "$user_file" "$real_user"
        echo "Popup Enabled - reboot to take effect."
    else
        rm -f "$system_file" "$user_file"
        write_desktop_entry "$system_disabled"
        write_desktop_entry "$user_disabled" "$real_user"
        echo "Popup Disabled - reboot to take effect."
    fi
}

popup_enabled=false
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
    set_popup_state "$force_mode"
    exit 0
fi

if [ "$popup_enabled" = true ]; then
    set_popup_state "disable"
else
    set_popup_state "enable"
fi
