# pleasebeup

This was a hackday project that I built in one day with @samlader.

It's a **website monitoring and alert system**.

<hr>

![](https://github.com/healeycodes/pleasebeup/raw/master/preview-home.png)

<hr>

![](https://github.com/healeycodes/pleasebeup/raw/master/preview-dashboard.jpg)

<br>

If your website stops responding to our pings you get an email alert. Our stretch goal was SMS alerts (but we didn't make it).


<br>

## Rough install/running steps

In case I want to pick this up again:

<br>

Install:

```
cd .
npm install
cd task
pip install -r requirements
```

<br>

Run:

```
npm run start
docker-compose up -d task
```

<br>

and then the following tasks need to be running:

```
celery -A app worker --loglevel=info
celery -A app beat --loglevel=info
```

<br>

🧙‍♂️
