import boto3
from botocore.vendored import requests
import time
from datetime import date
from datetime import datetime
from boto3.dynamodb.conditions import Key, Attr

courtReservationTable = "ReserveCourt"
courtTable = boto3.resource('dynamodb').Table(courtReservationTable)
userTable = "UserInfo"
userTable = boto3.resource('dynamodb').Table(userTable)

def within_five_minutes(standard_time: str) -> str:
    """Convert from standard time to military, standard time must be given in the form of 'H:M '"""
    now = datetime.now()
    hour = int(standard_time[:standard_time.find(':')]) if standard_time[-2:] == 'AM' else int(standard_time[:standard_time.find(':')]) + 12
    minute = int(standard_time[standard_time.find(':') + 1 : standard_time.find(' ')])
    todayTime = now.replace(hour = hour, minute = minute)
    delta = todayTime - now
    if (delta.total_seconds() < (400)):
        return True
    return False
    

def compare_date_to_today(inputDate: str):
    today = date.today()
    month, day = inputDate.split('/')[0], inputDate.split('/')[1]
    inputDateTime = date(today.year, int(month), int(day))
    return (inputDateTime - today).days
    

def lambda_handler(event, context):
    response = courtTable.scan()
    data = response['Items']
    while 'LastEvaluatedKey' in response:
        response = courtTable.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])
    data.sort(key = lambda x : x['Date'])
    for item in data:
        date = item['Date']
        time = item['Time']
        if(compare_date_to_today(date) <= 2 and within_five_minutes(time)):
            print("Triggering court reservation for: " + item['PhoneNumber'] + " on " + date + " at " + time)
            response = userTable.query(KeyConditionExpression=Key('PhoneNumber').eq(item['PhoneNumber']))
            if (len(response) > 0):
                userEmail = response['Items'][0]['email']
                password = response['Items'][0]['password']
                requests.post('https://v0kjlg9u96.execute-api.us-east-2.amazonaws.com/Prod/reserveCourt', 
                json = {"User": userEmail,"Pass": password, "Time": time,
                "DaysAhead": compare_date_to_today(date),"IsIndoors": item['IsIndoors'],"Length":item['Length']})
            else:
                print("This user has not registered")