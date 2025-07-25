# Automatic KU Leuven VPN login

Once logged in to toledo, the script calls all the nessecary steps to log into the KU Leuven VPN in order to be able to use software like siemens NX off campus.

## Installation

### Files

Only windows installations have been tested.

Two .exe files are provided, one for settings (vpn_kul_settings.exe), and one for actually running the automation of VPN login (vpn_kul.exe). Ivanti secure access should already be installed.

There is also a **vpn_config.json file and an .env that need to stay together with the .exe files.** So it is best to make a shortcut to the files on your desktop.

### Setup

To use the vpn_kul file, you need to **provide your login**, r-number and password (the password is stored safely in a keyring).
Other things like if the browser tabs should be closed after connection can be selected.

The buttons that need to be pressed (mainly the one for selecting B-zone) can be selected by image recogniton or by manually providing a click coordinate by running **"Set manual click position" and selecting "Manual Coordinates"** in the options menu. This option can be helpfull if the image recognition does not work well on your machine.
Ivanti is pulled up then and you should click the B-zone connect button, this position is then recorded and saved.
There is also an image recognition option for clicking the button which is selected by default.

Other stability issues may be solved by **checking if the ivanti secure access path references correctly to the one on your PC**. The speed of the different actions can be slowed to 0.5 for stability if the clicks are too fast. The actions can also be sped up to 2 times normal speed.

## Order of operations

### User has manually logged into toledo

To use the vpn automation, the user needs to be already connected to the KU Leuven services to be able to open the vpn tabs and do following steps. So **log into toledo** with two factor authentication.

### Run the vpn_kul.exe file

The file will do all the following steps for you.

### Open vpn.kuleuven.be

First the vpn site https://vpn.kuleuven.be is opened in the browser which is nessecary since 2025 to be able to use ivanti secure access

### Ivanti login

Ivanti is opened automaticaly, the B-zone connect button is selected and provided login is supplied after which te proceed button is pressed.

### ICTS website connection to secure connection

The script finally opens https://uafw.icts.kuleuven.be to secure the connection.

### If selected, applications are closed

Ivanti secure access and the two browser tabs can be closed automatically.

## Known bugs

After setting the manual click coordinate, there is a few seconds of noticable lag.

When B-zone is not selected in blue (happens when it has been selected last) or any other UI elements differ, image recognition will not work.