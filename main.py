import platform
import random
from argparse import ArgumentParser
from distutils.util import strtobool
from json import load
from pathlib import Path
from time import sleep, time
from webbrowser import open_new_tab

from playsound import playsound
from requests import Response, get, post
from requests.structures import CaseInsensitiveDict
from rich.console import Console
from rich.text import Text
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager

if platform.system() == "Windows":
    import ctypes
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
config = load(open(f"{Path(__file__).parent}/config/config.json"))


class ProlificUpdater:
    def __init__(self, bearer=None):
        if bearer:
            self.bearer = bearer
        else:
            self.bearer = "Bearer " + self.get_bearer_token()
        self.oldResults = list()
        self.participantId = config["Prolific_ID"]

    def getRequestFromProlific(self) -> Response:
        url = "https://internal-api.prolific.com/api/v1/participant/studies/"
        headers = CaseInsensitiveDict()
        headers["Accept"] = "application/json, text/plain, */*"
        headers["Authorization"] = self.bearer
        headers["x-legacy-auth"] = "false"
        return get(url, headers=headers)

    def reservePlace(self, id) -> Response:
        url = "https://internal-api.prolific.com/api/v1/submissions/reserve/"
        headers = CaseInsensitiveDict()
        headers["Accept"] = "application/json"
        headers["Authorization"] = self.bearer
        headers["x-legacy-auth"] = "false"
        postObj = {"study_id": id, "participant_id": self.participantId}
        return post(url, headers=headers, data=postObj)

    def getResultsFromProlific(self) -> list:
        try:
            response = self.getRequestFromProlific()
        except Exception:
            console.print("[bold red][+] Network error[/bold red]")
            return list()
        if response.status_code == 200:
            return response.json()["results"]
        else:
            if not strtobool(config["auto_renew_bearer"]):
                print("Response error {}".format(response.status_code))
                print("Response error {}".format(response.reason))
                return list("bearer")
            else:
                self.bearer = self.get_bearer_token()
                self.getResultsFromProlific()

    def get_bearer_token(self) -> str:
        print("[+] Getting a new bearer token...")
        pageurl = "https://auth.prolific.com/u/login"

        options = Options()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_argument("--disable-web-security")
        options.add_argument("log-level=3")
        options.add_argument("--disable-site-isolation-trials")
        options.add_argument("--headless")
        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()), options=options
        )
        print("Driver started")
        driver.get(pageurl)
        isLoggedIn = False
        # start = time()
        while not isLoggedIn:
            print("Login in...")
            # anchor_url = "https://www.recaptcha.net/recaptcha/api2/anchor?ar=1&k=6LeMGXkUAAAAAOlMpEUm2UOldiq38QgBPJz5-Q-7&co=aHR0cHM6Ly9pbnRlcm5hbC1hcGkucHJvbGlmaWMuY286NDQz&hl=fr&v=gWN_U6xTIPevg0vuq7g1hct0&size=invisible&cb=igv4yino6y0f"
            # reCaptcha_response = reCaptchaV3(anchor_url)
            # end = time()
            # print(f"Captcha solved in {end-start}s")

            # Wait for the page to be fully loaded
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[@type='submit']")))

            # Continue with the rest of the code
            driver.execute_script(
                f'document.getElementsByName("username")[0].value = "{config["mail"]}"'
            )
            driver.execute_script(
                f'document.getElementsByName("password")[0].value = "{config["password"]}"'
            )
            driver.find_element(By.XPATH, '//button[@type="submit"]').click()
            
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "image-container")))

            if driver.current_url == "https://auth.prolific.com/u/login":
                isLoggedIn = False
                print("[-] Failed to log in, retrying in 3s...")
                driver.get(pageurl)
                sleep(3)
                # start = time()
                continue
            isLoggedIn = True
            print("Logged in !")
        driver.refresh()
        print('[+] Retrieving bearer token from requests...')
        while True:
            for request in driver.requests:
                if "https://internal-api.prolific.com/api/v1/" in request.url:
                    try:
                        new_bearer = request.headers["Authorization"]
                        #print(new_bearer)
                        print(f"Got a new bearer token ! : {new_bearer}\n")
                        return new_bearer
                    except Exception:
                        pass
            sleep(0.5)

    def executeCycle(self) -> bool:
        results = self.getResultsFromProlific()
        print("results : ", results)
        if results:
            if results != self.oldResults:
                currency_symbol = "£" if str(results[0]["study_reward"]["currency"]) == "GBP" else "$"
                console.print(
                    f"""Trying to join {results[0]["name"]} ([bold green]{currency_symbol}{str(float(results[0]["study_reward"]["amount"])/100)}[/bold green])"""
                )
                reserve_place_res = self.reservePlace(id=results[0]["id"])
                if reserve_place_res.status_code == 400:
                    console.print(f"""[bold red][+] Error code {str(reserve_place_res.json()["error"]["error_code"])}
                                      \nTitle : {str(reserve_place_res.json()["error"]["title"])}
                                      \nDetails : {str(reserve_place_res.json()["error"]["detail"])}""")
                    self.oldResults = results
                    return False
                else:
                    playsound(rf"{Path(__file__).parent}\alert.wav", True)
                    a_website = "https://app.prolific.com/studies"
                    open_new_tab(a_website)

        self.oldResults = results

        if results:
            return True
        else:
            if results == ["bearer"]:
                exit("Bearer token not valid anymore, need to change it !")
            return False


