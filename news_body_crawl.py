from bs4 import BeautifulSoup
import requests
import re
#from selenium import webdriver
#from selenium.webdriver.chrome.options import Options
import calendar
from datetime import  datetime
now = datetime.now()

import time


#chrome_driver를 다운 받고, 다운 받은 경로를 아래에 적어야 합니다.
#chrome_driver_path = 'C:\\Users\speechlab\Downloads\chromedriver_win32/chromedriver.exe'  # chrome driver의 경로


###아래를 수정해서 크롤링하고자 하는 연월을 조정할 수 있습니다.
# START_YEAR~END_YEAR

START_YEAR = 2019
END_YEAR = 2019

START_MONTH = "01"

END_MONTH = "03"
#####################



'''
current_year = "2018"
current_month = "1"
currnet_day = 1
'''

current_page = 1

# limits page number
#PAGE_LIMIT = 20

#chrome_options = Options()
#chrome_options.add_argument('--headless')

#driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver_path)

f = open("0410_네이버바디크롤링.txt", "w", encoding='UTF8')
f_ex = open("0410_네이버바디크롤링_url.txt","w",encoding="UTF8")

# 기사를 가져오는걸로 바꿔야 한다.
def extract_text_from_url(url):

    #다음 페이지 넘버를 알아보자.
    r = requests.get(url)


    try:
        r = requests.get(url)
    except:
        print("52 error occured at :)")
        f_ex.write("52 error occured at :)")
        time.sleep(120)
        r = requests.get(url)


    soup = BeautifulSoup(r.content, 'html.parser')
    text = ''
    join_list = []
    for item in soup.find_all('div', id='articleBodyContents'):

        item = str(item)

        text = clean_text(item)

        tmp_len = len(text.split("."))
        tmp_int = 1
        for i in text.split("."):
            tmp_str = str(i)
            file_print(tmp_str)
            tmp_int += 1

            if  tmp_int > tmp_len - 10 :
                print("break")
                break



def file_print(text):
    text = text.strip()
    flag = 1

    if len(text) < 10 :
        flag = 0

    filter_string_list = ["기자","본문 내용","영상 플레이어","리포트"]

    for i in filter_string_list:
        erase = re.compile(i)
        if erase.search(text) :
            flag = 0

    if flag == 1:
        print(text)
        f.write(text + "\n")

def clean_text(text):
    # ~ -> 에서
    text = re.sub("∼","에서",text)
    text = re.sub("~", "에서", text)

    #cm -> 센티미터 : sub
    text = re.sub("cm","센티미터",text)

    #숫자 . 숫자 -> 숫자 점 숫자 :
    text = re.sub(r'([0-9])\.([0-9])',r'\1점\2',text)

    #68768-5656 -> 숫자 다시 숫자 :
    text = re.sub(r'([0-9])\.([0-9])',r'\1 다시 \2',text)

    # -1 -> 마이너스 1 :sub
    text = re.sub(r'-([0-9])',r'\1마이너스',text)

    # 숫자% -> 퍼센트 :
    text = re.sub(r'([0-9])%',r"\1퍼센트",text)

    #㎡ -> 제곱미터 :
    text = re.sub(r'([0-9])㎡', r'\1제곱미터',text)

    hangul = re.compile('[^ .ㄱ-ㅣ가-힣0-9]+')  # 한글과 띄어쓰기 숫자를 제외한 모든 글자
    text = hangul.sub('', text)  # 한글과 띄어쓰기 숫자를 제외한 모든 부분을 제거


    #특수 문자 제거
    #text = re.sub('[-=+,#/\?:^$@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》{}_;\t▶ⓒ☞◀]', '', text)

    #영어 제거
    text = re.sub('[a-zA-Z]+',"",text)

    # 숫자로 끝나는거 제거
    text = re.sub('[0-9]+\s', "", text)

    #182520121231158800007여자농구 의미 없는 숫자 너무 긴거 제거
    text = re.sub('[0-9]{3,100}[0-9]',"",text)


    text_list = text.split("\n")



    hangul = re.compile('[0-9ㄱ-ㅣ가-힣\s]+[ㄱ-ㅣ가-힣]')  # 한글과 띄어쓰기를 제외한 모든 글자

    max_len = 0
    indexOf = -1
    for i in text_list:
        cleaned_text = str(i)
        if max_len <len(cleaned_text):
            max_len = len(cleaned_text)
            temp_str = i
    if len(temp_str) != 0 and max_len >40:

        cleaned_text = temp_str

    return cleaned_text



