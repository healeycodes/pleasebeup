import json

import requests

POSTMARK_URL = 'https://api.postmarkapp.com/email'
POSTMARK_TOKEN = '5ed4903c-88cd-4550-870d-fbfdffb68d0b'

headers = {
    'Content-Type': 'application/json',
    'X-Postmark-Server-Token': POSTMARK_TOKEN,
    'Accept': 'application/json'
}

data = {
    'From': 'alert@pleasebeup.xyz',
    'To': 'sam.lader@tails.com',
    'Subject': 'Your website is on fire!',
    'HtmlBody': '<b>We noticed that your site has been '
                'offline for more than 5 minutes!</b>'
}

r = requests.post(
    POSTMARK_URL,
    headers=headers,
    data=json.dumps(data)
)

response = json.loads(r.text)

print(response)