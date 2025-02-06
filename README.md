# Initial setup

Note: all of these scripts/shortcuts used by the tools assume the user is ```pi``` and the home dir would be ```/home/pi```

### 1) Clone the repo
```
cd ~
mkdir github

cd github
git clone https://github.com/ramdor/G2Tools
```

### 2) Run the setup and place the shortcuts on the Desktop
```
chmod +x ~/github/G2Tools/desktop/G2Tools_setup.sh
~/github/G2Tools/desktop/G2Tools_setup.sh
```

### Future updates to the repo
```
cd ~/github/G2Tools
git reset --hard HEAD
git pull
chmod +x ~/github/G2Tools/desktop/G2Tools_setup.sh
~/github/G2Tools/desktop/G2Tools_setup.sh
```
