# SpotiMeuk
Great tool for finding 'Meuk' on Spotify! Only works on MacOs and Linux.


## Setup
Go to https://developer.spotify.com/dashboard/applications and create and application.
Copy the client_id and client_secret to the `client_info.py` file. And setup the `redirect_uri` in the application to `https://google.com` or some other site, doesnt realy matter. 

## How to install
Clone the github rep, and run:
    `pip install requirements.txt`

run the script in the command line:
    `python main.py`

### First Use
Browser window prompt, login with spotify account, copy the url the appears on your redirect uri page to the command line (paste using ctrl-shift-v). This creates an `tekore.cfg` file that will manage access tokens from now on. 

## ToDo
Add/Extend support for searching by song titles and genres. Finish chaning search settings from the CLI