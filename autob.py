#!/usr/bin/env python3
from unittest import result
from selenium import webdriver
import chromedriver_autoinstaller_fix
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
import subprocess, platform
from re import search
from cryptography.fernet import Fernet
import os.path
import sys
import sysconfig
import winreg
from win32com.client import Dispatch
from subprocess import CREATE_NO_WINDOW # This flag will only be available in windows
import ctypes

# Checking if executed from compiled ("frozen") exe or from a py file and adds current working directory to path so variables can be dynamically imported when running exe file
if getattr(sys, 'frozen', False):
    app_path = os.path.dirname(sys.executable)
    sys.path.append(app_path)
else:
    app_path = os.path.dirname(os.path.abspath(__file__))

# Import from external variables file
import variables

program_name = "autob"

MessageBox = ctypes.windll.user32.MessageBoxW

def findnthoccurrence(str, char, n):
    '''
    Extract the position in string of a specified character (the nth occurrence)
    '''
    count = str.count(char)
    if count < n:
        return -1
    index = -1
    for i in range(n):
        index = str.index(char, index + 1)
    return index

def extractpathurl(str):
    '''
    If str = https://bonjour.com/weuhriu/ewrweurh/rtyrtu
    Returns = /weuhriu/ewrweurh/rtyrtu
    '''
    return str[findnthoccurrence(str, '/', 3):]

def quitandclose():
    sys.exit(0)
 
def ping(host):
    '''
    Ping devices from this script
    '''
    # Detects whether the operating system is Windows, if so, variable set to True, otherwise False
    isWin = platform.system().lower() == "windows"
    # 'try' allows you to handle errors if any (to customize the display, for example)
    try:
        # Allows you to run the ping command on the system terminal and adapts its syntax according to the OS: 'n' for Windows; 'c' for Linux
        output = subprocess.check_output("ping -{} 1 {}".format('n' if isWin else 'c', host), shell=True)
        # If Windows
        if isWin:
            # If the regex matches (and therefore the ping worked), return True
            if search("[0-9] *ms", str(output)):
                return True
            # Else False
            else:
                return False
    # If error, then:
    except Exception as e:
        print("Error:", e)
        return False

    # If ping Linux OK, return True
    return True

def myPopupAskQuestion(message):
    result = MessageBox(None, message, program_name, 0x1000 | 0x30 | 0x4) # Respectively: MB_SYSTEMMODAL | MB_ICONWARNING | MB_YESNO
    if result == 6:
        return 'yes'
    elif result == 7:
        return 'no'
    return 'error'

def myPopupShowInfo(message):
    result = MessageBox(None, message, program_name, 0x1000 | 0x40) # Respectively: MB_SYSTEMMODAL | MB_ICONINFORMATION
    return result

def myPopupShowError(message):
    result = MessageBox(None, message, program_name, 0x1000 | 0x10) # Respectively: MB_SYSTEMMODAL | MB_ICONSTOP
    return result

def confirmStart(toprint = None):
    if toprint:
        MsgBox = myPopupAskQuestion(toprint + '\nWould you like to badge now?')
    else:
        MsgBox = myPopupAskQuestion('Would you like to badge now?')

    if MsgBox == 'yes':
        MsgBox = myPopupAskQuestion('Are you sure?')
        if MsgBox == 'no':
            # Exit program
            quitandclose()
    else:
        # Exit program
        quitandclose()

def decrypt(token: bytes, key: bytes) -> bytes:
    '''
    Decrypt a token with a key
    '''
    try:
        result = Fernet(key).decrypt(token)
    except Exception as e:
        myPopupShowError("Looks like the key linked to your password has changed, please regenerate your password's hash with the new key and paste the result in \"variables.py\".")
        sys.exit(1)
    return result

def mykeygen() -> bytes:
    '''
    Generate a key and store it in a file
    '''
    # Does the key already exists?
    if os.path.isfile(".key"):
        # If yes, read it
        with open(".key", "rb") as file:
            key = file.read()
    else:
        # If no, generate it and write it in a file
        key = Fernet.generate_key()  # store in a secure location
        with open(".key", "wb") as file:
            file.write(key)
    # Encode the key in bytes if it is not already
    if type(key) != bytes:
        key = key.encode("utf-8")
    return key

def get_reg(name, path):
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0,
                                       winreg.KEY_READ)
        value, regtype = winreg.QueryValueEx(registry_key, name)
        winreg.CloseKey(registry_key)
        return value
    except WindowsError:
        return None

# ----

###
# Main program
###

