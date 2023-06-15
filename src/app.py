from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
import time as t
from datetime import datetime
from datetime import date
import ast

nextDayButtonClass = 'k-nav-next'
scheduleTableClass = "k-scheduler-table"
courtItemContainerClass = 'consolidate-item-container'
disclosureAgreeClass = 'rowCheckbox'
selectLengthOfPlayClass = 'k-list-item-text'
failurePopupClass = 'swal2-container'
failureDisclosureAgreeClass = 'swal2-confirm'
submitButtonClass = 'btn-submit'
slotButtonClass = 'slot-btn'

# uncomment before deploying
# chrome_options = webdriver.ChromeOptions()
# chrome_options.binary_location = "/opt/chrome/chrome"
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--disable-dev-tools")
# chrome_options.add_argument("--no-zygote")
# chrome_options.add_argument("--single-process")
# chrome_options.add_argument("window-size=2560x1440")
# chrome_options.add_argument("--user-data-dir=/tmp/chrome-user-data")
# chrome_options.add_argument("--remote-debugging-port=9222")
# driver = webdriver.Chrome("/opt/chromedriver", options=chrome_options)
driver = webdriver.Chrome()

def format_time(input_time: datetime) -> str:
    """Format datetime object into H:M time str"""
    return input_time.strftime("%H:%M")

def military_to_standard(military_time) -> str:
    """Convert from military time to standard, adding AM/PM suffix. Military time must be given in 'H:M'"""
    standard_time = ""
    if int(military_time[:military_time.find(':')]) > 12:
        standard_time += str(int(military_time[:2]) - 12) + military_time[2:] + ' PM'
    else:
        standard_time = military_time
        standard_time += ' AM'
    return standard_time

# Login flow
def login(user = 'nyar99@gmail.com', passcode = '********'):
    """Login to Court Reserve API"""
    driver.get('https://app.courtreserve.com/Online/Account/LogIn/5881')
    try:
        inputs = driver.find_elements(By.TAG_NAME, "input")
        username = inputs[2]
        password = inputs[3]

        username.send_keys(user)
        password.send_keys(passcode)

        driver.find_element(By.TAG_NAME, "button").click()
    except:
        print("Login flow failed")
    
def get_available_courts(day = 0, indoor = False):
    """Get available courts at NTC"""
    reservationLink = "https://app.courtreserve.com/Online/Reservations/Bookings/5881?sId=294" if indoor else "https://app.courtreserve.com/Online/Reservations/Bookings/5881?sId=295"
    driver.get(reservationLink)
    driver.implicitly_wait(5)

    changeDate = driver.find_element(By.CLASS_NAME, nextDayButtonClass)
    for i in range(day):
        changeDate.click()
        driver.implicitly_wait(3)
    driver.implicitly_wait(3)
    
    schedulingTable = driver.find_elements(By.CLASS_NAME, scheduleTableClass)
    scrollAnchor = driver.find_elements(By.CLASS_NAME, slotButtonClass)[-1]
    a = ActionChains(driver)
    a.move_to_element(scrollAnchor).perform()
    times = schedulingTable[-2].find_elements(By.TAG_NAME, "small")

    courtItems = driver.find_elements(By.CLASS_NAME, courtItemContainerClass)
    timeToCourtElement = {}

    for i in range(len(times)):
        courtItems = driver.find_elements(By.CLASS_NAME, courtItemContainerClass)
        try:
            courtElement = courtItems[i].find_element(By.TAG_NAME, 'a')
            timeToCourtElement[times[i].text] = courtElement
            print('found available court', times[i].text)
        except:
            print('Time not available ', times[i].text)
    driver.implicitly_wait(5)
    return timeToCourtElement

def reserve_court(timeToCourtElement: dict, time: str, length: int) -> bool:
    """Attempt to reserve court at NTC for specified time"""
    print("Trying to reserve court for time: " + time)
    try:
        if time not in timeToCourtElement:
            print("Court container did not properly load")
            return False
        timeToCourtElement[time].click()
        disclosureElement = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, disclosureAgreeClass))
        )
        disclosureElement.click()
        t.sleep(2)
        timeOptions = driver.find_elements(By.CLASS_NAME, selectLengthOfPlayClass)
        while len(timeOptions) <= 4:
            timeOptions = driver.find_elements(By.CLASS_NAME, selectLengthOfPlayClass)
        driver.implicitly_wait(2)
        print('Found Time Options')
        driver.execute_script("arguments[0].click();", timeOptions[length//30 - 1])
        try:
            driver.execute_script("arguments[0].click();", timeOptions[length//30 - 1])
        except Exception as e:
            print(e)
            timeOptions = driver.find_elements(By.CLASS_NAME, selectLengthOfPlayClass)
            driver.execute_script("arguments[0].click();", timeOptions[length//30 - 1])
        print("Play Options selected")
        try:
            while(driver.current_url != 'https://app.courtreserve.com/Online/Payments/ProcessPayment/5881'):
                driver.implicitly_wait(0.25)
                if (driver.find_elements(By.CLASS_NAME, failurePopupClass)):
                    print("Found disclosure")
                    driver.find_element(By.CLASS_NAME, failureDisclosureAgreeClass).click()
                driver.find_element(By.CLASS_NAME, submitButtonClass).click()
                driver.implicitly_wait(0.25)
        finally:
            print("Court successfully reserved")
            driver.implicitly_wait(5)
            # driver.find_element(By.ID, 'PayButton').click()
            return True
    except Exception as e:
        print(e)
        return False
#samiam password: tP5$&C9%
def handler(event, context):
    item = event['body']
    item = item.replace('true', 'True')
    item = item.replace('false', 'False')
    print(item)
    print(type(item))
    item = ast.literal_eval(item)
    print(item)
    user = item['User']
    password = item['Pass']
    daysAhead = item['DaysAhead']
    time = item['Time']
    length = item['Length']
    indoors = item['IsIndoors']
    executionSucceeded = False
    firstExecution = True

    login(user, password)
    while (not executionSucceeded):
        map = get_available_courts(daysAhead, indoors) if firstExecution else get_available_courts(0)
        executionSucceeded = reserve_court(map, time, int(length))
        firstExecution = False

# comment before deploying
item = '{"User":"nyar99@gmail.com", "Pass": "Nav1Swa2", "Time":"10:00 PM", "Length": 60, "IsIndoors": false, "DaysAhead": 1}'
handler({'body':item}, None)