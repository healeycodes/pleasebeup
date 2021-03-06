import json
import logging
from datetime import datetime

import requests
from celery import Celery
from requests import RequestException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Website

from models import User

app = Celery(backend='rpc://')

engine = create_engine('sqlite:///../data/sqlite.db', echo=True)
init_session = sessionmaker(bind=engine)

POSTMARK_URL = 'https://api.postmarkapp.com/email'
POSTMARK_TOKEN = '5ed4903c-88cd-4550-870d-fbfdffb68d0b'

EMAIL_SEND_ADDR = 'alert@pleasebeup.xyz'


@app.on_after_configure.connect
def setup_periodic_task(sender, **kwargs):
    sender.add_periodic_task(60.0, queue_ping.s(), expires=60)


@app.task
def queue_ping():
    session = init_session()
    websites = session.query(Website).all()
    session.close()

    for website in websites:
        ping.delay(website.id)

    logging.info(f'{len(websites)} active websites queued!')


@app.task
def ping(website_id, failure=False):
    session = init_session()
    website = session.query(Website).get(website_id)

    try:
        r = requests.head(website.url, timeout=15)
        if r.status_code != 200 or 302:
            failure = True

    except RequestException:
        failure = True

    website.last_checked = datetime.now()

    if failure:
        website.failure_count += 1
        if website.failure_count in (5, 10, 30):
            # Skip email while in alpha
            # send_email.delay(website_id)
            return
    else:
        website.failure_count = 0

    session.commit()
    session.close()


@app.task
def send_email(website_id, attempt=0):
    if attempt > 3:
        logging.info(f'Exceeded max send attempts')
        return

    session = init_session()
    website = session.query(Website).get(website_id)

    # Andy didnt set up the foreign key relationship
    user = session.query(User).filter(User.email == website.email)[0]

    website.failure_count = 0
    session.commit()

    headers = {
        'Content-Type': 'application/json',
        'X-Postmark-Server-Token': POSTMARK_TOKEN,
        'Accept': 'application/json'
    }

    data = {
        'From': EMAIL_SEND_ADDR,
        'To': user.email,
        'Subject': 'Your website is on fire!',
        'HtmlBody': '<b>We noticed that your site has been '
                    'offline for more than 5 minutes!</b>'
    }

    session.close()

    r = requests.post(
        POSTMARK_URL,
        headers=headers,
        data=data
    )

    response = json.loads(r.text)

    if response['ErrorCode'] == 0:
        logging.info(f'Email alert sent for {website}!')

    else:
        attempt += 1
        send_email.apply_async((website_id, attempt), countdown=15)
        logging.info(f'{attempt} Failed to send email. Re-queued.')


@app.task
def send_sms():
    pass


@app.task
def make_phonecall():
    pass
