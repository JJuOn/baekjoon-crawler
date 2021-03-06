from __future__ import print_function
from selenium import webdriver
from selenium.common.exceptions import SessionNotCreatedException, WebDriverException
from getpass import getpass
from time import sleep
from bs4 import BeautifulSoup
import os
import requests
import datetime
import sys
import json

def print_explaination(order,problemListLen=None):
    if order==0:
        print("="*25)
        print("해결한 문제의 풀이를 파일로 손쉽게 저장하기 위한 프로그램입니다.")
        print("자신이 해결한 문제의 소스코드에 접근하기 위해 로그인이 필요하며")
        print("다른 목적으로는 사용되지 않습니다.")
        print("로그인이 진행된 후 CAPTCHA를 풀어주시면 이어서 진행됩니다.")
        print("="*25)
        print("두 가지 방식으로 소스코드를 저장할 수 있습니다.")
        print("1. 푼 모든 백준 문제를 저장.")
        print("2. 이전 실행과 비교하여 새로 푼 문제만 저장.")
        option=input("선택할 기능을 입력해 주세요. : ")
        if option!='1' and option!='2':
            print("잘못된 입력입니다. 프로그램을 종료합니다.")
            exit()
        return option
    elif order==1:
        print("사용자 {}가 푼 문제 수는 {}입니다.".format(userId,len(problemList)))
        dirname=datetime.datetime.now().strftime("%Y%m%d")
        print("{}\\{}에 {}개의 문제가 1000개씩 묶여 한 폴더에 저장됩니다.".format(os.getcwd(),dirname,problemListLen))
        print("지원되는 확장자는 다음과 같습니다.")
        print("C++:.cpp")
        print("Java:.java")
        print("Python:.py")
        print("C:.c")
        print("node.js:.js")
        print("Golfscript:.gs")
        print("PHP:.php")
        input("아무 키를 눌러 진행해 주세요. ")
        if not os.path.exists('./{}'.format(dirname)):
            os.mkdir(dirname)
    return


def login():
    print("="*25)
    userId=input("백준 ID를 입력해 주세요. : ")
    password=getpass("백준 PW를 입력해 주세요. : ")
    return userId, password


def get_cookies(userId,password):
    try:
        driver=webdriver.Chrome('./chromedriver/chromedriver.exe')
    except SessionNotCreatedException:
        print("chromedriver의 버전이 맞지 않습니다.\nhttps://chromedriver.chromium.org/downloads 에서 현재 chrome의 버전에 맞는 chromedriver를 설치해 주세요.",file=sys.stderr)
        exit(1)
    driver.implicitly_wait(3)
    driver.get('https://acmicpc.net/login?next=%2F')
    driver.find_element_by_name('login_user_id').send_keys(userId)
    driver.find_element_by_name('login_password').send_keys(password)
    driver.find_elements_by_id('submit_button')[0].click()
    print("="*25)
    input("CAPTCHA를 푸셨으면 아무 키나 눌러 주세요. ")
    cookies=driver.get_cookies()
    driver.quit()
    return cookies

def get_problem_list(cookies):
    for cookie in cookies:
        if cookie['name']=='OnlineJudge':
            cookies={'OnlineJudge':cookie['value']}
            break
    response=requests.get('https://www.acmicpc.net/user/{}'.format(userId),cookies=cookies).text
    soup=BeautifulSoup(response,'html.parser')
    problemListTags=soup.select('a.result-ac')
    problemList=[]
    for problemListTag in problemListTags:
        problemList.append(problemListTag.text)
    return cookies, problemList

def get_log(path='log.json'):
    if not os.path.exists(path):
        log=dict()
    else:
        file=open(path,'r')
        log=json.loads(file.read())
        file.close()
    return log


def check_log(log,problemNo,soultionLength):
    if problemNo in log:
        # if True, skip saving
        return log[problemNo]==soultionLength
    else:
        # it means new problem
        return False


def save_log(log,path,problemNo,soultionLength):
    log[problemNo]=soultionLength
    file=open(path,'w')
    file.write(json.dumps(log))
    file.close()
    # print('log saved')
    return log


def get_extension(language):
    extension=""
    if "C++" in language:
        extension="cpp"
    elif "Java" in language:
        extension="java"
    elif "Python" in language:
        extension="py"
    elif "C" in language:
        extension="c"
    elif "node.js" in language:
        extension="js"
    elif "Golfscript" in language:
        extension="gs"
    elif "PHP" in language:
        extension="php"
    return extension

def get_source(problemList,option):
    dirname=datetime.datetime.now().strftime("%Y%m%d")
    log=get_log('log.json')
    for i,problem in enumerate(problemList):
        print("{}> ({}%)".format("="*int(max((i+1)/len(problemList)*20,1)),int((i+1)/len(problemList)*100)),end="\r")
        response=requests.get("https://www.acmicpc.net/status?from_mine=1&problem_id={}&user_id={}".format(problem,userId),cookies=cookies).text
        soup=BeautifulSoup(response,'html.parser')
        trs=soup.select('html > body > div.wrapper > div.container.content > div.row > div.col-md-12 > div.table-responsive > table#status-table > tbody > tr')
        tds=trs[0].select('td')

        solutionId=tds[0].text
        language=tds[6].select('a')[0].text
        response=requests.get("https://www.acmicpc.net/submit/{}/{}".format(problem,solutionId),cookies=cookies).text
        soup=BeautifulSoup(response,'html.parser')
        source=soup.select("textarea#source")
        source=source[0].text
        # print('Processing...\tproblem:{}\tlength:{}\tlanguage:{}'.format(problem,len(source),language))
        # skip condition
        if option=='2' and check_log(log,problem,len(source)):
            # print('skip')
            continue
        extension=get_extension(language)
        if not os.path.exists('./{}/{}~{}'.format(dirname,int(problem)//1000*1000,(int(problem)//1000+1)*1000-1)):
            os.mkdir('./{}/{}~{}'.format(dirname,int(problem)//1000*1000,(int(problem)//1000+1)*1000-1))
        file=open('./{}/{}~{}/{}.{}'.format(dirname,int(problem)//1000*1000,(int(problem)//1000+1)*1000-1,problem,extension),'w')
        file.write(source)
        file.close()
        log=save_log(log,'log.json',problem,len(source))

if __name__=="__main__":
    option=print_explaination(0)
    userId,password=login()
    cookies=get_cookies(userId,password)
    cookies,problemList=get_problem_list(cookies)
    print_explaination(1,len(problemList))
    get_source(problemList,option)
    input("작업이 완료되었습니다. 아무 키를 눌러 종료해 주세요.")
    
