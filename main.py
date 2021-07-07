from __future__ import print_function
from selenium import webdriver
from selenium.common.exceptions import SessionNotCreatedException, WebDriverException
from getpass import getpass
from bs4 import BeautifulSoup
from multiprocessing import cpu_count
from tqdm import tqdm
from functools import partial
from multiprocessing.dummy import Pool as ThreadPool

import os
import requests
import datetime
import sys
import json

import numpy as np


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
        extensions=[
            {'name':'C++','extension':'cpp'},
            {'name':'Java','extension':'java'},
            {'name':'Python','extension':'py'},
            {'name':'C','extension':'c'},
            {'name':'PyPy','extension':'py'},
            {'name':'C#','extension':'cs'},
            {'name':'node.js','extension':'js'},
            {'name':'PHP','extension':'php'},
            {'name':'Ruby','extension':'rb'},
            {'name':'Kotlin','extension':'kt'},
            {'name':'Go','extension':'go'},
            {'name':'Golfscript','extension':'gs'}
        ]
        for e in extensions:
            print('{} : .{}'.format(e['name'],e['extension']))
        input("아무 키를 눌러 진행해 주세요. ")
        if not os.path.exists('./{}'.format(dirname)):
            os.mkdir(dirname)
    return


def login():
    print("="*25)
    userId=input("백준 ID를 입력해 주세요. : ")
    password=getpass("백준 PW를 입력해 주세요. : ")
    return userId, password


def session_validataion(cookies):
    for cookie in cookies:
        if cookie['name']=='OnlineJudge':
            cookies={'OnlineJudge':cookie['value']}
            break
    response=requests.get('https://www.acmicpc.net/',cookies=cookies).text
    soup=BeautifulSoup(response,'html.parser')
    if len(soup.select('a.username'))!=0:
        return True
    else:
        return False


def get_cookies(userId,password):
    existFileButNotUser=False
    if os.path.exists('./user.json'):
        userFile=open('./user.json','r')
        userDict=json.loads(userFile.read())
        if userId in userDict:
            if session_validataion([{'name':'OnlineJudge','value':userDict[userId]}]):
                return [{'name':'OnlineJudge','value':userDict[userId]}]
        existFileButNotUser=True
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

    if not os.path.exists('./user.json'):
        value=""
        for cookie in cookies:
            if cookie['name']=="OnlineJudge":
                value=cookie['value']
        file=open('./user.json','w')
        file.write(json.dumps({userId:value}))
        file.close()

    elif existFileButNotUser:
        value=""
        for cookie in cookies:
            if cookie['name']=="OnlineJudge":
                value=cookie['value']
        file=open('./user.json','r')
        userDict=json.loads(file.read())
        userDict[userId]=value
        file.close()
        file=open('./user.json','w')
        file.write(json.dumps(userDict))
        file.close()
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
        log=list()
    else:
        file=open(path,'r')
        log=json.loads(file.read())
        file.close()
        if isinstance(log,dict):
            li=[]
            for key in log.keys():
                li.append({'problemNo':key,'solutionLength':log[key]})
            log=li
            file=open(path,'w')
            file.write(json.dumps(log))
            file.close()
    return log


def check_log(log,problemNo,soultionLength):
    for elem in log:
        if elem['problemNo']==problemNo:
            if elem['solutionLength']==soultionLength:
                return True
            else:
                return False
    return False


def save_log(log,path,problemNo,solutionLength):
    log.append({'problemNo':problemNo,'solutionLength':solutionLength})
    file=open(path,'w')
    file.write(json.dumps(log))
    file.close()
    return log


def get_extension(language):
    extension=""
    if "C++" in language:
        extension="cpp"
    elif "Java" in language:
        extension="java"
    elif "Python" in language or "PyPy" in language:
        extension="py"
    elif "C#" in language:
        extension="cs"
    elif "node.js" in language:
        extension="js"
    elif "Golfscript" in language:
        extension="gs"
    elif "PHP" in language:
        extension="php"
    elif "Ruby" in language:
        extension="rb"
    elif "Kotlin" in language:
        extension="kt"
    elif "C" in language:
        extension="c"
    elif "Go" in language:
        extension="go"
    return extension

def get_source(problemList,option,userId,cookies,progress_bar):
    dirname=datetime.datetime.now().strftime("%Y%m%d")
    log=get_log('log.json')
    for problem in problemList:
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
        progress_bar.update(1)
        # skip condition
        if option=='2' and check_log(log,problem,len(source)):
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
    problemListLen=len(problemList)
    print_explaination(1,len(problemList))
    splitedProblemList=np.array_split(problemList,cpu_count())
    splitedProblemList=[x.tolist() for x in splitedProblemList]
    pool=ThreadPool(processes=cpu_count())
    with tqdm(total=problemListLen) as progress_bar:
        get_source_partial=partial(get_source,option=option,userId=userId,cookies=cookies,progress_bar=progress_bar)
        pool.map(get_source_partial,splitedProblemList)
    input("작업이 완료되었습니다. 아무 키를 눌러 종료해 주세요.")