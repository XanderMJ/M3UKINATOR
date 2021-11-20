import os
import tekore as tk

CLIENT_ID = None 
CLIENT_SECRET = None
REDIRECT_URI = "https://google.com"
SCOPE = tk.scope.every

def fetch_token():
    file = "tekore.cfg"
    if os.path.isfile(file):
        conf = tk.config_from_file(file, return_refresh=True)
        token = tk.refresh_user_token(*conf[:2], conf[3])
    else:
        print(f"{file} not found, log-in to spotify and paste URL in commandline",)
        conf = (CLIENT_ID,CLIENT_SECRET,REDIRECT_URI)
        token = tk.prompt_for_user_token(*conf, scope=SCOPE)
        tk.config_to_file(file, conf + (token.refresh_token,))
    return token
