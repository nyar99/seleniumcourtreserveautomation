from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
import time as t
from datetime import datetime, timedelta
import pytz
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

timeToCourtElementIndex = {
    "7:00 AM" : 0,
    "7:30 AM" : 1,
    "8:00 AM" : 2,
    "8:30 AM" : 3,
    "9:00 AM" : 4,
    "9:30 AM" : 5,
    "10:00 AM" : 6,
    "10:30 AM" : 7,
    "11:00 AM" : 8,
    "11:30 AM" : 9,
    "12:00 PM" : 10,
    "12:30 PM" : 11,
    "1:00 PM" : 12,
    "1:30 PM" : 13,
    "2:00 PM" : 14,
    "2:30 PM" : 15,
    "3:00 PM" : 16,
    "3:30 PM" : 17,
    "4:00 PM" : 18,
    "4:30 PM" : 19,
    "5:00 PM" : 20,
    "5:30 PM" : 21,
    "6:00 PM" : 22,
    "6:30 PM" : 23,
    "7:00 PM" : 24,
    "7:30 PM" : 25,
    "8:00 PM" : 26,
    "8:30 PM" : 27,
    "9:00 PM" : 28,
    "9:30 PM" : 29,
    "10:00 PM": 30,
    "10:30 PM": 31
}

# headless chrome options
# service = Service("/opt/chromedriver")
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
# driver = webdriver.Chrome(service=service, options=chrome_options)

#local chrome options
service = webdriver.ChromeService(executable_path="chromedriver")
driver = webdriver.Chrome()

def return_NY_time() -> datetime:
    """Return current time in NY"""
    tz_NY = pytz.timezone('America/New_York') 
    datetime_NY = datetime.now(tz_NY)
    return datetime_NY

def wait_until_time(timeToGet, daysAhead):
    """Wait until the minutes of the time are either :00 or :30"""
    # we should run this method if the difference between the current time and the time we want to reserve is > 48 hours
    if (hours_til_reservation(timeToGet, daysAhead) > 48):
        while True:
            now = datetime.now()
            if now.minute == 0 or now.minute == 30:
                break
            t.sleep(0.001)
        return
    else:
        return

def hours_til_reservation(timeToGet, daysAhead):
    """Return the number of hours until timeToGet"""
    nowNy = return_NY_time()
    d = datetime.strptime(timeToGet, "%I:%M %p")
    targetDt = nowNy + timedelta(days=daysAhead)
    targetDt = targetDt.replace(hour=d.hour, minute=d.minute, second=0, microsecond=0)
    secondsDiff = (targetDt - nowNy).total_seconds()
    return secondsDiff / (60 * 60)

# Login flow
def login(user = 'sameerpusapaty@gmail.com', passcode = 'password'):
    """Login to Court Reserve API"""
    driver.get('https://app.courtreserve.com/Online/Account/LogIn/5881')
    try:
        inputs = driver.find_elements(By.TAG_NAME, "input")
        username = inputs[2]
        password = inputs[3]

        username.send_keys(user)
        password.send_keys(passcode)

        driver.find_element(By.TAG_NAME, "button").click()
        return True
    except Exception as e:
        print("Login flow failed")
        print(e)
        return False
    
def get_available_courts(day = 0, indoor = False, time = '6:00 PM'):
    """Get available courts at NTC"""
    reservationLink = "https://app.courtreserve.com/Online/Reservations/Bookings/5881?sId=294" if indoor else "https://app.courtreserve.com/Online/Reservations/Bookings/5881?sId=295"
    driver.get(reservationLink)
    driver.implicitly_wait(5)

    changeDate = driver.find_element(By.CLASS_NAME, nextDayButtonClass)
    for i in range(day):
        changeDate.click()
        print("changed day")
        driver.implicitly_wait(3)
    driver.implicitly_wait(3)
    
    schedulingTable = driver.find_elements(By.CLASS_NAME, scheduleTableClass)
    scrollAnchor = driver.find_elements(By.CLASS_NAME, slotButtonClass)[-1]
    a = ActionChains(driver)
    a.move_to_element(scrollAnchor).perform()
    times = schedulingTable[-2].find_elements(By.TAG_NAME, "small")

    courtItems = driver.find_elements(By.CLASS_NAME, courtItemContainerClass)
    courtItemException = 0
    while(courtItemException <= 20):
        try:
            courtItems = driver.find_elements(By.CLASS_NAME, courtItemContainerClass)
            courtElement = courtItems[timeToCourtElementIndex[time]].find_element(By.TAG_NAME, 'a')
            ActionChains(driver) \
                .pause(2) \
                .move_to_element(courtElement) \
                .perform()
            print("found available court")
            return courtElement
        except:
            courtItemException += 1
            print("Could not get time or court not available")
    print('failed to see court after 20 iterations', time)
    return None

def reserve_court(timeToCourtElement, time: str, length: int, daysAhead: int) -> bool:
    """Attempt to reserve court at NTC for specified time"""
    print("Trying to reserve court for time: " + time)
    if (timeToCourtElement != None):
        try:
            timeToCourtElement.click()
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
            try:
                driver.execute_script("arguments[0].click();", timeOptions[length//30 - 1])
            except Exception as e:
                print(e)
                timeOptions = driver.find_elements(By.CLASS_NAME, selectLengthOfPlayClass)
                driver.execute_script("arguments[0].click();", timeOptions[length//30 - 1])
            print("Play Options selected")
            try:
                driver.implicitly_wait(1)
                wait_until_time(time, daysAhead)
                if (driver.current_url != 'https://app.courtreserve.com/Online/Payments/ProcessPayment/5881'):
                    driver.find_element(By.CLASS_NAME, submitButtonClass).click()
                    print("Clicked submit button")
            except Exception as e:
                print("Reached some exception while stalling")
                print(e)
            while(driver.current_url != 'https://app.courtreserve.com/Online/Payments/ProcessPayment/5881'):
                t.sleep(1)
            if (driver.find_element(By.ID, 'PayButton')):
                #driver.find_element(By.ID, 'PayButton').click()
                print("Court successfully reserved")
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False
    else:
        print("Court not available")
        return False

def handler(event, context):
    item = event['body']
    item = item.replace('true', 'True')
    item = item.replace('false', 'False')
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
    executions = 0

    login(user, password)
    while (not executionSucceeded and executions <= 5):
        # date is persisted across refreshes
        if (firstExecution):
            courtItem = get_available_courts(daysAhead, indoors, time)
            firstExecution = False
        else:
            get_available_courts(0, indoors, time)
        executionSucceeded = reserve_court(courtItem, time, int(length), daysAhead)
        executions += 1

# local run config
item = '{"User":"sameerpusapaty@gmail.com", "Pass": "password", "Time":"9:00 PM", "Length": 60, "IsIndoors": false, "DaysAhead": 2}'
handler({'body':item}, None)