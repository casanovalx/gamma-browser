#!/usr/bin/bash

echo 'Moving browser executable to /etc...'\ && sudo cp -r etc / && echo 'Moving browser files to /usr...'\ && sudo cp -r usr / && cd usr/bin && echo "Moving config files..."\ && mkdir /home/$USER/.config/gamma-browser && mv config.json /home/$USER/.config/gamma-browser && mv bookmarks.json /home/$USER/.config/gamma-browser && mv history.json /home/$USER/.config/gamma-browser && sudo update-desktop-database /usr/share/applications && echo "Done. Please restart the system."