# 수정 완료
def extract_URL(tmp):

    # for the return value
    move_around_url = []

    print(tmp)
    f_ex.write(tmp + "\n")
    r = requests.get(tmp)


    try:
        r = requests.get(tmp)
    except:
        print("166 error occured at :)")
        f_ex.write("166 error occured at :)")
        time.sleep(120)
        r = requests.get(tmp)


    if r.status_code != 200:
        print("in valid url!! error code: %s" % (r.status_code))
        return


    soup = BeautifulSoup(r.content, 'html.parser')

    # at the first page (which have all the newses) ,scrab all urls which are available
    # new_url is in list format
    # get additional url in the queue , only when we turn into the next page (not at the side newses)

    for link in soup.find_all("a"):
        # https://news.naver.com/main/read.nhn?mode=LPOD&amp;mid=tvh&amp;oid=056&amp;aid=0010665672
        if "https://news.naver.com/main/read.nhn" in str(link.get('href')):
            if link.get('class') == None:
                #print(link)
                extracted_ = link.get('href')
                #print(link)

                # 중복된거 안넣어야되
                if move_around_url.count(extracted_) < 1:
                    move_around_url.append(extracted_)

    return move_around_url


class Queue(list):
    # enqueue == > insert 관용적인 이름
    enqueue = list.append

    # dequeue == > delete
    def dequeue(self):
        return self.pop(0)

    def is_empty(self):
        if not self:
            return True
        else:
            return False

    def peek(self):
        return self[0]

    # check whether i is in the list
    # if there is then return 1
    def is_list(self, i):
        if self.count(i) == 1:
            return 1;

q = Queue()


# input must be elem of section_list
# start from the page ->  get all the comments from there ->scrab all urls which are available -> append next pages
def url_move_around_pages(section_url):
    global current_page
    global  previous_page
    global f
    current_page = 1
    previous_page = 0
    q.enqueue(section_url)

    # print("section url is %s"%(section_url))

    while not q.is_empty():
        i = q.dequeue()
        #print(type(f))
        #f.write("comments from: " + str(i) + '\n')

        print(i)

        # case for page_list web page
        # append a next page , until page num < PAGE_LIMIT
        if i.find("list") != -1:

            # 현재 page에서 이제 page_list에서 보이는 기사들의 url들을 뽑아오자.
            #print(i)
            new_url = extract_URL(i)
            if new_url != None and len(new_url) >= 0:
                for j in new_url:
                    #print(j)
                    q.enqueue(j)

            next_page_url = go_to_next_page(i)

            print("next page url is %s"%next_page_url)

            #더 이상 다음 페이지가 없으면 새로운 노드를 큐에서 빼서 실행하면 된다.
            if next_page_url == -1:
                print("next page returned -1")
                continue
            else :
                q.enqueue(next_page_url)


        # case for the article inside
        else:
            #https://news.naver.com/main/read.nhn?mode=LPOD&amp;mid=tvh&amp;oid=056&amp;aid=0010665672
            if i.find("aid") != -1 and i.find("https") != -1 and i.find("oid") != -1:
                # get all the comments from there
                extract_text_from_url(i)


def check_is_valid_url(i):
    print(i)
    r = requests.get(i)


    try:
        r = requests.get(i)
    except:
        print("281 error occured at :)")
        f_ex.write("281 error occured at :)")
        time.sleep(120)
        r = requests.get(i)

    if r.status_code != 200:
        return -1
    else:
        return 1


