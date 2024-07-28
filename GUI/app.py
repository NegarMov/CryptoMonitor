import os
from flask import Flask, render_template, request
from datetime import datetime
import requests


PEYK_HOST = os.environ['PEYK_HOST']
PEYK_PORT = int(os.environ['PEYK_PORT'])


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_currency_history', methods=['POST'])
def get_currency_history():
    currency_name = request.form['currency_name']

    response = requests.get(f'{PEYK_HOST}:{PEYK_PORT}/price/{currency_name}')
    price_history = response.json()
    
    if price_history:
        for record in price_history:
            record['fetch_timestamp'] = datetime.strptime(record['fetch_timestamp'], '%Y-%m-%dT%H:%M:%S').strftime('%Y/%m/%d %H:%M:%S')
    
    return render_template('index.html', currency_name=currency_name, price_history=price_history)


@app.route('/subscribe', methods=['POST'])
def subscribe():
    currency_name = request.form['currency_name']
    email = request.form['email']
    difference_percentage = request.form['difference_percentage']
    
    response = requests.post(f'{PEYK_HOST}:{PEYK_PORT}/subscribe', params={
        'currency': currency_name,
        'email': email,
        'difference_percentage': int(difference_percentage)
    })
    
    if response.status_code == 200:
        message = f'Subscribed to {currency_name} successfully!'
    else:
        message = 'Failed to subscribe'

    return render_template('index.html', message=message)


if __name__ == '__main__':
    app.run(debug=False)
