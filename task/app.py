import logging

import requests
from celery import Celery

app = Celery(backend='rpc://')


@app.on_after_configure.connect
def setup_periodic_task(sender, **kwargs):
    sender.add_periodic_task(10.0, queue_pings.s(), expires=10)


@app.task
def queue_pings():
    # Query all active websites
    websites = [x for x in range(5)]

    for website in websites:
        ping.delay(website)

    logging.info(f'{len(websites)} active websites queued!')


@app.task
def ping(website):
    try:
        r = requests.head('http://www.google.com')
        if r.status_code == 200:
            return
    except Exception as e:
        logging.info(f'Failed to send request!')

    user = website.user
    logging.info(f'{website.url} is down!')

    if user.email_enabled:
        send_email.delay()

    if user.sms_enabled:
        send_sms.delay()

    if user.phonecall_enabled:
        make_phonecall.delay()


@app.task
def send_sms():
    return('blahem')


@app.task
def send_email():
    return('blahem')


@app.task
def make_phonecall():
    return('blahem')
