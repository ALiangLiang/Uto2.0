from datetime import datetime
from dateutil import tz
from commands.config.config import TIME_ZONE
from datetime import date


def TimeZoneChange(time:str,type:str):
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz(TIME_ZONE)
    utc = datetime.strptime(time, type)
    utc = utc.replace(tzinfo=from_zone)
    central = utc.astimezone(to_zone)
    return central

def RewriteTime(time:datetime,returntype):
    return time.strftime(returntype)

def getTempNowTime(String:str):
    return int(datetime.now().strftime(String))

def dateCalculate(year,month,day):
    Calculate = date(year,month,day)-date.today()
    return Calculate.days
#TimeZoneChange(RewriteTime('2022-02-06T14:39:26+0000',WHSH_FUCK_TIME),WHSH_FUCK_TO_TIME)