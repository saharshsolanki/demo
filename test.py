import requests
from bs4 import BeautifulSoup

URL = "https://in.indeed.com/java-developer-jobs-in-Ujjain,-Madhya-Pradesh"
page = requests.get(URL)

soup = BeautifulSoup(page.content, "html.parser")
result = soup.find_all('a')

for p in result:
    t = p.find("h2", class_="jobTitle jobTitle-color-purple")
    if t == None:
        pass
    else:
        print(t.get_text())
    t1 = p.find("span", class_="companyName")
    if t1 == None:
        pass
    else:
        print(t.get_text())

# import requests
# url = 'https://jira-chat-bot-by-saharsh.herokuapp.com/webhooks/rest/webhook' ##change rasablog with your app name
# myobj = {
# "message": "hi",
# "sender": 1,
# }
# x = requests.post(url, json = myobj)
# print(x.text)
