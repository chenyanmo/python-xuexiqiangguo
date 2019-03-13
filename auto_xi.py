from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait  # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC  # available since 2.26.0
from time import sleep
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import logging
from selenium.common.exceptions import TimeoutException
import threading


class AutoControl():
    main_url = 'https://www.xuexi.cn'
    caps = DesiredCapabilities().FIREFOX
    caps["pageLoadStrategy"] = "eager"
    login_url = 'https://pc.xuexi.cn/points/login.html?ref=https://pc.xuexi.cn/points/my-study.html'
    mypoints = '/points/my-points.html'
    scroll_js = '''
clientheight=document.body.scrollHeight
var position=0
function startscroll(){
if(position<clientheight){position++;window.scrollTo(0,position);console.log(position)}
if(position>=clientheight){position=0;window.scrollTo(0,0);console.log(position)}
}
setInterval(startscroll,20)
'''
    toMiddle = '''clientheight=document.body.scrollHeight
    var position=clientheight/2
    window.scrollTo(0,position)'''

    news_path = '//div[@class="screen"]/div[2]/div[2]/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]' \
                '/div[1]/div[%d]'

    shijian_path = '//div[@class="screen"]/div[1]/div[2]/div[1]/div[2]/div[1]/div[%d]/div[1]'
    video_path = '//div[@class="screen"]/div[1]/div[2]/div[1]/div[3]/div[1]/div[%d]/div[1]/div[1]'

    def __init__(self, option):
        if option == 'Chrome':
            self.driver = webdriver.Chrome()
            # self.driver.set_page_load_timeout(20)
        elif option == 'Firefox':
            self.driver = webdriver.Firefox(desired_capabilities=self.caps)
        else:
            print('Warning')
            print('______________________________________________________________________')
            print("            we don't support other browser currently")

    # for opening the main page directly
    def open(self, url=main_url):
        logging.info("loading main page")
        self.driver.get(url)

    # login with mobile scanning
    def login(self):
        self.driver.get(self.login_url)

        element = WebDriverWait(self.driver, 90).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="top-div"]')))
        self.load_main_page()

    def load_main_page(self):
        print("loading main page...")
        self.open(self.main_url)
        print("loading complete")

    def study(self):
        # read 6 articles
        self.study_shijian(7)
        self.close_session()
        sleep(2)
        self.watch_tv(7)
        self.close_session()

    def multi_article(self, times):
        sleep(3)
        for time in range(1, times):
            try:
                self.study_article(time)
            except:
                logging.warning("reading failed, reading next article")

    def study_article(self, number):
        logging.info("reading the %d article" % number)
        try:
            article = self.driver.find_element_by_xpath(self.news_path % number)
            article.click()
            self.driver.switch_to.window(self.driver.window_handles[1])
            self.reading_action()
            sleep(5)
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
        except:
            self.driver.switch_to.window(self.driver.window_handles[0])

    # execute a javascript to scroll window
    def reading_action(self):
        self.driver.execute_script(self.scroll_js)
        sleep(10)

    # reading articles from xuexishijian
    def study_shijian(self, number):
        shijian = self.driver.find_element_by_xpath('//div[@class="shijian"]')
        WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="shijian"]')))
        shijian.click()
        logging.info("reading news %d" % number)
        self.driver.switch_to.window(self.driver.window_handles[1])
        element = WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="screen"]')))
        for n in range(1, number):
            print("start reading article of %d"
                  % n)
            try:
                stale = True
                while stale:
                    try:
                        article = self.driver.find_element_by_xpath(self.shijian_path % n)
                        WebDriverWait(self.driver, 30).until(
                            EC.element_to_be_clickable((By.XPATH, self.shijian_path % n)))
                        article.click()
                        stale = False
                    except:
                        stale = True
                sleep(1)
                self.driver.switch_to.window(self.driver.window_handles[2])
                self.reading_action()
                # reading duration
                sleep(300)
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[1])
                print("finished")
            except Exception as e:
                print(e)
                logging.warning("reading failed try for next article")

    # back to main page
    def close_session(self):
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

    # watch videos
    def watch_tv(self, times):
        tv = self.driver.find_element_by_xpath(
            '//div["class=screen"]/div[2]/div[2]/div[2]/div[2]/div[1]/div[5]/div[2]/div[1]/div')
        print(tv.text)
        sleep(3)
        tv.click()
        self.driver.switch_to.window(self.driver.window_handles[1])
        # wait until appearance of video 1
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.XPATH, self.video_path % 1)))

        for time in range(1, times):
            retry = 0
            try:
                stale = True
                while stale:
                    try:
                        video = self.driver.find_element_by_xpath(self.video_path % time)
                        print('viewing: ' + video.text)
                        sleep(2)
                        video.click()
                        stale = False
                    except:
                        stale = True

                self.driver.switch_to.window(self.driver.window_handles[2])
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'video')))
                content = self.driver.find_element_by_xpath("//video")
                self.driver.execute_script(self.toMiddle)
                ActionChains(self.driver).move_to_element(content).perform()
                sleep(3)
                duration = 0
                while duration == 0 and retry < 5:
                    sleep(1)
                    ActionChains(self.driver).move_to_element(content).perform()
                    try:
                        ActionChains(self.driver).move_to_element(content).perform()
                        duration = self.parse_time(self.driver.find_element_by_xpath('//span[@class="duration"]').text)
                    except Exception as e:
                        print(e)
                        duration = 0
                        retry = retry + 1

                print('video length:' + str(duration))
                # video watching duration
                sleep(duration)
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[1])
            except Exception as e:
                print(e)
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[1])
                print("failed, trying next video")

    # parse the time in minute into seconds
    def parse_time(self, duration):
        duration = duration.strip(' ')
        dur = duration.split(':')
        time_in_second = int(dur[0]) * 60 + int(dur[1])
        return time_in_second


def main():
    option = input("select 1 for Chrome,2 for Firefox")
    if option == '1':
        auto = AutoControl('Chrome')
    elif option == '2':
        auto = AutoControl('Firefox')
    else:
        print("we do not support!")
        return main()
    return auto

try:
    auto = main()
    auto.login()
    sleep(5)
    auto.study()
except TimeoutException:
    print('网速过慢，建议不学习')

