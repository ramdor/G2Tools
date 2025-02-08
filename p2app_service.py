#MW0LGE (c)2025
#Covered by the GNU GENERAL PUBLIC LICENSE v2. See the LICENSE file

import tkinter as tk
import subprocess
import os

SERVICE_FILE = "/etc/systemd/system/p2app.service"

def stop_service():
    subprocess.run(["sudo", "systemctl", "stop", "p2app.service"])
    root.after(2000, check_service)  # Re-check state after stopping

def start_service():
    subprocess.run(["sudo", "systemctl", "start", "p2app.service"])
    root.after(2000, check_service)  # Re-check state after starting

def restart_service():
    global check_after_id
    status_label.config(text="Restarting...", fg="red")
    subprocess.run(["sudo", "systemctl", "restart", "p2app.service"])
    if check_after_id:
        root.after_cancel(check_after_id)
    root.after(2000, check_service)  # Re-check state after restart

def enable_autostart():
    subprocess.run(["sudo", "systemctl", "enable", "p2app.service"])
    root.after(2000, check_autostart)

def disable_autostart():
    subprocess.run(["sudo", "systemctl", "disable", "p2app.service"])
    root.after(2000, check_autostart)

def check_service():
    global check_after_id

    status = subprocess.run(["systemctl", "is-active", "p2app.service"], capture_output=True, text=True).stdout.strip()

    if status == "active":
        status_label.config(text="Service is running", fg="green")
        start_btn.config(state="disabled")
        stop_btn.config(state="normal")
        restart_btn.config(state="normal")
    else:
        status_label.config(text="Service is stopped", fg="red")
        start_btn.config(state="normal")
        stop_btn.config(state="disabled")
        restart_btn.config(state="disabled")

    check_execstart()

    check_after_id = root.after(1000, check_service)

def check_autostart():
    status = subprocess.run(["systemctl", "is-enabled", "p2app.service"], capture_output=True, text=True).stdout.strip()
    if status == "enabled":
        autostart_status_label.config(text="p2app autostart Enabled", fg="green")
        enable_autostart_btn.config(state="disabled")
        disable_autostart_btn.config(state="normal")
    else:
        autostart_status_label.config(text="p2app autostart Disabled", fg="red")
        enable_autostart_btn.config(state="normal")
        disable_autostart_btn.config(state="disabled")

def check_execstart():
    """Check if G2 Panel Support (-p) is enabled in ExecStart."""
    with open(SERVICE_FILE, "r") as file:
        lines = file.readlines()

    for line in lines:
        if line.strip() == "ExecStart=/home/pi/github/Saturn/sw_projects/P2_app/p2app -p":
            execstart_status_label.config(text="G2 Panel Support Enabled", fg="green")
            return
        elif line.strip() == "ExecStart=/home/pi/github/Saturn/sw_projects/P2_app/p2app":
            execstart_status_label.config(text="G2 Panel Support Disabled", fg="red")
            return

def toggle_execstart():
    """Toggle between ExecStart with and without -p, using sudo for permissions."""
    temp_file = "/tmp/p2app.service"  # Temporary file to edit content

    # Read the original file with sudo
    result = subprocess.run(["sudo", "cat", SERVICE_FILE], capture_output=True, text=True)
    lines = result.stdout.splitlines()

    new_lines = []
    for line in lines:
        if line.strip() == "ExecStart=/home/pi/github/Saturn/sw_projects/P2_app/p2app -p":
            new_lines.append("#" + line)  # Comment out -p version
        elif line.strip() == "#ExecStart=/home/pi/github/Saturn/sw_projects/P2_app/p2app":
            new_lines.append(line[1:])  # Uncomment normal version
        elif line.strip() == "ExecStart=/home/pi/github/Saturn/sw_projects/P2_app/p2app":
            new_lines.append("#" + line)  # Comment out normal version
        elif line.strip() == "#ExecStart=/home/pi/github/Saturn/sw_projects/P2_app/p2app -p":
            new_lines.append(line[1:])  # Uncomment -p version
        else:
            new_lines.append(line)

    # Write new content to a temporary file
    with open(temp_file, "w") as file:
        file.write("\n".join(new_lines) + "\n")

    # Overwrite the system file using sudo tee
    subprocess.run(["sudo", "tee", SERVICE_FILE], input="\n".join(new_lines), text=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Reload systemd to apply changes
    subprocess.run(["sudo", "systemctl", "daemon-reload"])

    # Re-check state after 2 seconds
    root.after(2000, check_execstart)


root = tk.Tk()
root.title("MW0LGE")
root.geometry("320x460+200+200")
root.resizable(False, False)

button_config = {"width": 20, "height": 2, "font": ("Arial", 16)}

stop_btn = tk.Button(root, text="Stop p2app Service", command=stop_service, **button_config)
stop_btn.pack()

start_btn = tk.Button(root, text="Start p2app Service", command=start_service, **button_config)
start_btn.pack()

restart_btn = tk.Button(root, text="Restart p2app Service", command=restart_service, **button_config)
restart_btn.pack()

status_label = tk.Label(root, text="Checking service...", font=("Arial", 12))
status_label.pack()

enable_autostart_btn = tk.Button(root, text="Enable service autostart", command=enable_autostart, **button_config)
enable_autostart_btn.pack()

disable_autostart_btn = tk.Button(root, text="Disable service autostart", command=disable_autostart, **button_config)
disable_autostart_btn.pack()

autostart_status_label = tk.Label(root, text="Checking autostart...", font=("Arial", 12))
autostart_status_label.pack()

toggle_execstart_btn = tk.Button(root, text="Toggle G2 Panel Support", command=toggle_execstart, **button_config)
toggle_execstart_btn.pack()

execstart_status_label = tk.Label(root, text="Checking G2 Panel Support...", font=("Arial", 12))
execstart_status_label.pack()

check_after_id = None

if not os.path.exists(SERVICE_FILE):
    status_label.config(text="Service not installed", fg="red")
    autostart_status_label.config(text="Service not installed", fg="red")
    execstart_status_label.config(text="Service not installed", fg="red")
    for btn in [start_btn, stop_btn, restart_btn, enable_autostart_btn, disable_autostart_btn, toggle_execstart_btn]:
        btn.config(state="disabled")
else:
   check_service()
   check_autostart()
   check_execstart()

root.mainloop()
