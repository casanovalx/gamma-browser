# Gamma Browser

Browser written in PyQt (before)/PySide and utilizing QtWebEngine

Installation:

### Arch Linux:

Install PySide6 and QtWebEngine:

```
sudo pacman -S pyside6 python-pyqt6-webengine
```

Copy the repository to your system and enter the directory:

```
git clone https://github.com/casanovalx/gamma-browser.git && cd gamma-browser
```
Start the shell script in the folder:

```
./install.sh
```

After copying is over, restart the system.

### Fedora 41 and newer:

Install PySide6 and QtWebEngine:

```
sudo dnf5 install python3-pyside6 python-pyqt6-webengine
```

Copy the repository to your system and enter the directory:

```
git clone https://github.com/casanovalx/gamma-browser
```

Start the shell script in the folder:

```
./install.sh
```

## FAQ

1. Why there's no more Ubuntu releases?

Very simple: Ubuntu updates it's packages much slower, and I won't recommend you compiling PySide6 and QtWebEngine via pip or source code.

2. The shell script won't work. What to do?

Make the shell script executable. To do so, open the terminal in the directory you copied and write:

```
sudo chmod +x install.sh
```

And then, start it again.

3. Will there be an AUR/Copr repository?

No idea. I never looked it as an opportunity.
