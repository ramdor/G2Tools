# MW0LGE (c)2025
# You may distribute/copy this to your heart's content

import tkinter as tk
from tkinter import messagebox
import os

CONFIG_FILES = ["/boot/firmware/config.txt", "/boot/config.txt"]

# Overclock profiles
overclock_profiles = {
    "No Overclock": (1500, 0),
    "Mid Overclock": (1750, 2),
    "High Overclock": (2000, 6),
    "Extreme Overclock (not recommended)": (2200, 6)
}

def apply_overclock(profile):
    """Applies the selected overclock settings after confirmation (except for 'No Overclock')."""
    arm_freq, over_voltage = overclock_profiles[profile]

    # Skip confirmation if "No Overclock" is selected
    if profile != "No Overclock":
        confirmation_message = (
            f"You have selected: {profile}\n\n"
            "This will apply the following settings:\n"
            f" - arm_freq={arm_freq}\n"
            f" - over_voltage={over_voltage}\n\n"
        )

        details_message = (
            "Overclocking can cause instability, crashes, and potential damage to your hardware.\n"
            "Only proceed if you understand the risks.\n\n"
            "If you radio fails to boot, then you will need to remove the micro sd card "
            "and edit it on another machine with an sd card reader. You need to comment "
            "out the [arm_freq] and [over_voltage] lines using a '#'. These settings are "
            "stored in the config.txt file which should be in the boot/bootfs partition. " 
            "Make the changes, and save. Safely eject the sd card and replace into your radio.\n\n"
            "Do you want to continue?"
        )

        if not messagebox.askokcancel("Confirm Overclock", confirmation_message, detail=details_message, icon="warning"):
            return  # User canceled, do nothing

    try:
        # Determine which config file exists
        CONFIG_FILE = next((f for f in CONFIG_FILES if os.path.exists(f)), CONFIG_FILES[-1])

        # Read current config.txt
        with open(CONFIG_FILE, "r") as file:
            lines = file.readlines()

        new_lines = []
        found_arm_freq = False
        found_over_voltage = False
        
        for line in lines:
            if "arm_freq=" in line:
                if not found_arm_freq:
                    new_lines.append(f"arm_freq={arm_freq}\n")
                    found_arm_freq = True
                continue
            elif "over_voltage=" in line:
                if not found_over_voltage:
                    new_lines.append(f"over_voltage={over_voltage}\n")
                    found_over_voltage = True
                continue
            else:
                new_lines.append(line)
        
        # Ensure settings exist, otherwise append
        if not found_arm_freq:
            new_lines.append(f"arm_freq={arm_freq}\n")
        if not found_over_voltage:
            new_lines.append(f"over_voltage={over_voltage}\n")

        # Write back to config.txt
        with open(CONFIG_FILE, "w") as file:
            file.writelines(new_lines)

        messagebox.showinfo("Success", f"Overclock set to: {profile}\nReboot required!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to update config.txt\n{e}")

def create_gui():
    """Creates the GUI for selecting an overclock profile."""
    root = tk.Tk()
    root.title("Overclock Settings")
    root.geometry("350x260")
    root.resizable(False, False)

    # Instruction label
    tk.Label(root, text="Select Overclock Level:", font=("TkDefaultFont", 10)).pack(pady=5)

    # Create buttons with labels above each
    for profile, (arm_freq, over_voltage) in overclock_profiles.items():
        tk.Label(root, text=f"arm_freq={arm_freq} | over_voltage={over_voltage}", fg="black", font=("TkDefaultFont", 8)).pack()
        tk.Button(root, text=profile, command=lambda p=profile: apply_overclock(p)).pack(fill=tk.X, pady=5, padx=10)

    root.mainloop()

if __name__ == "__main__":
    if os.geteuid() != 0:
        messagebox.showerror("Error", "This program must be run as root!")
    else:
        create_gui()
