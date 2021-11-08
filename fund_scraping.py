from bs4 import BeautifulSoup

import requests
# Send the mail
import smtplib
# email body
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# system date and time manipulation
import datetime
import re

FUNDS = {
    'BlackRock Next Generation Technology Fund': 'https://endowus.com/investment-funds-list/blackrock-bgf-next-generation-technology-fund-LU2290526321',
    'BlackRock World Technology Fund': 'https://endowus.com/investment-funds-list/blackrock-bgf-world-technology-fund-LU1852331112',
    'JP Morgan China Fund': 'https://endowus.com/investment-funds-list/jp-morgan-china-a-share-opportunities-fund-LU1655091616',
    'Franklin Technology Fund': 'https://endowus.com/investment-funds-list/franklin-templeton-franklin-technology-fund-LU1803068979',
    'Franklin U.S. Fund': 'https://endowus.com/investment-funds-list/franklin-templeton-u.s.-opportunities-fund-LU0320765059',
    'Schroders Climate Change Fund': 'https://endowus.com/investment-funds-list/schroders-isf-global-climate-change-fund-LU0312595415',
    'Schroders Global Growth Fund': 'https://endowus.com/investment-funds-list/schroders-isf-global-sustainable-growth-fund-LU2289884723'
}

now = datetime.datetime.now()

content = '''
<head>
<style>
table {
  font-family: arial, sans-serif;
  border-collapse: collapse;
  width: 100%;
}

td, th {
  border: 1px solid #dddddd;
  text-align: left;
  padding: 8px;
}

tr:nth-child(even) {
  background-color: #dddddd;
}

a {
    color: #0472ff;
    text-decoration: none;
}
</style>
</head>
<body>

<h2>Investment Portfolio</h2>

<table>
  <tr>
    <th>Fund</th>
    <th>NAV</th>
    <th>Change</th>
    <th>Last Update</th>
  </tr>
'''


def get_fund_code(fund):
    return fund.split('-')[-1]


def get_day_change(soup):
    result = soup.find_all('span', class_='mod-ui-data-list__value')
    nav = result[0].text
    delta = result[1].text.split('/')[-1]
    delta = delta.strip()
    return nav, delta


def get_updated_date(soup):
    result = soup.find_all('div', class_='mod-disclaimer')
    result_list = result[0].text.split(' ')
    month = result_list[-3]
    day = result_list[-2]
    year = result_list[-1][:-1]
    return f'{day} {month}, {year}'


def get_fund_soup(fund_code):
    link = f'https://markets.ft.com/data/funds/tearsheet/summary?s={fund_code}:SGD'
    resp = requests.get(link)
    return BeautifulSoup(resp.content, 'html.parser')


def convert_to_html(fund_name, fund_detail, nav, delta, updated_date):
    return f'''
        <tr>
            <td>
                <a href={fund_detail} target="_blank">
                    {fund_name}
                </a>
            </td>
            <td>
                {nav}
            </td>
            <td>
                {delta}
            </td>
            <td>
                {updated_date}
            </td>
        </tr>
    '''


print("Scraping in progress")
for fund_name, fund_detail in FUNDS.items():
    print(f'Scraping {fund_name}')
    fund_code = get_fund_code(fund_detail)
    soup = get_fund_soup(fund_code)
    nav, delta = get_day_change(soup)
    updated_date = get_updated_date(soup)
    content += convert_to_html(fund_name, fund_detail,
                               nav, delta, updated_date)
content.replace('\n', '')

print('Composing Email')

SERVER = 'smtp.gmail.com'  # "your smtp server"
PORT = 587  # your port number
FROM = 'bteocoding@gmail.com'  # "your from email id"
TO = 'tteo43@gmail.com'  # "your to email ids"  # can be a list
PASS = 'P@ssw0rd4523'  # "your email id's password"

msg = MIMEMultipart()
msg['Subject'] = f'Daily Investment Portfolio Update {str(now.day)}-{str(now.month)}-{str(now.year)}'
msg['From'] = FROM
msg['To'] = TO
msg.attach(MIMEText(content, 'html'))

print('Initiating Server...')

server = smtplib.SMTP(SERVER, PORT)
#server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
server.set_debuglevel(1)
server.ehlo()
server.starttls()
# server.ehlo
server.login(FROM, PASS)
server.sendmail(FROM, TO, msg.as_string())

print('Email Sent...')

server.quit()
