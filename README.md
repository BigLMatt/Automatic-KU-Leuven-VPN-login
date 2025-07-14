# automatic-KU-Leuven-Ivanti-VPN-login
Once logged in to toledo, the script calls all the nessecary steps to log into the KU Leuven VPN in order to be able to use software like siemens NX off campus.

## Installation
Upon first running the .exe file, the login (r-number) and password need to be provided. These are to be stored in plain text in an environment variable document (.env)
Do not add any spaces before or after the =.

## Order of operations
### Open vpn.kuleuven.be
First the vpn site https://vpn.kuleuven.be is called in the browser which is nessecary since 2025 to be able to use ivanti secure access

### Ivanti login
Ivanti is opened automaticaly, the B-zone connect button is selected and provided login is supplied after which te proceed button is pressed.

### ICTS website connection to secure connection
The script finally opens https://uafw.icts.kuleuven.be to secure the connection, after this the browser windows can be closed manually.
