from selenium import webdriver
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException

from selenium.webdriver.common.by import By

millPondUrl = "https://www.nycgovparks.org/tennisreservation/availability/4"


driver = webdriver.Chrome()
driver.get(millPondUrl)

def selectDate(daysAhead):
    if (daysAhead == 0):
        raise ValueError("daysAhead must be greater than 0")
    if (daysAhead > 6):
        raise ValueError("daysAhead must be less than 7")
    else:
        courtDateParent = driver.find_element(By.ID, "court-availability")
        children = courtDateParent.find_elements(By.TAG_NAME, "a")
        try:
            children[daysAhead].click()
        except Exception as e:
            raise e
        
def get_minutes_from_time_string(time_string):
    # Parse the time string to a datetime object
    time_obj = datetime.strptime(time_string, "%I:%M %p")
    # Return the minute part
    return time_obj.minute


# tbody element not found, figure out how to get the tbody element
def selectTime(time, daysAhead):
    if (time == None):
        raise ValueError("time cannot be None")
    if (get_minutes_from_time_string(time) != 0):
        raise ValueError("time must be on the hour")
    dayElement = driver.find_element(By.CLASS_NAME, 'tab-content').find_element(By.CLASS_NAME, 'active')
    timeItems = dayElement.find_element(By.TAG_NAME, 'tbody').find_elements(By.TAG_NAME, 'tr')
    times = [
        '6:00 AM', '7:00 AM', '8:00 AM', '9:00 AM', '10:00 AM', '11:00 AM', '12:00 PM', '1:00 PM', 
        '2:00 PM','3:00 PM', '4:00 PM', '5:00 PM', '6:00 PM', '7:00 PM', '8:00 PM', '9:00 PM', '10:00 PM'
    ]
    for index, t in enumerate(times):
        if time == t:
            reservableCourts = timeItems[index].find_elements(By.TAG_NAME, 'td')
            for court in reservableCourts[1:]:
                try:
                    court.find_element(By.TAG_NAME, 'a')
                    court.find_element(By.TAG_NAME, 'a').click()
                    confirmPlayerString = "Confirm and Enter Player Details"
                    driver.find_element(By.XPATH, f"//input[@value='{confirmPlayerString}']").click()
                    return True
                except Exception as e:
                    print(e)
                    continue
    return False

def fillInDetails(lengthOfPlay):
    if (lengthOfPlay == 60):
        driver.find_element(By.ID, 'num_players_2').click()
        driver.find_element(By.ID, 'single_play_exist_2').click()
    else:
        driver.find_element(By.ID, 'num_players_4').click()
        driver.find_element(By.ID, 'single_play_exist_4').click()
    driver.find_element(By.ID, 'name').send_keys('Naveen')
    driver.find_element(By.ID, 'email').send_keys('nyar99@gmail.com')
    driver.find_element(By.ID, 'address').send_keys('220 E 29th St')
    driver.find_element(By.ID, 'city').send_keys('New York')
    driver.find_element(By.ID, 'zip').send_keys('10016')
    driver.find_element(By.ID, 'phone').send_keys('5128048607')
    driver.find_element(By.XPATH, "//input[@value='Continue to Payment']").click()
    pass

def fillInPaymentInfo():
    driver.find_element(By.ID, 'cc_number').send_keys('1234567890123456')
    driver.find_elements(By.ID, 'expdate_month')[1].send_keys('12')
    driver.find_elements(By.ID, 'expdate_year')[1].send_keys('2023')
    driver.find_element(By.ID, 'cvv2_number').send_keys('123')
    driver.find_element(By.ID, 'btn_pay_cc').click()
    pass

selectDate(6)       
if (selectTime('3:00 PM', 6)):
    fillInDetails(60)
    driver.implicitly_wait(10)
    fillInPaymentInfo()
