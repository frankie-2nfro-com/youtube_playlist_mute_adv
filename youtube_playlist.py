from selenium import webdriver
#from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.common.by import By 
import re
import time
import osascript
import json

"""
from selenium.webdriver import ActionChains as A
act = A(driver)
act.send_keys("M").perform()
"""





class YouTubeVideo:
    def __init__(self, volume=10):
        self.volume = volume 

        chromeOptions = webdriver.ChromeOptions()
        #chromeOptions.add_argument("--headless") # make it not visible, just comment if you like seeing opened browsers
        chromeOptions.add_argument("--window-size=1024,1024")	
        chromeOptions.add_argument("disable-infobars");	
        chromeOptions.add_argument("--disable-extensions");
        chromeOptions.add_argument("--disable-gpu");
        chromeOptions.add_argument("--disable-dev-shm-usage");
        chromeOptions.add_argument("--no-sandbox");		
        self.web = webdriver.Chrome(options=chromeOptions)

        #self.wait = WebDriverWait(self.web, 600)

        # go to youtube, login and accept cookie
        self.web.get("https://www.youtube.com")
        while True:
            try:
                cookieButton = self.web.find_element(by=By.XPATH, value='//*[@id="content"]/div/div[6]/div[1]/ytd-button-renderer[2]/a')
                cookieButton.click()
                break
            except:
                pass

            try:
                agreeButton = self.web.find_element(by=By.XPATH, value='//*[@id="content"]/div[2]/div[5]/div[2]/ytd-button-renderer[2]/a')
                agreeButton.click()
                break
            except:
                pass


    def destroy(self):
        self.web.close()
        self.web.quit()

    def loadNextTube(self):
        # open json file and pop first record, then update json and save back
        file = open("youtube_playlist.json", "r", encoding='UTF-8')
        listInfo = file.read()
        playList = json.loads(listInfo)
        file.close()
        
        if len(playList)==0:
            return False

        # set mute before load the video
        self.setComputerMute(True)

        url = playList.pop(0)
        if url is None:
            return False

        print("Try video link: " + url)
        self.web.get(url)

        # update playList json file
        with open("youtube_playlist.json", "w", encoding='UTF-8') as outfile:
            json.dump(playList, outfile)

        return True

    def setComputerMute(self, isMute):
        code, out, err = osascript.run("output volume of (get volume settings)")

        if isMute and int(out)>0:
            print("Mute video sound from " + out)
            osascript.osascript("set volume output volume 0")
        elif not isMute and int(out)==0:
            print("Resuming video sound to " + str(self.volume))
            osascript.osascript("set volume output volume " + str(self.volume))

    def getPlayStatus(self):
        try:
            player_status = self.web.execute_script("return document.getElementById('movie_player').getPlayerState()")
            print(player_status)
        except:
            time.sleep(0.1)
            return self.getPlayStatus()

        try:
            advInterface = self.web.find_element(by=By.XPATH, value="//*[contains(@id, 'player-overlay')]")
            # if no exception, mute adv sound
            self.setComputerMute(True)
        except:
            if player_status==1:
                self.setComputerMute(False) 

        return player_status

    def playStart(self):
        while True:
            try:
                but = self.web.find_element(by=By.XPATH, value='//*[@id="movie_player"]')
                but.click()
                break
            except:
                pass

        print("video starts playing")

    def try_skip_adv(self):
        try:
            skipAdvButton = self.web.find_element(by=By.XPATH, value="//*[contains(@id, 'skip-button')]/span/button")
            print("Adv skip button found! Try to skip advertisment...")
            self.setComputerMute(True)
            skipAdvButton.click()
        except:
            pass









ytube = YouTubeVideo()
time.sleep(1)

videoLoaded = ytube.loadNextTube()
if videoLoaded:
    ytube.playStart()

while videoLoaded:
    player_status = ytube.getPlayStatus()
    
    if player_status==0:            # play to end
        print("Video is ended. Try to load next video...")
        videoLoaded = ytube.loadNextTube()
        continue
    elif player_status==1:          # playing
        ytube.try_skip_adv()
    elif player_status==2:          # pause
        print("Manually skip this video")
        videoLoaded = ytube.loadNextTube()
        continue        
    elif player_status==-1:         # advertisment
        ytube.try_skip_adv()

    time.sleep(0.1)

ytube.destroy()




