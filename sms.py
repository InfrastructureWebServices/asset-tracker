import requests
from os import environ
from dotenv import load_dotenv
load_dotenv('.env')

# twilio
def send_sms(to_number, body_text):
    if environ['twilio_account_sid'] != "" and environ['twilio_api_key'] != "" and environ['twilio_from_number'] != "":
        session = requests.Session()
        session.auth = (environ['twilio_account_sid'], environ['twilio_api_key'])
        from_number = environ['twilio_from_number']
        data = {"To": to_number, "From": from_number, "Body": body_text }
        url = "https://api.twilio.com/2010-04-01/Accounts/%s/Messages.json" % (environ['twilio_account_sid'])
        response = session.post(url, data)
        print(response.text)
        return response
    else: 
        print("TWILIO SECRETS MISSING")
        return None

if __name__ == "__main__":
    body_text = "Hi"
    to_number = "+614" # 
    send_sms(to_number, body_text)