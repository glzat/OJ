import requests
import json
import os
import time
from bs4 import BeautifulSoup

# 初始化变量
with open("config.json", "r") as f:# 加载配置
    config = json.load(f)
    username = config["username"]
    password = config["password"]
    first_time = config["first_time"]

headers = { # 伪装成浏览器
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
}
data = {
    "username": username,
    "password": password
}
question_list = {}# 格式:{题单编号：[题目名称,....]}
questions = []# 题单编号列表，方便url访问

def login(url):# 登录
    # 使用session对象，这样cookie会在跨请求时保存
    session = requests.Session()
    session.post("http://noi.ybtoj.com.cn/api/login",headers=headers,data=data)
    return session.get(url,headers=headers)

def question_list_len(chapter):# 获取题单长度
    try:
        url = f"http://noi.ybtoj.com.cn/contest/{chapter}"
        response = login(url)
        soup = BeautifulSoup(response.text, "html.parser")
        # 找到第一个表格
        table = soup.find('table')
        # 获取表格的所有行
        rows = table.find_all('tr')
        # 表格的长度就是行的数量
        length = len(rows)
    except AttributeError:# 题单不存在
        return 0
    else:
        return length
    
def get_problem(chapter,question_id,k,v):# 获取题目内容
    url = f"http://noi.ybtoj.com.cn/contest/{chapter}/problem/{question_id}"
    response = login(url)
    soup = BeautifulSoup(response.text, "html.parser")
    columns = soup.findAll("div",attrs={"class":"column"})
    f = open(f"questions\{k}-{v}.html","w",encoding="utf-8")
    for i in range(1,6):
        try:
            f.write(columns[i].prettify())
        except IndexError:
            continue
    f.close()

def add_question_list():# 添加题单列表
    with open("question.txt","w") as f:
        for i in range(672,830):
            if(question_list_len(i) != 0):
                print(f"[Log] Successfully to add the Page {i}!")
                f.write(f"{i},")
            else:
                print(f"[Error] Failed to add the Page {i}!")
                continue

def get_question_list_name():# 获取题单名称
    url = f"http://noi.ybtoj.com.cn/course/3"
    response = login(url)
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find('table')
    rows = table.find_all('td',attrs={"class":""})
    for i in range(0,len(questions)):
        question_list[rows[i].text.strip()]=[]
        ql = f"http://noi.ybtoj.com.cn/contest/{questions[i]}"
        res = login(ql)
        sp = BeautifulSoup(res.text, "html.parser")
        tb = sp.find('table')
        rw = tb.find_all('td',attrs={"class":""})
        for j in range(0,question_list_len(questions[i])-1):
                question_list[rows[i].text.strip()].append(rw[j].text.strip())
        print(f"[Log] Successfully to add the question list {rows[i].text.strip()}!")

if first_time:# 初始化程序
    # add_question_list()
    
    # with open("question_list.json","w") as f:
    #     json.dump(question_list,f)
    config["first_time"] = False
    with open("config.json","w")as f:# 更新配置文件
        json.dump(config,f)

with open("question_list.json","r",encoding="utf-8") as f:
    question_list = json.load(f)

with open("question.txt","r") as f:# 读取题单
    questions = f.read().split(",")

questions.pop()# 删除最后一个空元素
# get_question_list_name() # 获取题单
# with open("question_list.json","w",encoding="utf-8") as f:
#     json.dump(question_list,f)
idx_list = 1
idx_problem = 1
for key in question_list:
    for value in question_list[key]:
        with open(f"questions\{key}-{value}.html","w",encoding="utf-8")as f:
            get_problem(questions[idx_list],idx_problem,key,value)
            print(f"[Log] Successfully to add the problem {key}-{value}!")
        idx_problem += 1
    time.sleep(1)
    idx_problem = 1
    idx_list += 1
print("[Log] All done!")
os.system("pause")