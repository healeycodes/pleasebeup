import json
import logging
from datetime import datetime

import requests
from celery import Celery
from requests import RequestException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from task.models import Website

app = Celery(backend='rpc://')

engine = create_engine('sqlite:///sqllight.db', echo=True)
init_session = sessionmaker(bind=engine)

POSTMARK_URL = 'https://api.postmarkapp.com/email'
POSTMARK_TOKEN = 'b9654a7f-8ed5-4d13-af41-f77e95d3d055'

EMAIL_SEND_ADDR = 'alert@pleasebeup.xyz'


@app.on_after_configure.connect
def setup_periodic_task(sender, **kwargs):
    sender.add_periodic_task(60.0, queue_ping.s(), expires=60)


@app.task
def queue_ping():
    session = init_session()
    websites = session.query(Website).filter(Website.active == 1)
    session.close()

    for website in websites:
        ping.delay(website)

    logging.info(f'{len(websites)} active websites queued!')


@app.task
def ping(website):
    try:
        r = requests.head(website.url)

        session = init_session()
        website.last_checked = datetime.now()

        if r.status_code != 200:
            logging.info(f'{website.url} is down!')
            website.failure_count += 1

            if website.user.email_enabled:
                send_email.delay()

        session.commit()
        session.close()

    except RequestException:
        logging.info(f'Failed to send request!')


@app.task
def send_email(website, attempt=0):
    if attempt > 3:
        logging.info(f'Exceeded max send attempts')
        return

    user = website.user

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
        send_email.apply_async((website, attempt), countdown=15)
        logging.info(f'Failed to send email. Re-queued.')


@app.task
def send_sms():
    pass


@app.task
def make_phonecall():
    pass
