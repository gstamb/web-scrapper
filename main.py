import requests
import selectorlib
import smtplib
import ssl
import os
import time
import sqlite3

URL = "https://programmer100.pythonanywhere.com/tours/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/39.0.2171.95 Safari/537.36'}
connection = sqlite3.connect("data.db")


def scrape(url):
    """Scrape a page source from the URL"""
    response = requests.get(url, HEADERS)
    source = response.text
    return source


def extract(source):
    extractor = selectorlib.Extractor.from_yaml_file("extract.yaml")
    value = extractor.extract(source)['tours']
    return value


def send_email(message):
    host = 'smtp.gmail.com'
    port = 465

    password = os.getenv('test_mail_server_password')
    username = os.getenv('test_mail_server_username')

    receiver = os.getenv('MYEMAIL')
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(host, port, context=context) as server:
        server.login(username, password)
        server.sendmail(username, receiver, message)


def store(new_event):
    row = new_event.split(", ")
    row = [x.strip() for x in row]
    cursor = connection.cursor()
    cursor.execute(f"INSERT INTO events VALUES(?,?,?)", row)
    connection.commit()


def get_data(data):
    row = data.split(", ")
    band, city, date = [x.strip() for x in row]
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM events where band=? and city=? and date=?", (band, city, date))
    rows = cursor.fetchall()
    return rows


if __name__ == '__main__':
    while True:
        scraped = scrape(URL)
        extracted = extract(scraped)
        print(extracted)
        if extracted != 'No upcoming tours':
            row = get_data(extracted)
            if not row:
                store(extracted)
                send_email(message=(f"New event was found {extracted}"))
        time.sleep(2)
