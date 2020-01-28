from selenium import webdriver 
from getpass import getpass
from time import sleep
from bs4 import BeautifulSoup
import os
import requests
import datetime

if __name__=="__main__":
    print("="*25)
    print("해결한 문제의 풀이를 파일로 손쉽게 저장하기 위한 프로그램입니다.")
    print("자신이 해결한 문제의 소스코드에 접근하기 위해 로그인이 필요하며")
    print("다른 목적으로는 사용되지 않습니다.")
    print("로그인이 진행된 후 CAPTCHA를 풀어주시면 이어서 진행됩니다.")
    print("="*25)
    userId=input("백준 ID를 입력해 주세요. : ")
    password=getpass("백준 PW를 입력해 주세요. : ")
    driver=webdriver.Chrome('./chromedriver/chromedriver.exe')
    driver.implicitly_wait(3)
    driver.get('https://acmicpc.net/login?next=%2F')
    driver.find_element_by_name('login_user_id').send_keys(userId)
    driver.find_element_by_name('login_password').send_keys(password)
    driver.find_elements_by_id('submit_button')[0].click()
    print("="*25)
    input("CAPTCHA를 푸셨으면 아무 키나 눌러 주세요. ")
    cookies=driver.get_cookies()
    driver.quit()
    for cookie in cookies:
        if cookie['name']=='OnlineJudge':
            cookies={'OnlineJudge':cookie['value']}
            break
    response=requests.get('https://www.acmicpc.net/user/{}'.format(userId),cookies=cookies).text
    soup=BeautifulSoup(response,'html.parser')
    problemListTags=soup.select('html > body > div.wrapper > div.container.content > div.row > div.col-md-12 > div.row > div.col-md-9 > div.panel.panel-default > div.panel-body > span.problem_number > a.result-ac')
    problemList=[]
    for problemListTag in problemListTags:
        problemList.append(problemListTag.text)
    print("사용자 {}가 푼 문제 수는 {}입니다.".format(userId,len(problemList)))

    dirname=datetime.datetime.now().strftime("%Y%m%d")
    print("{}\\{}에 {}개의 문제가 1000개씩 묶여 한 폴더에 저장됩니다.".format(os.getcwd(),dirname,len(problemList)))
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
        if not os.path.exists('./{}/{}~{}'.format(dirname,int(problem)//1000*1000,(int(problem)//1000+1)*1000-1)):
            os.mkdir('./{}/{}~{}'.format(dirname,int(problem)//1000*1000,(int(problem)//1000+1)*1000-1))
        file=open('./{}/{}~{}/{}.{}'.format(dirname,int(problem)//1000*1000,(int(problem)//1000+1)*1000-1,problem,extension),'w')
        file.write(source)
        file.close()
    input("작업이 완료되었습니다. 아무 키를 눌러 종료해 주세요.")
    
