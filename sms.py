import requests
from os import environ
from urllib import parse
from dotenv import load_dotenv
load_dotenv('.env')

# transmitsms
# session = requests.Session()
# session.auth = (environ['burst_api_key'], environ['burst_api_secret'])

# list_response = {
#     "list_id":8769785,
#     "msisdn":61422792641,
#     "first_name":"",
#     "last_name":"",
#     "created_at":"2024-06-24 07:33:47",
#     "status":"active",
#     "country":"AU"
# }

# url = "https://api.transmitsms.com/add-list.json?name=test"
# payload={}
# headers = {}
# response = session.post(url, headers=headers, data=payload)
# print(response.text)

# url = "https://api.transmitsms.com/add-to-list.json?list_id=%s&msisdn=61422792641" % (list_response['list_id'])
# payload={}
# headers = {}
# response = session.post(url, headers=headers, data=payload)
# print(response.text)

# url = "https://api.transmitsms.com/send-sms.json?message=Hi Brendan&to=61422792641"
# payload={}
# headers = {}
# response = session.post(url, headers=headers, data=payload)
# print(response.text)

# twilio
def send_sms(to_number, body_text):
    session = requests.Session()
    session.auth = (environ['twilio_account_sid'], environ['twilio_api_key'])
    from_number = "+19862350812"
    data = {"To": to_number, "From": from_number, "Body": body_text }
    url = "https://api.twilio.com/2010-04-01/Accounts/%s/Messages.json" % (environ['twilio_account_sid'])
    response = session.post(url, data)
    print(response.text)
    return response

if __name__ == "__main__":
    body_text = "Hi Brendan"
    to_number = "+61422792641"
    send_sms(to_number, body_text)