import logging

import requests
from celery import Celery

app = Celery(backend='rpc://')


@app.on_after_configure.connect
def setup_periodic_task(sender, **kwargs):
    # Calls test('world') every 30 seconds
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
    r = requests.get('http://www.google.com')
    if r.status_code == 200:
        return('blahem')
    else:
        return('what')


@app.task
def send_sms():
    return('blahem')


@app.task
def send_email():
    return('blahem')


@app.task
def make_phonecall():
    return('blahem')
