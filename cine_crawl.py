from bs4 import BeautifulSoup
import requests
import re
from fake_useragent import UserAgent
from datetime import  datetime
now = datetime.now()
import time

#chrome_driver를 다운 받고, 다운 받은 경로를 아래에 적어야 합니다.
#chrome_driver_path = 'C:\\Users\speechlab\Downloads\chromedriver_win32/chromedriver.exe'  # chrome driver의 경로


###아래를 수정해서 크롤링하고자 하는 연월을 조정할 수 있습니다.

current_page = 2717

# START_YEAR~END_YEAR

#####################


f_ex = open("movie_lylics_url.txt","w",encoding="UTF8")
f = open("movie_lylics.txt", "w", encoding='UTF8')
url = "http://cineaste.co.kr/bbs//board.php?bo_table=psd_caption&page="+ str(current_page)

ua = UserAgent()

header = {
    "User-agent": str(ua.random),
}


#자막 가져오는걸로 바꿔야된다.
def get_lylics_text(url):
    header["User-agent"] = str(ua.random)


    print(url)
    try:
        r = requests.get(url,headers = header)
    except:
        print("54 error occured at :)")
        f_ex.write("54 error occured at :)")

        time.sleep(120)

        r = requests.get(url, headers=header)

    soup = BeautifulSoup(r.content, 'html.parser')
    text = ''
    join_list = []

    count = 0

    for item in soup.find_all("a"):
        temp = str(item)

        if "onclick=\"view_cap" in str(item) and count != 1:
            count = 1
            #자막 페이지로 들어왔다.
            url = get_lylics_url(str(item))


            header["User-agent"] = str(ua.random)

            print(url)
            try:
                r = requests.get(url,headers = header)
            except:
                print("79 error occured at :)")
                f_ex.write("79 error occured at :)")

                time.sleep(120)

                r = requests.get(url, headers=header)
            soup = BeautifulSoup(r.content, "html.parser")
            soup_text = soup.get_text()

            tmp_list = soup_text.split("\n")

            for k in tmp_list:
                #print(k)
                text_list = clean_text(str(k))
                if len(text_list) != 0:
                    text_str = flatten(text_list)

                    if " " in text_str:
                        text_str = text_str.strip()
                        print(text_str)
                        f.write(text_str+"\n")


            #접속 거부를 막기위해 기다린다.
            time.sleep(3)









def get_lylics_url(url):

    url = url.split("view_cap(\'")[1].split("\');")[0]
    url_summed = "http://cineaste.co.kr/skin/board/apms-caption-new/view_caption.php?bo_table=psd_caption&fname=" + url


    return url_summed


def flatten(l):

    flatStr = ""
    for elem in l:
        flatStr += elem

    return flatStr


#이번엔 필요가 없을것 같다.
#한글만 추린다.
#text는 str
def clean_text(text):
    hangul = re.compile('[0-9ㄱ-ㅣ가-힣\s]+[ㄱ-ㅣ가-힣]')  # 한글과 띄어쓰기를 제외한 모든 글자

    #list로 반환된다.
    cleaned_text =  hangul.findall(text)

    return cleaned_text



# 수정 완료
# 페이지 리스트에서 들어갈 페이지의 url들을 모아서 리스트로 반환한다.
def extract_URL(tmp):
    header["User-agent"] = str(ua.random)

    # for the return value
    move_around_url = []

    print(tmp)
    try:
        r = requests.get(tmp,headers = header)
    except:
        print("153 error occured at :)")
        f_ex.write("153 error occured at :)")

        time.sleep(120)

        r = requests.get(tmp, headers=header)

    if r.status_code != 200:
        print("in valid url!! error code: %s" % (r.status_code))
        return

    soup = BeautifulSoup(r.content, 'html.parser')

    # at the first page (which have all the newses) ,scrab all urls which are available
    # new_url is in list format
    # get additional url in the queue , only when we turn into the next page (not at the side newses)

    for link in soup.find_all("a"):
        #페이지 리스트에서 보이는 각 영화에 대한 게시글의 링크.
        #<a href="http://cineaste.co.kr/bbs/board.php?bo_table=psd_caption&amp;wr_id=1225848"

        if "http://cineaste.co.kr/bbs/board.php?" in str(link.get('href'))  and "page=" in str(link.get('href')) and\
                "http://cineaste.co.kr/bbs/board.php?bo_table=psd_caption&wr_id=1094872&page=1" != str(link.get('href'))\
                and "http://cineaste.co.kr/bbs/board.php?bo_table=psd_caption&wr_id=870383&page=1" != str(link.get('href')):
            if link.get('class') == None:
                #print(link)
                extracted_ = link.get('href')
                #print(link)

                # 중복된거 안넣어야되
                if move_around_url.count(extracted_) < 1:
                    move_around_url.append(extracted_)
    #list로 반환한다.
    return move_around_url





# 페이지 리스트에서 한번 보고 30개에 대해 수행 -> 반복
def url_move_around_pages(start_url):



    header["User-agent"] = str(ua.random)

    next_page_url = start_url

    while next_page_url  != -1 :

        next_page_url = go_to_next_page(next_page_url)
        #print(next_page_url)

        # new url은 list 자료형이다.
        new_url = extract_URL(next_page_url)
        #print(new_url)

        # 현재 page에서 이제 page_list에서 보이는 기사들의 url들을 뽑아오자.
        # 한 페이지에 30개씩있다.
        for j in new_url:
            #print(j)
            f_ex.write(j + "\n")
            get_lylics_text(j)

#이상 없음
def check_is_valid_url(i):
    print(i)
    try:
        r = requests.get(i,headers = header)
    except:
        print("220 error occured")
        f_ex.write("220 error occured at :)")

        time.sleep(120)
        r = requests.get(i, headers=header)

    if r.status_code != 200:
        return -1
    else:
        return 1

#수정 완료
def go_to_next_page(section_url):
    global current_page


    # http://cineaste.co.kr/bbs//board.php?bo_table=psd_caption&  page=1000
    summed_url =  section_url.replace( "page=" + str(current_page)  ,  "page="+str(current_page+1) )

    print("current_page is %d"%current_page)

    current_page += 1

    if check_is_valid_url(summed_url) == 1 :
        print("current page is %d "%current_page)
        return summed_url
    else :
        print("summed url is invalid mabye end of the page")
        return -1


url_move_around_pages(url)


f.close()
f_ex.close()




