from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from webbrowser import open_new_tab
from requests import get, post
from requests.structures import CaseInsensitiveDict
from datetime import datetime
from plyer import notification
from json import load
from time import time, sleep
from pathlib import Path
from distutils.util import strtobool
from argparse import ArgumentParser
from rich.console import Console
from rich.text import Text



config = load(open(f'{Path(__file__).parent}/config/config.json'))



class ProlificUpdater:
    def __init__(self, bearer = None):
        if bearer: self.bearer = bearer
        else: self.bearer = "Bearer " + self.get_bearer_token()
        self.oldResults = list()
        self.participantId = config["Prolific_ID"]

    def getRequestFromProlific(self):
        url = "https://internal-api.prolific.co/api/v1/studies/?current=1"
        headers = CaseInsensitiveDict()
        headers["Accept"] = "application/json, text/plain, */*"
        headers["Authorization"] = self.bearer
        return get(url, headers=headers)

    def reservePlace(self, id):
        url = "https://internal-api.prolific.co/api/v1/submissions/reserve/"
        headers = CaseInsensitiveDict()
        headers["Accept"] = "application/json"
        headers["Authorization"] = self.bearer
        postObj = {"study_id": id, "participant_id": self.participantId}
        return post(url, headers=headers, data = postObj)

    def getResultsFromProlific(self):
        try:
            response = self.getRequestFromProlific()
        except:
            print("Network error")
            notification.notify(
                title="Prolific update error {}".format(datetime.now().strftime("%H:%M:%S")),
                app_name="Prolific updater",
                message="Network error!",
                app_icon=f"{Path(__file__).parent}/assets/Paomedia-Small-N-Flat-Bell.ico",
                timeout=50
            )
            return list()
        if response.status_code == 200:
            return response.json()['results']
        else:
            if not strtobool(config["auto_renew_bearer"]):
                print("Response error {}".format(response.status_code))
                print("Response error {}".format(response.reason))
                notification.notify(
                    title="Prolific update error {}".format(datetime.now().strftime("%H:%M:%S")),
                    app_name="Prolific updater",
                    message="Bearer error!",
                    app_icon=f"{Path(__file__).parent}/assets/Paomedia-Small-N-Flat-Bell.ico",
                    timeout=50
                )
                return list("bearer")
            else:
                self.bearer = self.get_bearer_token()
                self.getResultsFromProlific()
            
    
    def get_bearer_token(self) -> str:
        print("Getting a new bearer token...")
        pageurl = 'https://internal-api.prolific.co/auth/accounts/login/'

        options = Options()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-site-isolation-trials')
        options.add_argument('--headless')
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options= options)
        driver.get(pageurl)
        print("Driver launched")

        site_key = "6LeMGXkUAAAAAOlMpEUm2UOldiq38QgBPJz5-Q-7" #Prolific site key
        api_key = config["2captcha_api_key"]
        form = {"method": "userrecaptcha",
                "googlekey": site_key,
                "key": api_key, 
                "pageurl": pageurl, 
                "json": 1}

        response = post('http://2captcha.com/in.php', data=form)
        request_id = response.json()['request']
        url = f"http://2captcha.com/res.php?key={api_key}&action=get&id={request_id}&json=1"
        status = 0
        start = time()
        print("Trying to bypass captcha...")
        while not status:
            res = get(url)
            if res.json()['status']==0:
                print("Failed, retrying...")
                sleep(3)
            else:
                end = time()
                print(f"Captcha solved in {end-start}s")
                driver.execute_script(f'document.getElementsByName("username")[0].value = "{config["mail"]}"')
                driver.execute_script(f'document.getElementsByName("password")[0].value = "{config["password"]}"')
                requ = res.json()['request']
                driver.execute_script(f'document.getElementById("g-recaptcha-response-100000").innerHTML="{requ}";')
                driver.find_element(By.ID, "login").submit()
                sleep(3)
                if driver.current_url =="https://internal-api.prolific.co/auth/accounts/login/":
                    status = 0
                    print("Failed to log in, retrying...")
                    driver.get(pageurl)
                    sleep(3)
                    start = time()
                    continue
                status = 1
                print(f"Refresh {driver.current_url}")
                driver.refresh()
                while True:
                    for request in driver.requests:
                        if request.response:
                            if request.url.startswith("https://internal-api.prolific.co/openid/authorize?client_id="):
                                new_bearer = request.response.headers['location'].split("&")[0].split("access_token=")[-1]
                                print(f"Got a new bearer token ! : {new_bearer}")
                                return new_bearer
                        sleep(0.5)


    def executeCycle(self):
        results = self.getResultsFromProlific()
        if results:
            if results != self.oldResults:
                self.reservePlace(id = results[0]["id"])
                notification.notify(
                    title="Prolific update {}".format(datetime.now().strftime("%H:%M:%S")),
                    app_name="Prolific updater",
                    message="New studies available!",
                    app_icon=f"{Path(__file__).parent}/assets/Paomedia-Small-N-Flat-Bell.ico",
                    timeout=50
                )
                a_website = "https://app.prolific.co/studies"  # TODO: open url in results
                open_new_tab(a_website)
        
        self.oldResults = results
        
        if results:
            return True
        else:
            if results == ["bearer"]:
                exit("Bearer token not valid anymore, need to change it !")
            return False    

def parseArgs():
    parser = ArgumentParser(description='Keep updated with Prolific')
    parser.add_argument('-b', '--bearer', type=str, help='bearer token')
    args = parser.parse_args()
    try:
        return {"bearer": "Bearer " + args.bearer}
    except TypeError:
        pass



if __name__ == "__main__":
    myArguments = parseArgs()
    if strtobool(config["auto_renew_bearer"]) and not myArguments:
        p_updater = ProlificUpdater()
    else:
        p_updater = ProlificUpdater(bearer = myArguments["bearer"])

    console = Console()
    status =  console.status("[bold blue] Waiting for study...",spinner="arc")
    status.start()
    while (True):
        updateTime = 10
        if(p_updater.executeCycle()):
            status.stop()
            text = Text("Study found !")
            text.stylize("bold red")
            console.print(text)
            updateTime = 15
        else:
            updateTime = 10
        # sleep for 10 sec
        sleep(updateTime)
        
