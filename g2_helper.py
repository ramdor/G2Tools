import tkinter as tk
import subprocess
import os

root = tk.Tk()
root.title("G2 Helper - MW0LGE")
root.geometry("380x500")  # Increased height to fit new button
root.resizable(False, False)

LOCK_FILE = "/tmp/terminal_lock"
SCRIPT_FILE = "/tmp/g2_helper_script.sh"

UPDATE_COMMAND = r"""
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

INSTALL_LIBS_COMMAND = r"""
~/github/Saturn/scripts/install-libraries.sh

sudo apt-get install -y gpiod libgpiod-doc
sudo apt-get install -y libgtk-3-dev
"""

BUILD_XDMA_COMMAND = r"""
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

MAKE_G2_COMMAND = r"""
~/github/Saturn/scripts/update-desktop-apps.sh
~/github/Saturn/scripts/update-p2app.sh
"""

MAKE_PIHPSDR_COMMAND = r"""
cd ~/github/pihpsdr
make clean
make
"""

COPY_DESKTOP_ICONS_COMMAND = r"""
cp ~/github/Saturn/desktop/* ~/Desktop
echo Desktop icons copied.
"""

def disable_ui():
    print("Disabling UI...")
    for widget in root.winfo_children():
        if isinstance(widget, tk.Button):
            widget.config(state=tk.DISABLED)

def enable_ui():
    print("Enabling UI...")
    for widget in root.winfo_children():
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

    script_contents = f"""\
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

def update_github_repos():
    print("Update button was clicked.")
    run_command_in_terminal(UPDATE_COMMAND)

def install_libs():
    print("Install Libs button was clicked.")
    run_command_in_terminal(INSTALL_LIBS_COMMAND)

def build_install_xdma():
    print("Build & Install XDMA button was clicked.")
    run_command_in_terminal(BUILD_XDMA_COMMAND)

def make_all_g2():
    print("Make All G2 Apps button was clicked.")
    run_command_in_terminal(MAKE_G2_COMMAND)

def make_pihpsdr():
    print("Make piHPSDR button was clicked.")
    run_command_in_terminal(MAKE_PIHPSDR_COMMAND)

def copy_desktop_icons():
    print("Copy Desktop Items button was clicked.")
    run_command_in_terminal(COPY_DESKTOP_ICONS_COMMAND)


button1 = tk.Button(root, text="Update G2 & piHPSDR GitHub Repos", command=update_github_repos)
button1.pack(pady=20)

button2 = tk.Button(root, text="Install Libraries", command=install_libs)
button2.pack(pady=20)

button3 = tk.Button(root, text="Build & Install XDMA Drivers", command=build_install_xdma)
button3.pack(pady=20)

button4 = tk.Button(root, text="Make All G2 Apps", command=make_all_g2)
button4.pack(pady=20)

button5 = tk.Button(root, text="Make piHPSDR", command=make_pihpsdr)
button5.pack(pady=20)

button6 = tk.Button(root, text="Copy Desktop Icons", command=copy_desktop_icons)
button6.pack(pady=20)

root.mainloop()
