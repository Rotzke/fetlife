#!/usr/bin/python3.5
"""Parsing members data from current URL on FetLife website."""
import csv
import sys
import logging
from time import sleep

import requests
import clipboard
from bs4 import BeautifulSoup

logging.basicConfig(format='%(asctime)s | %(levelname)s: %(message)s',
                    level=logging.INFO)


def soup_filter(html, tag=None, _class=None, multiple=True):
    """Beautifulsoup filtering function."""
    if tag is None:
        return BeautifulSoup(html, 'html.parser')
    elif multiple:
        return BeautifulSoup(html, 'html.parser').findAll(tag, _class)
    elif not multiple:
        return BeautifulSoup(html, 'html.parser').find(tag, _class)


def write_data(url, session, headers, cookies):
    """Write user info into CSV file."""
    data = {}
    raw_user = session.get(url, headers=headers, cookies=cookies)
    user_soup = soup_filter(raw_user.text)
    data['Link to profile'] = url
    data['Name'] = user_soup.find('img', {'class': 'pan'})['alt']
    data['Age'] = user_soup.find('span',
                                 {'class':
                                  'small quiet'}).text.split(' ')[0][0:2]
    try:
        data['Role'] = user_soup.find('span',
                                      {'class':
                                       'small quiet'}).text.split(' ')[1]
    except AttributeError:
        data['Role'] = ''
    try:
        data['Location'] = user_soup.find('div',
                                          {'class':
                                           'span-13 append-1'}).p.text
    except AttributeError:
        data['Location'] = ''
    try:
        data['D/s Relationship Status'] =\
            user_soup.find(text='relationship status:'
                           ).parent.parent.ul.text.strip().replace('\n', ', ')
    except AttributeError:
        data['D/s Relationship Status'] = ''
    try:
        data['Relationship Status'] =\
            user_soup.find(text='D/s relationship status:'
                           ).parent.parent.ul.text.strip().replace('\n', ', ')
    except AttributeError:
        data['Relationship Status'] = ''
    try:
        data['Orientation'] =\
            user_soup.find(text='orientation:'
                           ).parent.parent.td.text
    except AttributeError:
        data['Orientation'] = ''
    try:
        data['Active'] =\
            user_soup.find(text='active:'
                           ).parent.parent.td.text
    except AttributeError:
        data['Active'] = ''
    try:
        data['Is Looking For'] =\
            ('\n').join([i for i in user_soup.find(text='is looking for:'
                                                   ).parent.parent.td.contents
                         if isinstance(i, str)])
    except AttributeError:
        data['Is Looking For'] = ''
    try:
        data['Groups member of'] =\
            ('\n').join([i.a.text for i in
                         user_soup.find(text='Groups member of'
                                        ).find_next('ul',
                                                    {'class':
                                                     'list'}).contents])
    except AttributeError:
        data['Groups member of'] = ''
    try:
        data['About me'] = ''
        for tag in user_soup.find('h3',
                                  {'class':
                                   'bottom'}, text='About me '
                                  ).next_siblings:
            if tag.name == "h3":
                break
            else:
                try:
                    data['About me'] += tag.string
                except TypeError:
                    continue
    except AttributeError:
        data['About me'] = ''
    try:
        data['Fetishes'] = ''
        for tag in user_soup.find('h3',
                                  {'class':
                                   'bottom'}, text='Fetishes'
                                  ).next_siblings:
            if tag.name == "h3":
                break
            else:
                try:
                    data['Fetishes'] += tag.text
                except (TypeError, AttributeError):
                    continue
    except AttributeError:
        data['Fetishes'] = ''
    return data


def start_session(link):
    """Looped main script function."""
    logging.info('Parser initialization...OK')
    URL = 'https://fetlife.com'
    session = requests.Session()
    headers = {'User-Agent': """Mozilla/5.0 (X11; Linux x86_64) """
               """AppleWebKit/537.36 (KHTML, like Gecko) """
               """Chrome/58.0.3029.110 Safari/537.36"""}
    raw_token = session.get(
        'https://fetlife.com/users/sign_in', headers=headers)
    token = soup_filter(raw_token.text, tag='input',
                        _class={'name': 'authenticity_token'},
                        multiple=False)['value']
    payload = {'authenticity_token': token,
               'user[login]': '',
               'user[password]': '',
               'user[locale]': 'en',
               'user[otp_attempt]': 'step_1',
               'utf8': '✓'}
    login = session.post('https://fetlife.com/users/sign_in',
                         headers=headers,
                         data=payload)
    if login.status_code != 200:
        logging.critical('Invalid credentials or website problems! Exiting...')
    n = 1
    with open('{}.csv'.format(('-').join(link.split('/')[3:])),
              'w', newline='') as csvfile:
        fieldnames = ['Link to profile', 'Name', 'Age', 'Role', 'Location',
                      'D/s Relationship Status', 'Relationship Status',
                      'Orientation', 'Active', 'Is Looking For',
                      'Groups member of', 'About me', 'Fetishes']
        writer = csv.DictWriter(csvfile,
                                fieldnames=fieldnames)
        writer.writeheader()
        while True:
            page = session.get(link +
                               '?page={}'.format(n),
                               headers=headers, cookies=session.cookies)
            users = soup_filter(page.text,
                                tag='div',
                                _class={'class':
                                        'fl-member-card'})
            if len(users) == 0:
                logging.info('Parsed last page! Exiting...')
                break
            else:
                logging.info('Parsing page {}\n'.format(n))
            for i in users:
                sex = i.find('span', {'class': 'fl-member-card__info'})
                iff = sex.text.strip().split('\n')[0]
                if len(iff) == 3 and iff.endswith('F'):
                    logging.info('Found {}!'.format(sex.parent.a.text))
                    writer.writerow(write_data(URL +
                                               i.find('a',
                                                      {'class':
                                                       'fl-member-card__user'
                                                       })['href'],
                                               session,
                                               headers,
                                               session.cookies))
            n += 1


def print_menu():
    """Print user menu."""
    print(30 * "-", "MENU", 30 * "-")
    print("1. Generate members list")
    print("2. Exit")
    print(66 * "-")


if __name__ == '__main__':
    while True:
        print()
        print_menu()
        choice = input("Enter your choice [1-2]: ")
        if choice == '1':
            try:
                print()
                input('Copy URL and press any key...')
                if clipboard.paste().startswith(('https://', 'http://')):
                    print()
                    start_session(clipboard.paste())
                    break
                else:
                    logging.warning("""Invalid URL provided - """
                                    """it has to start with http(s)!""")
                    sleep(2)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logging.critical('{} on line {}'.format(
                    e, str(exc_tb.tb_lineno)))
                input('Press any key to exit...')
                exit(1)
        elif choice == '2':
            exit(0)
