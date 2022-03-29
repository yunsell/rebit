from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

def daum_content(driver, url):
    driver.get(url)
    try:  # 블로그 본문
        if url.startswith("https://blog.naver.com"):
            article = (driver.find_element(By.CLASS_NAME, "cContentBody"))
            gonggam = (driver.find_element(By.CLASS_NAME, "txt_like uoc-count"))
            comment = (driver.find_element(By.ID, "commentCount326_2"))
    except NoSuchElementException:
        article

    return article, gonggam, comment

def daum_blog_comment(driver, url):
    result = []

    try:
        driver.get(url)
    except Exception as e:
        print('사이트 오류')
        return result
    names = []
    contents = []
    dates = []

    if 'tistory' in url:
        try:
            if driver.find_elements(By.CLASS_NAME, 'comment-content'):
                names = driver.find_elements(By.CLASS_NAME, 'comment-author')
                dates = driver.find_elements(By.CLASS_NAME, 'comment-date')
                contents = driver.find_elements(By.CLASS_NAME, 'comment-content')
                contents = list(map(lambda x: x.text, contents))
            elif driver.find_elements(By.CLASS_NAME, 'author_info'):
                names = driver.find_elements(By.XPATH, "//div[@class='author_info']/div/a[2]")
                dates = driver.find_elements(By.XPATH, "//div[@class='comment_body']//span[@class='date']")
                contents = driver.find_elements(By.XPATH, "//div[@class='comment_body']")
                contents = list(map(lambda x:'\n'.join(x.text.split('\n')[2:-1]), contents))
            elif driver.find_elements(By.CLASS_NAME, 'rp_general'):
                names = driver.find_elements(By.XPATH, "//div[@class='info']/span[@class='name']")
                dates = driver.find_elements(By.XPATH, "//div[@class='info']/span[@class='date']")
                contents = driver.find_elements(By.XPATH, "//div[@class='info']/following-sibling::p")
                contents = list(map(lambda x: x.text, contents))
            else :
                result = []
            for name, content, date in zip(names, contents, dates):
                if content == '비밀댓글입니다':
                    continue
                result.append([name.text, content, date.text[:16]])
        except Exception as e:
            print('tistory Error:', e)
    elif 'daum' in url:
        try:
            if driver.find_elements(By.CLASS_NAME, 'opinionListMenu'):
                names = driver.find_elements(By.XPATH, "//div[@class='commentList']//li[@class='fl']")
                dates = driver.find_elements(By.XPATH, "//div[@class='commentList']//li[@class='sDateTime']")
                contents = driver.find_elements(By.XPATH, "//div[@class='commentList']//div[@class='cont']")
            elif driver.find_elements(By.CLASS_NAME, 'list-reply'):
                names = driver.find_elements(By.XPATH, "//div[@class='box-content']/div[@class='box-meta']/strong")
                dates = driver.find_elements(By.XPATH, "//div[@class='box-content']//span[@class='date']")
                contents = driver.find_elements(By.XPATH, "//div[@class='box-content']/p[@class='text']")
            else:
                result = []
            for name, content, date in zip(names, contents, dates):
                if content == '비밀댓글입니다':
                    continue
                result.append([name.text, content.text, date.text.replace(' ', '')[:16]])
        except Exception as e:
            print('daum Error:', e)
    else:
        print('크롤링 모듈 미개발', end = ' ')

    return result