def parseArgs() -> dict:
    parser = ArgumentParser(description="Keep updated with Prolific")
    parser.add_argument("-b", "--bearer", type=str, help="bearer token")
    args = parser.parse_args()
    try:
        return {"bearer": "Bearer " + args.bearer}
    except TypeError:
        pass


if platform.system() == "Windows":

    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

    def get_idle_duration():
        lii = LASTINPUTINFO()
        lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
        if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii)):
            millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
            seconds = millis / 1000
            return seconds
        else:
            error_code = (
                ctypes.windll.kernel32.GetLastError()
            )  # Get the last error code
            print(f"Error code: {error_code}")
            return 0  # Handle the error as needed

    def pause_script():
        print("Pausing script...")
        while True:
            idle_duration = get_idle_duration()
            if idle_duration > 600:  # 10 minutes in seconds
                print(
                    f"Idle Time: {idle_duration} seconds [script paused after 10 minutes of inactivity, to avoid temp ban from the API due to overuse]"
                )
                sleep(10)
            else:
                print("Resuming script...")
                break


if __name__ == "__main__":
    myArguments = parseArgs()
    if strtobool(config["auto_renew_bearer"]) and not myArguments:
        p_updater = ProlificUpdater()
    else:
        p_updater = ProlificUpdater(bearer=myArguments["bearer"])

    console = Console()
    status = console.status("[bold blue] Waiting for study...", spinner="arc")
    status.start()
    while True:
        updateTime = config["wait_time"]
        if p_updater.executeCycle():
            status.stop()
            text = Text("Study found !")
            text.stylize("bold red")
            console.print(text)
            sleep(5)
            input("Press enter to resume study search")
            status.start()

        if strtobool(config["pause_on_idle"]) and platform.system() == "Windows":
            idle_duration = get_idle_duration()
            if idle_duration >= 600:  # 10 minutes in seconds
                pause_script()
            # else:
            #     print(f"Idle Time: {idle_duration} seconds [script not paused]") #leave commented if not debugging

        # Generate a random integer between -5 and 5
        random_offset = random.randint(-5, 5)

        # Generate a random number which is +/- 5 from the updateTime variable
        random_time = updateTime + random_offset
        sleep(
            random_time if random_time >= 0 else 0
        )  # if statement covers edge case, if the user sets up <5 wait_time (I found <20 results in a temp ban), which with the use of random above, could result in a negative number being passed to the sleep()
