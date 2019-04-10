from bs4 import BeautifulSoup
import requests
import re
#from selenium import webdriver
#from selenium.webdriver.chrome.options import Options
import calendar
from datetime import  datetime
now = datetime.now()


#chrome_driver를 다운 받고, 다운 받은 경로를 아래에 적어야 합니다.
#chrome_driver_path = 'C:\\Users\speechlab\Downloads\chromedriver_win32/chromedriver.exe'  # chrome driver의 경로

###아래를 수정해서 크롤링하고자 하는 연월을 조정할 수 있습니다.
# START_YEAR~END_YEAR

START_YEAR = 2019
END_YEAR = 2019

START_MONTH = "01"
END_MONTH = "03"
#####################


##
current_year = "2019"
current_month = "4"
currnet_day = 1
current_page = 1

# limits page number
#PAGE_LIMIT = 20

#chrome_options = Options()
#chrome_options.add_argument('--headless')

#driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver_path)

f_ex = open("naver_news_crawl_url.txt","w",encoding="UTF8")
f = open("naver_news_crawl.txt", "w", encoding='UTF8')
#f_url = open("executed_urls.txt", "w")


# input : url
# do: comments 리스트에 저장한다. text contents를
# output :x
def extract_text_from_url(url):
    oid = url.split("oid=")[1].split("&")[0]
    aid = url.split("aid=")[1]
    page = 1
    header = {
        "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
        "referer": url,

    }
    while True:
        c_url = "https://apis.naver.com/commentBox/cbox/web_neo_list_jsonp.json?ticket=news&templateId=default_society&pool=cbox5&_callback=jQuery1707138182064460843_1523512042464&lang=ko&country=&objectId=news" + oid + "%2C" + aid + "&categoryId=&pageSize=20&indexSize=10&groupId=&listType=OBJECT&pageType=more&page=" + str(
            page) + "&refresh=false&sort=FAVORITE"
        # 파싱하는 단계입니다.
        r = requests.get(c_url, headers=header)
        cleaned_text = []
        cont = BeautifulSoup(r.content, "html.parser")

        # print(str(cont))

        total_comm = str(cont).split('comment":')[1].split(",")[0]

        match = re.findall('"contents":([^\*]*),"userIdNo"', str(cont))

        hangul = re.compile('[0-9ㄱ-ㅣ가-힣\s]+[ㄱ-ㅣ가-힣]')  # 한글과 띄어쓰기를 제외한 모든 글자

        for i in match:
            cleaned_text = hangul.findall(i)
            print("cleaned_text",cleaned_text)
            #cleaned_text = flatten(cleaned_text)

        # 댓글을 리스트에 중첩합니다.
        for i in flatten(cleaned_text):
            # f.write(str(url) + '\n')

            i = i.replace(".","\n")
            print(type(i))
            print("내용",i)
            if len(i) > 10:
                f.write(str(i)+"\n")


        # 한번에 댓글이 20개씩 보이기 때문에 한 페이지씩 몽땅 댓글을 긁어 옵니다.
        if int(total_comm) <= ((page) * 20):
            break
        else:
            page += 1


# 여러 리스트들을 하나로 묶어 주는 함수입니다.
def flatten(l):
    flatList = []
    for elem in l:
        # if an element of a list is a list
        # iterate over this list and add elements to flatList
        if type(elem) == list:
            for e in elem:
                flatList.append(e)
        else:
            flatList.append(elem)
    return flatList


# extract soup from the naver's main new page
# return urls in list format
def extract_URL(tmp):
    # for the return value
    move_around_url = []

    f_ex.write(tmp + "\n")
    r = requests.get(tmp)

    if r.status_code != 200:
        print("in valid url!! error code: %s" % (r.status_code))
        return

    r = requests.get(tmp)
    soup = BeautifulSoup(r.content, 'html.parser')

    # at the first page (which have all the newses) ,scrab all urls which are available
    # new_url is in list format
    # get additional url in the queue , only when we turn into the next page (not at the side newses)

    for link in soup.find_all("a"):
        #print(link)
        # <a href="https://news.naver.com/main/read.nhn?mode=LS2D&mid=shm&sid1=100&sid2=264&oid=421&aid=0003169691">
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


        print("url",i)



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
            if i.find("aid") != -1 and i.find("https") != -1 and i.find("oid") != -1:
                # get all the comments from there
                extract_text_from_url(i)


def check_is_valid_url(i):
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
    #https://news.naver.com/main/list.nhn?mode = LS2D&mid = shm&sid2 = 264&sid1 = 100&date = 20190101&page = 1

    # &date=20180125&page=4
    additional_url = "&date="+current_year+current_month+str(currnet_day).zfill(2) +"&page="+str(current_page)

    tmp =  section_url.replace( "page=" + str(section_url.split("=")[6])  ,  "page="+str(current_page)     )

    summed_url = tmp

    #print("suumed_url is %s"%summed_url)
    if check_is_valid_url(summed_url) == 1 :

        return summed_url




def clean_text(text):
    hangul = re.compile('[0-9ㄱ-ㅣ가-힣\s]+[ㄱ-ㅣ가-힣]')  # 한글과 띄어쓰기를 제외한 모든 글자

    #list로 반환된다.
    cleaned_text =  hangul.findall(text)

    return cleaned_text





#sid = {sid1:[sid2]}
# a = { 'a': [1,2,3]}

sid= {'100':["264","265","266","267","268","269"],
       '101':['259','258','261','771','260','262','310','263'],
       '102':['249','250','251','254','252','59b','255','256','276','257'],
       '103': ['241','239','240','237','238','376','242','243','244','248','245'],
        '104':['231','232','233','234','322'],
      '105':['731','226','227','230','732','283','229','228']
      }


#https://news.naver.com/main/list.nhn?mode=LS2D&mid=shm&sid2=259&sid1=101&date=20190127&page=2
def get_the_next_section_url_bu_changing_sid1_sid2(sid1,sid2):
    url = "https://news.naver.com/main/list.nhn?mode=LS2D&mid=shm&" + "sid2=" + sid2 + "&"\
    +"sid1=" + sid1 + "&" + "date=" + current_year + current_month + currnet_day + "&" + "page=" + str(current_page)

    return url



# minor section list를 수집한다.
#


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

            #chage sid1,sid2
            for i in sid:
                for t in sid[i]:
                    print((i),(t))

                    url = get_the_next_section_url_bu_changing_sid1_sid2(str(i), str(t))
                    url_move_around_pages(url)



f.close()
f_ex.close()