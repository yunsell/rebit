import time
import random

from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def naver_blog_content(driver, url):
    try:
        driver.get(url)
        driver.implicitly_wait(1)
        driver.switch_to.frame("mainFrame")
        driver.implicitly_wait(1)

        req = driver.page_source
        soup = BeautifulSoup(req, 'html.parser')

        if soup.find("div", attrs={"class": "se-main-container"}):  # se-component se-video se-l-default 제외
            text = soup.find("div", attrs={"class": "se-main-container"})
            if soup.find("div", attrs={"class": "se-component se-video se-l-default"}):
                unwanted = text.find("div", attrs={"class": "se-component se-video se-l-default"})
                unwanted.decompose()
            text = text.get_text()
            text = text.replace("\n", "").replace("\u200b", "").replace("​", "").replace(" ", "")  # 공백 제거
            # content_blog.append(text)
            content_blog = text
        elif soup.find("div", attrs={"id": "postViewArea"}):
            text = soup.find("div", attrs={"id": "postViewArea"}).get_text()
            text = text.replace("\n", "")  # 공백 제거
            # content_blog.append(text)
            content_blog = text
        elif soup.find("div", attrs={"id": "postListBody"}):
            text = soup.find("div", attrs={"id": "postListBody"}).get_text()
            text = text.replace("\n", "")  # 공백 제거
            # content_blog.append(text)
            content_blog = text
        else:
            print("본문 없음")
            # content_blog.append(text)
            content_blog = 'none'

        if soup.find("em", attrs={"class": "u_cnt _count", "style": "display: none;"}):
            text = soup.find("em", attrs={"class": "u_cnt _count", "style": "display: none;"})  #
            # print(text)
            try:
                # gonggam.append((int(text.get_text())))
                gonggam = (int(text.get_text()))
            except:
                # gonggam.append(0)
                gonggam = 0
        elif soup.find("em", attrs={"class": "u_cnt _count"}):
            text = soup.find("em", attrs={"class": "u_cnt _count"})
            # print(text)
            try:
                # gonggam.append((int(text.get_text())))
                gonggam = (int(text.get_text()))
            except:
                # gonggam.append(0)
                gonggam = 0
        else:
            print("공감 요소 없음")
            # gonggam.append('none')
            gonggam = 0

        if soup.find("em", attrs={"class": "_commentCount"}):  # null일 경우 0
            text = soup.find("em", attrs={"class": "_commentCount"})
            try:
                # commentCount.append(int(text.get_text()))
                commentCount = int(text.get_text())
            except:
                # commentCount.append(0)
                commentCount = 0
        else:
            print("댓글 요소 없음")
            # commentCount.append('none')
            commentCount = 0
    except:
        content_blog = 'none'
        gonggam = 0
        commentCount = 0

    return content_blog, gonggam, commentCount


def naver_blog_comment(driver, url):
    id_index_start = url.find('com/') + 4
    if 'Redirect' in url:
        id_index_end = url.find('?')
        log_index = url.find('logNo=') + 6
    else:
        id_index_end = url.find('/', id_index_start)
        log_index = url.find('/', id_index_end)+1


    blogId = url[id_index_start:id_index_end]
    logNo = url[log_index:]


    url = "https://m.blog.naver.com/CommentList.nhn?blogId="+blogId+"&logNo="+logNo
    result = []

    driver.get(url)

    try:
        WebDriverWait(driver, 1).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        alert.dismiss()
    except:
        try:
            WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span.u_cbox_nick')))
            names = driver.find_elements(By.CSS_SELECTOR, 'span.u_cbox_nick')
            dates = driver.find_elements(By.CSS_SELECTOR, 'span.u_cbox_date')
            contents = driver.find_elements(By.CSS_SELECTOR, 'span.u_cbox_contents')
            for name, content, date in zip(names, contents, dates):
                result.append([name.text, content.text, date.text])
            return result
        except:
            result = []

    return result

def naver_cafe_comment(driver, url):
    result = []

    driver.get(url)
    time.sleep(1 + random.uniform(0, 1))

    driver.switch_to.frame('cafe_main')

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    try:
        WebDriverWait(driver, 1).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        alert.dismiss()
    except:
        try:
            if (soup.select('div.Article')[0].text) == '':
                return False
            else:
                title = soup.select('h3.title_text')[0].text.strip()
                views = soup.select('span.count')[0].text.replace('조회 ', '')
                datetime = soup.select('span.date')[0].text
                try:
                    content = soup.select('div.se-main-container')[0].text
                except:
                    content = soup.select('div.ContentRenderer')[0].text

                # like = int(soup.select('em.u_cnt._count')[0].text)

                author = list(map(lambda author: author.text.strip(), soup.select('div.comment_nick_box')))
                all_reply = list(map(lambda reply: reply.text, soup.select('span.text_comment')))
                commentdate = list(map(lambda dates : dates.text, soup.select('span.comment_info_date')))
                for name, content, date in zip(author, all_reply, commentdate):
                    result.append([name, content, date.replace('. ', ' ')])
                return result
        except Exception as e:
            print(e)

    return result