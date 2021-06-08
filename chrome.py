from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import threading

class Chrome:

    def __init__(self, personal=False, url='https://www.google.com/', skip=True):
        self.work = True
        self.skip = skip
        self.setInsDict()

        self.openChrome(personal, url)
        

        if self.skip:
            self.thread = threading.Thread(target=self.skipAD)
            self.thread.start()
        
    # 取得使用者名稱
    def getUsername(self):
        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(options=options)
        driver.get('chrome://version/')
        profile_path = driver.find_element_by_id('profile_path').text
        driver.close()
        return profile_path.split('\\')[2]
    
    # 回傳使用者名稱
    def returnUsername(self):
        return self.username
    
    # 打開chrome
    def openChrome(self, personal, url):
        options = webdriver.ChromeOptions()
        # 不顯示 '受控制' 的文字
        options.add_experimental_option("excludeSwitches", ['enable-automation'])
        # 開啟個人化介面
        if personal:
            options.add_argument('--user-data-dir=C:/Users/'+ self.getUsername() +'/AppData/Local/Google/Chrome/User Data')
        # 開啟chrome
        self.driver = webdriver.Chrome(options=options)
        # 前往指定頁面
        if url == '' or url == None:
            url = 'https://www.youtube.com/'
        self.driver.get(url)
    
    def setInsDict(self):
        self.insDict = {
            'play': 'k', # 播放/暫停
            'mute': 'm', # 靜音
            '+5': Keys.RIGHT, # 快轉5秒
            '-5': Keys.LEFT, # 倒轉5秒
            'voice+': Keys.UP, # 聲音變大
            'voice-': Keys.DOWN, # 聲音變小
            'full': 'f', # 全螢幕
            'movie': 't', # 劇院模式
            'cc': 'c', # 字幕
            'next': Keys.SHIFT + 'n', # 下一個
            'previous': Keys.SHIFT + 'p', # 上一個
        }

    # 執行Instruction
    def executeIns(self, key):
        if not self.work:
            return
        if key not in self.insDict:
            print('no this instruction')
            return
        if 'https://www.youtube.com/watch' in self.driver.current_url:
            print(str(key), ' ', end='')
            try:
                self.driver.find_element_by_id("movie_player").send_keys(self.insDict[key])
                print('ok')
            except:
                print('error')
    
    # 廣告處理
    def skipAD(self):
        while self.work and self.skip:
            # 影片廣告 -> 按 '略過廣告'
            try:
                ele = self.driver.find_elements_by_class_name('ytp-ad-text.ytp-ad-skip-button-text')
                if len(ele) > 0:
                    self.driver.execute_script('var vid = document.getElementsByClassName("video-stream html5-main-video")[0]; vid.currentTime = vid.duration;')
                    print('skip ad ok')
                    ele[0].click()
                    print('skip ad ok click')
            except:
                pass
                
            if not self.work:
                break
            # 不能略過的廣告
            try:
                ele = self.driver.find_elements_by_class_name('ytp-ad-text.ytp-ad-preview-text')
                if len(ele) > 0:
                    self.driver.execute_script('var vid = document.getElementsByClassName("video-stream html5-main-video")[0]; vid.currentTime = vid.duration;')
                    print('skip___ ad ok')
            except:
                pass
            
            if not self.work:
                break
            # 影片下方的橫條廣告 -> 按叉叉
            try:
                ele = self.driver.find_elements_by_class_name('ytp-ad-overlay-close-container')
                if len(ele) > 0:
                    self.driver.execute_script('document.getElementsByClassName("video-ads ytp-ad-module")[0].innerHTML="";')
                    print('down ad ok')
            except:
                pass

    def isClosed(self):
        try:
            if not self.work:
                return True
            self.driver.title
            return False
        except:
            self.work = False
            return True
