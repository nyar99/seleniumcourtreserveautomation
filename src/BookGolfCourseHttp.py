import json
import requests
#from pip._vendor import requests
from multiprocessing import Queue, Process
import datetime
import time

class Account:
    def __init__(self, username, password, remainingReservations = 8):
        self.username = username
        self.password = password
        self.remainingReservations = remainingReservations
    def setToken(self, jwtToken):
        self.jwtToken = jwtToken

class Cluster:
    def __init__(self, time, date, color, acceptableDelta=27, beginTime="8:00"):
        self.date = date
        self.time = time
        self.acceptableDelta = acceptableDelta
        self.beginTime = beginTime
        self.bethpageInterval = color['bethpageInterval']
    def returnAcceptableTimes(self):
        acceptableTimes = []
        timeIterator = datetime.datetime.strptime(self.beginTime, "%H:%M")
        time = datetime.datetime.strptime(self.time, "%H:%M")
        upperBoundTime = time + datetime.timedelta(minutes=self.acceptableDelta)
        lowerBoundTime = time - datetime.timedelta(minutes=self.acceptableDelta)
        while timeIterator <= upperBoundTime:
            if timeIterator > lowerBoundTime:
                print(timeIterator.strftime("%H:%M"))
                acceptableTimes.append(timeIterator.strftime("%H:%M"))
            timeIterator += datetime.timedelta(minutes=self.bethpageInterval)
        return acceptableTimes
        
def delay_until_7pm():
    now = datetime.datetime.now()
    target_time = now.replace(hour=19, minute=0, second=0, microsecond=0)
    
    if now > target_time:
        target_time += datetime.timedelta(days=1)
    
    time_to_wait = (target_time - now).total_seconds()
    time.sleep(time_to_wait)


def login(a : Account):
    url = "https://foreupsoftware.com/index.php/api/booking/users/login"
    
    headers = {
        "api-key": "no_limits"
    }
    
    data = {
        "username": a.username,
        "password": a.password,
        "booking_class_id": "",
        "api_key": "no_limits",
        "course_id": "19765"
    }
    
    # Sending the POST request
    response = requests.post(url, headers=headers, data=data)
    
    # Returning the response
    return response

red = {"color": "Red", "schedule_id": "2432", "teesheet_side_id": "1016", "course_id": "19765", "booking_class_id": "50295", "bethpageInterval": 9}

green = {"color": "Green", "schedule_id": "2434", "teesheet_side_id": "1020", "course_id": "19765", "booking_class_id": "50296", "bethpageInterval": 9}

blue = {"color": "Blue", "schedule_id": "2433", "teesheet_side_id": "1018", "course_id": "19765", "booking_class_id": "50293", "bethpageInterval": 9}

black = {"color": "Black", "schedule_id": "2431", "teesheet_side_id": "1014", "course_id": "19765", "booking_class_id": "50293", "bethpageInterval": 10}

def get_reservation_id(token, date, time, players, queue, color=red):
    print("calling get reservation id")
    url = "https://foreupsoftware.com/index.php/api/booking/pending_reservation"
    
    headers = {
        "api-key": "no_limits",
        "x-authorization": f"Bearer {token}",
    }

    data = {
        "time": f"{date} {time}",
        "holes": "18",
        "players": players,
        "carts": "false",
        "schedule_id": color["schedule_id"],
        "teesheet_side_id": color["teesheet_side_id"],
        "course_id": color["course_id"],
        "booking_class_id": color["booking_class_id"],
        "duration": "1",
        "foreup_discount": "false",
        "foreup_trade_discount_rate": "0",
        "trade_min_players": "8",
        "cart_fee": "0",
        "cart_fee_tax": "0",
        "green_fee": "65",
        "green_fee_tax": "0"
    }

    # Sending the POST request
    response = requests.post(url, headers=headers, data=data)
    print("Response received", response.text)
    queue.put(response)
    return response

