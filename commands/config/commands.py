import imp
import json
import os
from commands.config.config import PRE

with open("./commands/config/commands.json",'r',encoding='utf8') as jfile:
    config = json.load(jfile)

def getHelpcommands(command):
    try:
        txt = "\n".join(config[command])
        txt = txt.replace("%%",PRE)
        return txt
    except:
        return None