#MW0LGE (c)2025
#Covered by the GNU GENERAL PUBLIC LICENSE v2. See the LICENSE file

import tkinter as tk
import subprocess
import os

LOCK_FILE = "/tmp/g2_helper_terminal_lock"
SCRIPT_FILE = "/tmp/g2_helper_script.sh"

root = tk.Tk()

####################
# Scripts
####################

UPDATE_REPOS = r"""
mkdir -p ~/github
cd ~/github

if [ ! -d "Saturn/.git" ]; then
    rm -rf Saturn  # Remove in case it's an incomplete clone
    git clone https://github.com/laurencebarker/Saturn
else
    cd Saturn && git pull
fi

cd ~/github

if [ ! -d "pihpsdr/.git" ]; then
    rm -rf pihpsdr  # Remove in case it's an incomplete clone
    git clone https://github.com/dl1ycf/pihpsdr
else
    cd pihpsdr && git pull
fi
"""

INSTALL_LIBS = r"""
~/github/Saturn/scripts/install-libraries.sh
sudo apt-get install -y gpiod libgpiod-doc
sudo apt-get install -y libgtk-3-dev
"""

BUILD_XDMA = r"""
sudo apt install -y raspberrypi-kernel-headers
sudo rmmod -s xdma
cd ~/github/Saturn/linuxdriver/xdma
make
sudo make install
sudo modprobe xdma
sudo cp ~/github/Saturn/linuxdriver/etc/udev/rules.d/60-xdma.rules /etc/udev/rules.d/
sudo cp ~/github/Saturn/linuxdriver/etc/udev/rules.d/xdma-udev-command.sh /etc/udev/rules.d/
sudo chmod +x /etc/udev/rules.d/xdma-udev-command.sh
sudo udevadm control --reload-rules
sudo udevadm trigger
"""

MAKE_G2 = r"""
~/github/Saturn/scripts/update-desktop-apps.sh
~/github/Saturn/scripts/update-p2app.sh
"""

MAKE_PIHPSDR = r"""
cd ~/github/pihpsdr
make clean
make
"""

COPY_DESKTOP_ICONS = r"""
cp ~/github/Saturn/desktop/* ~/Desktop
echo Desktop icons copied.
"""

DESKTOP_AUTOSTART_FP = r"""
sudo cp ~/github/Saturn/scripts/front-panel-autostart /etc/xdg/lxsession/LXDE-pi/autostart
sudo chmod 644 /etc/xdg/lxsession/LXDE-pi/autostart
echo "Desktop Autostart front panel file copied successfully."
"""
DESKTOP_AUTOSTART_NFP = r"""
sudo cp ~/github/Saturn/scripts/no-front-panel-autostart /etc/xdg/lxsession/LXDE-pi/autostart
sudo chmod 644 /etc/xdg/lxsession/LXDE-pi/autostart
echo "Desktop Autostart no front panel file copied successfully."
"""
DESKTOP_AUTOSTART_DISABLE = r"""
sudo cp ~/github/G2Tools/no-p2app-piHPSDR-autostart /etc/xdg/lxsession/LXDE-pi/autostart
sudo chmod 644 /etc/xdg/lxsession/LXDE-pi/autostart
echo "Desktop Autostart disabled."
"""

P2APP_SERVICE = r"""
sudo ~/github/G2Tools/p2app_service.sh
"""

P2APP_SERVICE_DISABLE = r"""
sudo ~/github/G2Tools/p2app_service_undo.sh
"""

G2_CONFIG_TXT = r"""
[ -d "/boot/firmware" ] && sudo cp ~/github/G2Tools/G2_config.txt /boot/firmware/config.txt || sudo cp ~/github/G2Tools/G2_config.txt /boot/config.txt
echo Installed G2 config.txt
"""

G27_CONFIG_TXT = r"""
[ -d "/boot/firmware" ] && sudo cp ~/github/G2Tools/G27_config.txt /boot/firmware/config.txt || sudo cp ~/github/G2Tools/G27_config.txt /boot/config.txt
echo Install G2 7 inch screen config.txt
"""

G2U8_CONFIG_TXT = r"""
[ -d "/boot/firmware" ] && sudo cp ~/github/G2Tools/G2U8_config.txt /boot/firmware/config.txt || sudo cp ~/github/G2Tools/G2U8_config.txt /boot/config.txt
echo Install G2 Ultra 8 inch screen config.txt
"""

PIHPSDR_LIBS = r"""
cd ~/github/pihpsdr
./LINUX/libinstall.sh
"""

RECENT_FW = r"""
~/github/Saturn/scripts/find-bin.sh
echo ""
echo "FPGA Update Instructions:"
echo "1. If FPGA needs updating, launch flashwriter desktop app (icon on desktop)"
echo "2. Navigate: Open file → Home → github → Saturn → FPGA"
echo "3. Select the new .BIT file listed above"
echo "4. Ensure 'primary' is selected"
echo "5. Click 'Program'"
echo ""
echo "Note: Programming takes approximately 3 minutes"
echo "Important: Power cycle completely after programming"
"""

PERFORMANCE = r"""
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor > /dev/null
sudo cp ~/github/G2Tools/99-performance-governor.rules /etc/udev/rules.d
sudo udevadm control --reload-rules && sudo udevadm trigger
echo Performance mode now enabled. CPU ondemand changed to performance
"""

G2_RULES = r"""
cd ~/github/Saturn/rules
./install-rules.sh
echo Rules now installed
"""

####################
# Script execution
####################

def disable_ui():
    print("Disabling UI...")
    for widget in frame.winfo_children():  # Iterate over the frame's children
        if isinstance(widget, tk.Button):
            widget.config(state=tk.DISABLED)