def go_to_next_page(section_url):
    global current_page
    global previous_page
    find_flag = 0
    #다음 페이지 넘버를 알아보자.
    r = requests.get(section_url)


    try:
        r = requests.get(section_url)
    except:
        print("302 error occured at :)")
        f_ex.write("302 error occured at :)")
        time.sleep(120)
        r = requests.get(section_url)


    soup = BeautifulSoup(r.content, 'html.parser')

    #<a href="?mode=LS2D&amp;sid2=264&amp;sid1=100&amp;mid=shm&amp;date=20180101&amp;page=11" class="nclicks(fls.page)">11</a>
    #다음 페이지 넘버를 찾자! sunset = soup.find_all('span', {'class': 'sunset'})


    for link in soup.find_all('a',{'class':'nclicks(fls.page)'}):
        find_flag = 0


        #다음 버튼이 있으면 11,21로 아니면 그냥 다음 숫자.
        if ((str)(link).split(">")[1].split("<")[0]) == "다음":
            next_page = (previous_page / 10) * 10 + previous_page % 10 + 1
            next_page = int(next_page)
        elif ((str)(link).split(">")[1].split("<")[0]) == "이전":
            continue
        else:
            next_page = (int)((str)(link).split(">")[1].split("<")[0])

        print(current_page)
        print(previous_page)
        print(next_page,'\n')

        if next_page == previous_page:
            print("next and previous is same")
            return -1

        #다음으로 넘어갈 페이지가 있으면
        if next_page > current_page :
            find_flag= 1
            current_page = next_page
            current_page = (int)(current_page)

            previous_page = current_page

            break




    #not any pages to move
    if find_flag ==0 :
        print("find_flag is 0\n")
        current_page = 1
        previous_page = 0
        return -1


    # "#"을 기준으로 뒤에꺼를 tmp로 바꾸면된다.
    #https://news.naver.com/main/tv/list.nhn?mode = LPOD&mid = tvh&oid = 437&date = 20190127&page = 2

    # &date=20180125&page=4
    additional_url = "&date="+current_year+current_month+str(currnet_day).zfill(2) +"&page="+str(current_page)

    tmp =  section_url.replace( "page=" + str(section_url.split("=")[5])  ,  "page="+str(current_page)     )

    summed_url = tmp

    #print("suumed_url is %s"%summed_url)
    if check_is_valid_url(summed_url) == 1 :

        return summed_url



oid= {"056","214","057","052","055","374","448","422","449","215","437" }

#https://news.naver.com/main/tv/list.nhn?mode=LPOD&mid=tvh& oid=056&date=20190128&page=1
#https://news.naver.com/main/tv/list.nhn?mode=LPOD&mid=tvh& oid=214&date=20190128&page=1
def get_the_next_section_url_bu_changing_sid1_sid2(oid):
    url = "https://news.naver.com/main/tv/list.nhn?mode=LPOD&mid=tvh&" + "oid=" + oid + "&"\
    +"date=" + current_year + current_month + currnet_day + "&" + "page=" + str(current_page)

    return url




# 추출한 url들로 부터 다음 페이지로 이동하고 다시 url추출하고 dfs로 탐색
# year
for j in range(START_YEAR, END_YEAR + 1):
    current_year = str(j)

    # month
    for h in range((int)(START_MONTH), (int)(END_MONTH) + 1):
        current_month = str(h).zfill(2)

        # day
        for k in range(1, (int)(calendar.monthrange(j, (int)(current_month))[1])):
            currnet_day = (str)(k).zfill(2)

            print(current_year,current_month,currnet_day,'\n')

            #현재의 "연 월 일"을 넘어갈 경우 대비
            if now.year < int(current_year):
                continue
            elif now.year == int(current_year) and now.month < int(current_month):
                continue
            elif now.year == int(current_year) and now.month == int(current_month) and now.day < int(currnet_day):
                continue

            #chage oid
            for i in oid:
                print(i)
                url = get_the_next_section_url_bu_changing_sid1_sid2(i)
                url_move_around_pages(url)



#test 안쓰면 지우삼
#extract_text_from_url("https://news.naver.com/main/read.nhn?mode=LPOD&mid=tvh&oid=422&aid=0000001992")

f.close()
f_ex.close()