from distutils import command
import requests
import facebook
import urllib3
import json


def openFB():
    with open('./commands/config/cmdconfig/facebook.json','r',encoding='utf8') as jfile:
        data = json.load(jfile)
    return data
def writeFB(data):
    with open('./commands/config/cmdconfig/facebook.json','w',encoding='utf8') as jfile:
        json.dump(data,jfile,indent=4)




def getFbPost(name):
    data = openFB()
    id = data[name]["url"]
    token = data[name]["token"]
    took = facebook.GraphAPI(access_token=token, version ='2.10')
    getdata = took.request(id)
    return getdata

def updateNowId(name,getdata):
    data = openFB()
    data[name]["id"] = getdata['posts']['data'][0]["id"]
    writeFB(data)

def getCount(name,getdata):
    data = openFB()
    for i in range(100):
        fbdata = getdata['posts']['data'][99-i]
        if(str(fbdata['id']) == data[name]["id"]):
            updateid = 99-i
            break
        else:
            updateid = -1
    return updateid