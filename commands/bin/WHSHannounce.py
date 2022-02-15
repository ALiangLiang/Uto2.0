from commands.bin.time import getTempNowTime
from commands.config.config import WHSHannounce
from commands.bin.embed import *

import requests
import re
import time
import bs4
import json



class news_id:
  def __init__(self, id: str, is_pinned: bool, date: time.struct_time = None):
    self.id = id
    self.is_pinned = is_pinned
    self.date = date


class msg:
  def __init__(self, link: str, title: str, date: time.struct_time):
    self.link: str = link
    self.title: str = title
    self.date: time.struct_time = date

  def detail(self) -> str:
    return f"{self.link}\n{self.title}\n{self.date_str()}"

  def url(self) -> str:
    return self.link

  def retitle(self) -> str:
    return self.title

  def date_str(self) -> str:
    return time.strftime("%Y-%m-%d", self.date)

header: dict = {
  "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36"
}

class info:
  def get(school: str, info: str) -> str:
    with open("./commands/bin/try.json",'r',encoding='utf8') as jfile:
      data = json.load(jfile)
    return data[f"{school}_latest_{info}"]

  def set(school: str, info: str, context: str):
    with open("./commands/bin/try.json",'r',encoding='utf8') as jfile:
      data = json.load(jfile)
    data[f"{school}_latest_{info}"] = context
    with open("./commands/bin/try.json",'w',encoding='utf8') as jfile:
      json.dump(data,jfile,indent=4)







whshlist = ["whsh", "web.whsh.tc.edu.tw", "WID_0_2_518cd2a7e52b7f65fc750eded8b99ffcc2a7daca"]

def get_newsid(sch_url: str, sch_uid: str, pageNum: int = 0, maxRows: int = 15) -> list:
  send_data: dict = {
    "field" : "time",
    "order" : "DESC",
    "pageNum" : str(pageNum),
    "maxRows" : str(maxRows),
    "keyword" : "",
    "uid" : sch_uid,
    "tf" : "1", #"tf" means "the fuck?"
    "auth_type" : "user"
  }

  responce: requests.Response = requests.post(url = f"https://{sch_url}/ischool/widget/site_news/news_query_json.php", data = send_data)
  result: list = []

  id_pinned: list = re.findall(r'"newsId":"([0-9]*)","top":([01])', responce.text)

  for i in id_pinned:
    is_pinned: bool = (i[1] == "1")
    result.append(news_id(i[0], is_pinned))

  return result
def get_news(sch_id: str, sch_url: str, sch_uid) -> list:
    print(f"{sch_id} runned")

    next: bool = True
    page: int = 0
    result: list = []

    vaild_news: list = []

    while(next):
        news: list = get_newsid(sch_url, sch_uid, page)

        for n in news:
          if(n.id == info.get(sch_id, "id") and not n.is_pinned):
            break

          link: str = f"https://{sch_url}/ischool/public/news_view/show.php?nid={n.id}"

          response: requests.Response = requests.get(link, headers = header)
          response.encoding = response.apparent_encoding

          soup: bs4.BeautifulSoup = bs4.BeautifulSoup(response.text, "html.parser")
          soup.encoding = response.encoding

          title: str = soup.title.string
          date: time.struct_time = time.strptime(soup.find(id = "info_time").text.strip(), "%Y-%m-%d %H:%M:%S")
          latest_date: time.struct_time = time.strptime(info.get(sch_id, "date"), "%Y-%m-%d")

          if(date >= latest_date or n.is_pinned):
            result.append(msg(link, title, date))
            if(not n.is_pinned):
              vaild_news.append(news_id(n.id, n.is_pinned, date))

          else:
            next = False
            break

        page += 1

    if(len(vaild_news) > 0):
        for vn in vaild_news:
          if(not vn.is_pinned):
            info.set(sch_id, "date", time.strftime("%Y-%m-%d", vn.date))
            info.set(sch_id, "id", vn.id)
            break

    return result


def announce():
  res = get_news(whshlist[0],whshlist[1],whshlist[2])
  date = "{}月{}日".format(getTempNowTime("%m"),getTempNowTime("%d"))
  message =  ""
  for re in res:
    message += WHSHannounce.description.format(re.retitle(),re.url(),re.date_str())
  embed = getembed(WHSHannounce.title.format(date),message+WHSHannounce.end_description,WHSHannounce.color)
    
  return embed

def openAnnounce():
  with open('./commands/config/cmdconfig/announce.json','r',encoding='utf8') as jfile:
    data = json.load(jfile)
  return data
def writeAnnounce(data):
  with open('./commands/config/cmdconfig/announce.json','w',encoding='utf8') as jfile:
    json.dump(data,jfile,indent=4)