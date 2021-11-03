# M3UKINATOR
The most stupid project you will ever see! Find 'Meuk' (NL) on Spotify! Only works on MacOs and Linux due to CLI.


## Setup
Go to https://developer.spotify.com/dashboard/applications and create and application.
Copy the client_id and client_secret to the `src/login.py` file. And setup the `redirect_uri` in the application to `https://google.com` or some other site, doesnt realy matter. 

## How to install
Clone the github rep, and run:
    `pip install requirements.txt`
However, this is broken, so install the modules listed in this file yourself :)

run the script in the command line:
    `python main.py`

## First Use
Browser window prompt, login with spotify account, copy the url the appears on your redirect uri page to the command line (paste using ctrl-shift-v). This creates an `tekore.cfg` file that will manage access tokens from now on. 

## Usage
Only 'Artist Search' works in this version, type name and press enter (takes few seconds)

## ToDo / Known Issues
- Add song search
- Speed up search process
- Improve CLI to go back to previous page instead of main menu
- add player controlles
- add song to playlist ect...
