import os
import tekore as tk

CLIENT_ID = "1315cd575b0341a9b49f45dc7659e398" 
CLIENT_SECRET = "a633e4f83ebf48b7901ab557b972d03b" 
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