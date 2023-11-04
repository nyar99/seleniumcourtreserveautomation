# backup code: 55dVGxM2RgD79c_m4wJOUdCpxbyZBKMyzMJ9IK5A

from twilio.rest import Client

# Your Account SID from twilio.com/console
account_sid = "AC0649c05670fca028334f2e36e7326e85"
# Your Auth Token from twilio.com/console
auth_token  = "964ecb0844c2ca3f79b696ce828f83ba"

client = Client(account_sid, auth_token)

message = client.messages.create(
    to="+15128048607", 
    from_="+12545363564",
    body="Hello from Python!")

print(message.sid)