def make_reservation(token, reservation_id, date, time, color=red, validate=True):
    url = 'https://foreupsoftware.com/index.php/api/booking/users/reservations'
    headers = {
        "api-key": "no_limits",
        "x-authorization": f"Bearer {token}",
    }
    data = {
        "time": f"{date} {time}",
        "start_front": 202409121633,
        "course_id": 19765,
        "course_name": "Bethpage State Park",
        "schedule_id": int(color["schedule_id"]),
        "teesheet_id": int(color["schedule_id"]),
        "schedule_name": f"Bethpage {color['color']} Course",
        "require_credit_card": False,
        "teesheet_holes": 18,
        "teesheet_side_id": int(color["teesheet_side_id"]),
        "teesheet_side_name": "Front",
        "teesheet_side_order": 1,
        "reround_teesheet_side_id": int(color["teesheet_side_id"]) + 1,
        "reround_teesheet_side_name": "Back",
        "available_spots": 4,
        "available_spots_9": 0,
        "available_spots_18": 4,
        "maximum_players_per_booking": "4",
        "minimum_players": "1",
        "allowed_group_sizes": ["1", "2", "3", "4"],
        "holes": "18",
        "has_special": False,
        "special_id": False,
        "special_discount_percentage": 0,
        "group_id": False,
        "booking_class_id": color["booking_class_id"],
        "booking_fee_required": False,
        "booking_fee_price": False,
        "booking_fee_per_person": False,
        "foreup_trade_discount_rate": 0,
        "trade_min_players": 8,
        "trade_cart_requirement": "riding",
        "trade_hole_requirement": "18",
        "trade_available_players": 0,
        "green_fee_tax_rate": False,
        "green_fee_tax": 0,
        "green_fee_tax_9": 0,
        "green_fee_tax_18": 0,
        "guest_green_fee_tax_rate": False,
        "guest_green_fee_tax": 0,
        "guest_green_fee_tax_9": 0,
        "guest_green_fee_tax_18": 0,
        "cart_fee_tax_rate": False,
        "cart_fee_tax": 0,
        "cart_fee_tax_9": 0,
        "cart_fee_tax_18": 0,
        "guest_cart_fee_tax_rate": False,
        "guest_cart_fee_tax": 0,
        "guest_cart_fee_tax_9": 0,
        "guest_cart_fee_tax_18": 0,
        "foreup_discount": False,
        "pay_online": "no",
        "green_fee": 65,
        "green_fee_9": 0,
        "green_fee_18": 65,
        "guest_green_fee": 65,
        "guest_green_fee_9": 0,
        "guest_green_fee_18": 65,
        "cart_fee": 0,
        "cart_fee_9": 0,
        "cart_fee_18": 0,
        "guest_cart_fee": 0,
        "guest_cart_fee_9": 0,
        "guest_cart_fee_18": 0,
        "rate_type": "walking",
        "special_was_price": None,
        "players": "4",
        "carts": False,
        "promo_code": "",
        "promo_discount": 0,
        "player_list": False,
        "duration": 1,
        "notes": [],
        "customer_message": "",
        "total": 260,
        "purchased": False,
        "pay_players": "4",
        "pay_carts": False,
        "pay_total": 260,
        "pay_subtotal": 260,
        "paid_player_count": 0,
        "discount_percent": 0,
        "discount": 0,
        "details": "",
        "pending_reservation_id": reservation_id,
        "allow_mobile_checkin": 0,
        "foreup_trade_discount_information": [],
        "airQuotesCart": [{"type": "item", "description": "Green Fee", "price": 93, "quantity": 1, "subtotal": 93}],
        "preTaxSubtotal": 93,
        "estimatedTax": 0,
        "subtotal": 93,
        "available_duration": None,
        "increment_amount": None,
        "availableHoles": "18",
        "blockReservationDueToExistingReservation": False,
        "captchaid": "03AFcWeA4P4Dd_x_24-M8UOda30VK-NzC4A98D9ofE9VQQTVYbwB5On7z3elJYDedlpm3pCBYMkWT9IZb10MRh2ArI8HS2Tmy8fS9NvGRX4DRLnomSBh-pprJAiYXRWos5xLVEpMwjZbIOlbRClyx7jgsIXioUwsvJklAKdjBl-Lj4EHcCNLPSI259Ut-S6WW-Be5fgkVwzizp6CKFrwAv2gX4QU3MvEo10_6eprPAsZtkJkN_zVgHMTyHMjEEs78jDEXlzMF7AmarZ2747JjzZorasrIBA_H6K8PQa7lSfHM4Gf0zG4sBZgn8_EvLKlyNs85Lim5Lh-sWmqREkxQf-Y_AGZVZN3UhNLu6jRNcTGKFY7h_93ZJnDCf8dAevrWkXtXNwFmgg72Q3E-rrwVIRh3rVSNVqszYQ9QKfz7xsyLop-o9_Q1no6RHltQEXQWTQu2GtU-xL_27gmnIJXocwSRwVeYh21cECqEMsw0spTfLN_U-BZ95ZXdn9oWJ38MEIcbOPtOvAJP5MmA3ZYFcyIZN_kXpkBf5zwA5qk4UaqlTvAbiXS3F9bU6G-gYcwCpcOnK7UYbpG_5nBny53cfm7O015KD9jTQkO46XX_mxz_FgX2eJ2x-4_A3cWv91VCk2uY7XngrtIyt1O106kDgZWn6oSvGLg_L2P-G1svesmzN8dV658S5EJ731eQ5xO5nLxyVX1QQJ0jIPKx7c2k44MhrIxQc-7JCf3h3qO90F2mm4vIUI4vT0nsMkJRxP7s5-Jvz0UzQ9pUjNpbCG9ux59BnIBB-96RQ_aEYrphD9ufxBMnFEShtmDLYPG3vjmzLI5K12sCd6XhsyntMJIyce3vUnU6m_oISeHV0eNpWFhdhcneizq60ZHedifLOCOBuGBs0Dkwt33S1K-BCTaMW2xUa9vTcbLu5cw"
    }

    if (validate):
        data["validateOnly"] = True

    print("Data created, ready to post request")
    response = requests.post(url, headers=headers, json=data)
    return response