def enable_ui():
    print("Enabling UI...")
    for widget in frame.winfo_children():  # Iterate over the frame's children
        if isinstance(widget, tk.Button):
            widget.config(state=tk.NORMAL)

def check_lock_file():
    """ Poll for /tmp/terminal_lock. If it no longer exists, re-enable UI. """
    if os.path.exists(LOCK_FILE):
        root.after(300, check_lock_file)
    else:
        enable_ui()

def run_command_in_terminal(command):
    if os.path.exists(LOCK_FILE):
        print("Removing stale lock file...")
        os.remove(LOCK_FILE)

    print("Creating lock file in Python...")
    with open(LOCK_FILE, "w") as lf:
        lf.write("locked")

    disable_ui()

    script_contents = f"""
echo
echo Script starting.... DO NOT X this window. Wait for it to finish and press a key as instructed.
echo
{command}
echo
echo 'Press any key to close window...'
read -n 1
rm {LOCK_FILE}
"""
    with open(SCRIPT_FILE, "w") as f:
        f.write(script_contents)

    os.chmod(SCRIPT_FILE, 0o755)
    print(f"Wrote script to {SCRIPT_FILE}")

    try:
        subprocess.Popen(["lxterminal", "-e", f"bash {SCRIPT_FILE}"])
    except FileNotFoundError as e:
        print("Could not launch lxterminal. Error:", e)
        enable_ui()
        return

    check_lock_file()

####################
# Button clicks
####################

def update_github_repos():
    print("Update button was clicked.")
    run_command_in_terminal(UPDATE_REPOS)

def install_libs():
    print("Install Libs button was clicked.")
    run_command_in_terminal(INSTALL_LIBS)

def build_install_xdma():
    print("Build & Install XDMA button was clicked.")
    run_command_in_terminal(BUILD_XDMA)

def make_all_g2():
    print("Make All G2 Apps button was clicked.")
    run_command_in_terminal(MAKE_G2 + G2_RULES)

def make_pihpsdr():
    print("Make piHPSDR button was clicked.")
    run_command_in_terminal(MAKE_PIHPSDR)

def copy_desktop_icons():
    print("Copy Desktop Items button was clicked.")
    run_command_in_terminal(COPY_DESKTOP_ICONS)

def autostart_fp():
    print("Autostart FP button was clicked.")
    run_command_in_terminal(P2APP_SERVICE_DISABLE + DESKTOP_AUTOSTART_FP)

def autostart_nfp():
    print("Autostart NFP button was clicked.")
    run_command_in_terminal(P2APP_SERVICE_DISABLE + DESKTOP_AUTOSTART_NFP)

def p2app_service():
    print("PS2App as serivce button was clicked.")
    run_command_in_terminal(DESKTOP_AUTOSTART_DISABLE + P2APP_SERVICE)

def g2_config():
    print("G2 config.txt button was clicked.")
    run_command_in_terminal(G2_CONFIG_TXT)

def g27_config():
    print("G2 7\" config.txt button was clicked.")
    run_command_in_terminal(G27_CONFIG_TXT)

def g2u8_config():
    print("G2 Ultra 8\" config.txt button was clicked.")
    run_command_in_terminal(G2U8_CONFIG_TXT)

def install_pihpsdr_libs():
    print("Install piHPSDR libs button was clicked.")
    run_command_in_terminal(PIHPSDR_LIBS)

def recent_fw():
    print("Recent firmware button was clicked.")
    run_command_in_terminal(RECENT_FW)
    
def performance():
    print("Performance button was clicked.")
    run_command_in_terminal(PERFORMANCE)

####################
# Main form/display
####################

root.title("G2 Helper - MW0LGE")
root.geometry("680x544")  # Increased height to fit new button
root.resizable(False, False)

# Warning Label
warning_label = tk.Label(
    root,
    text="⚠️ DO NOT click X on a console window. Wait for the process to finish and the\n'Press any key to close window...' prompt to show.",
    fg="red",
    font=("Arial", 10, "bold"),
    justify="center"
)
warning_label.pack(pady=10)

# Adjust button width to fit two columns
button_config = {"width": 32, "height": 2, "font": ("Arial", 14)}

# Create a frame for layout
frame = tk.Frame(root)
frame.pack()

# Place buttons in a two-column grid
buttons = [
    ("Update G2 & piHPSDR GitHub Repos", update_github_repos),
    ("Install Libraries", install_libs),
    ("Build & Install XDMA Drivers", build_install_xdma),
    ("Make All G2 Apps + Rules", make_all_g2),
    ("Install piHPSDR Libraries", install_pihpsdr_libs),
    ("Make piHPSDR", make_pihpsdr),
    ("Copy Desktop Icons", copy_desktop_icons),
    ("AutoStart Front Panel (piHPSDR)", autostart_fp),
    ("AutoStart No Front Panel (p2app)", autostart_nfp),
    ("P2App as a Service", p2app_service),
    ("Install G2 config.txt", g2_config),
    ("Install G2 7\" config.txt", g27_config),
    ("Install G2 Ultra 8\" config.txt", g2u8_config),
    ("Show most recent firmware", recent_fw),
    ("Enable CPU Performance mode", performance),
]

# Create and place buttons in two columns
for index, (text, command) in enumerate(buttons):
    row = index // 2  # Row index
    col = index % 2   # Column index
    tk.Button(frame, text=text, command=command, **button_config).grid(row=row, column=col, padx=5, pady=2)

# Ensure columns expand evenly
frame.columnconfigure(0, weight=1)
frame.columnconfigure(1, weight=1)

root.mainloop()
