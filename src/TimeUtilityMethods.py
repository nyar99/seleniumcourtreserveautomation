from datetime import datetime, timedelta
from datetime import date
import pytz


def return_NY_time() -> datetime:
    """Return current time in NY"""
    tz_NY = pytz.timezone('America/New_York') 
    datetime_NY = datetime.now(tz_NY)
    return datetime_NY

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
    
def standard_to_military(standard_time: str) -> str:
    """Convert from standard time to military, standard time must be given in the form of 'H:M '"""
    tz_NY = pytz.timezone('America/New_York') 
    now = datetime.now(tz_NY)
    hour = int(standard_time[:standard_time.find(':')]) if standard_time[-2:] == 'AM' else int(standard_time[:standard_time.find(':')]) + 12
    minute = int(standard_time[standard_time.find(':') + 1 : standard_time.find(' ')])
    todayTime = now.replace(hour = hour, minute = minute)
    return todayTime

def compare_time_to_now(inputTime: str) -> bool:
    """Compare user given time with current NYC time. If input time is earlier, then return True"""
    system_time = return_NY_time()
    input_time = standard_to_military(inputTime)
    return input_time < system_time

def within_fifteen_minutes(inputTime: str) -> bool:
    """Compare user given time with current NYC time. If input time is earlier, then return True"""
    system_time = return_NY_time()
    input_time = standard_to_military(inputTime)
    td = input_time - system_time
    days = td.days
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if (not hours):
        return minutes < 15
    return False
    
def compare_date_to_today(inputDate: str):
    today = return_NY_time().date()
    month, day = inputDate.split('/')[0], inputDate.split('/')[1]
    inputDateTime = date(today.year, int(month), int(day))
    return (inputDateTime - today).days

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