def consolidatedReservationFlow(jwtToken, date, time, players, queue, color, validate):
    try:
        res = get_reservation_id(jwtToken, date, time, players, queue, color)
        reservation_id = json.loads(res.text)['reservation_id']
        print("Acquired reservation ID", reservation_id)
        res = make_reservation(jwtToken, reservation_id, date, time, color, validate=validate)
        print("Made Reservation Call", res.text)
    except Exception as e:
        print("Failed to make reservation", e)

def main():
    # Create an account object
    a = Account("anilchakka2000@gmail.com", "pass", 8)
    b = Account("bvprakhyath@gmail.com", "pass", 7)
    users = [a, b]
    for user in users:
        res = login(user)
        user.setToken(json.loads(res.text)['jwt'])
    colors = [red, blue, green, black]
    queue = Queue()

    processes = []
    for color in colors:
        cluster = Cluster("08:30", "2024-11-9", color, 30, "8:00")
        for time in cluster.returnAcceptableTimes():
            for user in users:
                try:
                    if (user.remainingReservations > 0):
                        p = Process(target = consolidatedReservationFlow, args = (user.jwtToken, cluster.date, time, 4, queue, color, True))
                        processes.append(p)
                        user.remainingReservations -= 1
                    else:
                        break
                except Exception as e:
                    print("Failed to create process", e)
    
    delay_until_7pm()
    for p in processes:
        p.start()

    for p in processes:
        p.join()
    
    while not queue.empty():
        try:
            result = queue.get().text
            print(result)
        except Exception as e:
            print("Process failure, reached an exception", e)
    
    
        
    return {
        'statusCode': res.status_code,
        'body': "successful execution"
    }

if __name__ == "__main__":
    main()