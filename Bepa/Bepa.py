import os
import pymysql
import requests
import base64


# DB Variables
TIMEOUT = int(os.environ['DB_TIMEOUT'])
DB = os.environ['DB_NAME']
HOST = os.environ['DB_HOST']
PASSWORD = os.environ['DB_PASSWORD']
PORT = int(os.environ['DB_PORT'])
USER = os.environ['DB_USERNAME']


# Stablish DB connection
db_connection = pymysql.connect(
    charset="utf8mb4",
    connect_timeout=TIMEOUT,
    cursorclass=pymysql.cursors.DictCursor,
    db=DB,
    host=HOST,
    password=PASSWORD,
    read_timeout=TIMEOUT,
    port=PORT,
    user="root",
    write_timeout=TIMEOUT,
)
cursor = db_connection.cursor()


# Email service base URL and key
MAIL_URL = os.environ['MAIL_SERVICE_URL']
MAIL_KEY = os.environ['MAIL_SERVICE_KEY']


# CoinNews service host and port
COIN_NEWS_HOST = os.environ['COIN_NEWS_HOST']
COIN_NEWS_PORT = int(os.environ['COIN_NEWS_PORT'])
COIN_NEWS_API_URL = f"{COIN_NEWS_HOST}:{COIN_NEWS_PORT}/api/data"


def get_new_prices():
    currencies = requests.get(COIN_NEWS_API_URL).json()
    
    for currency in currencies:
        history = requests.get(f"{COIN_NEWS_API_URL}/{currency}/history").json()
        
        for record in history:
            insert_record = "INSERT IGNORE INTO Price (coinName, fetch_timestamp, price) VALUES (%s, %s, %s)"
            values = (currency, record['date'], record['value'])
            cursor.execute(insert_record, values)
        
        db_connection.commit()


def send_alerts():
    currencies = requests.get(COIN_NEWS_API_URL).json()
    print("[INFO] in send_alert function")
    for currency in currencies:
        currency_info = requests.get(f"{COIN_NEWS_API_URL}/{currency}").json()
        current_price = currency_info["value"]
        cursor.execute(f"SELECT price FROM Price WHERE coinName = '{currency}' ORDER BY fetch_timestamp DESC LIMIT 1")
        last_record = cursor.fetchone()
        db_connection.commit()

        if last_record:
            last_price = last_record["price"]
            roc = (abs(current_price - last_price) * 100 / last_price)

            cursor.execute(f"SELECT * FROM AlertSubscription WHERE coinName = '{currency}' AND DifferencePercentage <= {roc}")
            subscriptions = cursor.fetchall()
            db_connection.commit()

            for subscription in subscriptions:
                print(f"[INFO] Sending email to {subscription['email']}")
                email_content = {"from": "AUT Cloud Computing - <aut-cc@sandbox6748cfee9f664439be9af8f9eca357f4.mailgun.org>",
                                "to": [f"{subscription['email']}"],
                                "subject": f"{currency} Alert!",
                                "text": f"{currency} rate of change exceeded {subscription['DifferencePercentage']}%!"}

                requests.post(
                    MAIL_URL,
                    auth=("api", MAIL_KEY),
                    data=email_content
                )


try:
    send_alerts()
    get_new_prices()
except Exception as e:
    print(f"There was an exception running the Bepa service: {e}")
finally:
    db_connection.close()