def main():
    # Set DPI Awareness on current process (Properties / Compatibility / Change high DPI settings / Override high DPI scaling behavior. Scaling performed by: System)
    os.environ.update({"__COMPAT_LAYER": "DpiUnaware"}) # For "System"
    # os.environ.update({"__COMPAT_LAYER": "HighDpiAware"}) # For "Application"
    # os.environ.update({"__COMPAT_LAYER": "GdiDpiScaling DpiUnaware"}) # For "System (Enhanced)"
    # Sources : https://www.reddit.com/r/SCCM/comments/dlwblz/setting_per_application_dpi_settings/
    # https://stackoverflow.com/questions/37878185/what-does-compat-layer-actually-do
    # https://superuser.com/questions/1623879/force-scaling-performed-by-application-for-all-apps

    # Get or create the key use for password encryption
    mykey = mykeygen()

    i = 0
    while not ping(variables.address_to_ping_company_net):
        myPopupShowInfo("We are unable to access the " + variables.company_name + " network.\nCheck that you are connected to the VPN before clicking 'OK' to try again!")
        i += 1
        if i >= 5:
            quitandclose()

    chrome_path = chromedriver_autoinstaller_fix.install(path = ".")

    start_time = time.perf_counter()
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument('--no-startup-window')
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--blink-settings=imagesEnabled=false')
    chrome_options.add_argument('user-data-dir=C:\Temp\ChromeProfile')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    chrome_service = ChromeService(chrome_path)
    chrome_service.creation_flags = CREATE_NO_WINDOW

    driver = webdriver.Chrome(options = chrome_options, service = chrome_service)
    mysite = variables.hq_url
    driver.get(mysite)
    end_time = time.perf_counter()
    init_time = end_time - start_time # ChromeDriver initialization time

    start_time = time.perf_counter()

    # If an error appears asking you to disconnect from other tabs
    try:
        disconnect_prompt = driver.find_element(By.XPATH, "//*[@href='home.HQ?disconnect=true']")
        if disconnect_prompt:
            disconnect_prompt.click()
    # If error, then:
    except Exception as e:
        # There were no login errors
        pass

    # If an error appears asking you to disconnect from other tabs
    try:
        '''
        If I'm on the login page
        '''

        username = driver.find_element(By.ID, "usernameLogin")
        password = driver.find_element(By.ID, "passwordLogin")

        username.send_keys(variables.hq_username)
        if type(variables.hq_password) != bytes:
            variables.hq_password = variables.hq_password.encode("utf-8")
        password.send_keys(decrypt(variables.hq_password, mykey).decode())

        driver.find_element(By.ID, "connectBtn").click()
    # If error, then:
    except Exception as e:
        # There were no login errors
        myPopupShowError("An error occured while connecting!\nThe website could be unavailable.\nPlease try again.")
        return

    # Wait for option to appear
    wait = WebDriverWait(driver, 10)

    try:
        self_button = driver.find_element(By.LINK_TEXT, "Self service")
    # If error, then:
    except Exception as e:
        # There were no login errors
        if "login" in extractpathurl(driver.current_url):
            myPopupShowError("Error while logging in!\nThe configured password may be incorrect.\nPlease try again.")
        else:
            myPopupShowError("Error accessing the 'Self service' button!\nThe website could be unavailable.\nPlease try again.")
        return

    # Fixes a bug that prevented a button from being clicked when a "Processing in progress, please wait..." loading screen was displayed. Fails automatically after 100 attempts.
    for i in range(100):
        try:
            wait.until(EC.element_to_be_clickable(self_button)).click()
        except Exception as e:
            time.sleep(2)
            continue
        break
    if i >= 90:
        myPopupShowError("Error clicking on the 'Self service' button!\nPlease try again.")
        return

    wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@data-fct='SF_WBA']"))).click()

    init_print = ""

    wait.until(EC.element_to_be_clickable((By.ID, "BTN_BAD")))

    init_times = ""
    try:
        init_times = driver.find_element(By.XPATH, "//*[@class='bargridwba']").text # Collecting badged times
    # If error, then:
    except Exception as e:
        # There were no errors when collecting badged times
        pass

    init_print += str("---- Badged times today ----\n")
    init_print += str(init_times + "\n\n")

    end_time = time.perf_counter()
    browse_time = end_time - start_time # Load time for badging webpage

    init_print += str("Initialization time (for ChromeDriver):\n" + str(round(init_time, 2)) + " seconds\n\n")
    init_print += str("Loading time for badging webpage:\n" + str(round(browse_time, 2)) + " seconds\n\n")

    confirmStart(init_print)

    start_time = time.perf_counter()

    toprint = ""

    wait.until(EC.element_to_be_clickable((By.ID, "BTN_BAD"))).click()
    wait.until(EC.element_to_be_clickable((By.ID, "BTN_BAD_MODALMSG_BTNA"))).click() # Yes
    # wait.until(EC.element_to_be_clickable((By.ID, "BTN_BAD_MODALMSG_BTNC"))).click() # No

    times = driver.find_element(By.XPATH, "//*[@class='bargridwba']").text # Retrieval of badged times
    if times:
        toprint += str("You just have badged!\n\n")
        toprint += str("---- Badged times today ----\n")
        toprint += str(times + "\n\n")
    else:
        toprint += str("Error, unable to recover times.\n- Wrong page loaded?\n- Horoquartz was updated causing variable names to change?\n\n")
    end_time = time.perf_counter()
    toprint += str("Initialization time (for ChromeDriver):\n" + str(round(init_time, 2)) + " seconds\n\n")
    toprint += str("Page loading time for badging:\n" + str(round(browse_time, 2)) + " seconds\n\n")
    toprint += str("Execution time (for badging):\n" + str(round(end_time - start_time, 2)) + " seconds\n\n\n")
    toprint += str("Total execution time (to initialize ChromeDriver, load the page and badge):\n" + str(round(init_time + browse_time + (end_time - start_time), 2)) + " seconds")
    myPopupShowInfo(toprint)
    driver.quit()
    quitandclose()

if __name__ == '__main__':
    main()
