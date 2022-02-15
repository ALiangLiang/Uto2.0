import json
def permission(id,guild):
    with open("core/permission.json",'r',encoding='utf8') as jfile:
        getpermission = json.load(jfile)
    if id in getpermission["devoloper"]:
        return 4
    elif id in getpermission["admin"][guild]:
        return 3
    elif id in getpermission["high"][guild]:
        return 2
    else:
        return 1