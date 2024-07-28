import os
import pymysql
from fastapi import FastAPI
import uvicorn
import base64


# DB Variables
TIMEOUT = int(os.environ['DB_TIMEOUT'])
DB = os.environ['DB_NAME']
HOST = os.environ['DB_HOST']
PASSWORD = os.environ['DB_PASSWORD']
PORT = int(os.environ['DB_PORT'])
USER = os.environ['DB_USERNAME']


print("-----------------------------")
print("HOST :")
print(HOST)
print("-----------------------------")
print("USESR: ")
print(USER)


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
    user=USER,
    write_timeout=TIMEOUT,
)
cursor = db_connection.cursor()


# API host and port
API_HOST = os.environ['PEYK_API_HOST']
API_PORT = int(os.environ['PEYK_API_PORT'])


app = FastAPI()


# Get the price history of a specific currency
@app.get('/price/{currency}')
async def get_price(currency: str):
    cursor.execute(f"SELECT * FROM Price WHERE coinName = '{currency}'")
    currency_info = cursor.fetchall()
    db_connection.commit()

    return currency_info

# Subsribe to a certain currency
@app.post('/subscribe')
async def subscribe(currency: str, email: str, difference_percentage: int):
    try:
        add_subscription = "INSERT INTO AlertSubscription (email, coinName, DifferencePercentage) VALUES (%s, %s, %s)"
        values = (email, currency, difference_percentage)
        cursor.execute(add_subscription, values)
        db_connection.commit()

        return {"message": f"subscribed to {currency} successfully."}
    
    except Exception as e:
        return {
            "message": f"there was an error subscribing to {currency}.",
            "error": e
        }

if __name__ == "__main__":
    uvicorn.run(app, host=API_HOST, port=API_PORT)
