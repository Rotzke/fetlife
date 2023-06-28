#!/usr/bin/env python3
"""Parsing members data from current URL on FetLife website."""
import os
import csv
import sys
import logging
from time import sleep

from selenium import webdriver
from lxml import html

logging.basicConfig(format='%(asctime)s | %(levelname)s: %(message)s',
                    level=logging.INFO)

options = webdriver.ChromeOptions()
options.add_argument("headless")
driver = webdriver.Chrome(os.path.join('modules', 'chromedriver.exe'), options=options)

URL = 'https://fetlife.com'


def write_data(url, drivery):
    """Write user info into CSV file."""
    data = {}
    drivery.get(url)
    sleep(3)
    tree = html.fromstring(drivery.page_source.encode())

    data['Link to profile'] = url
    try:
        data['Name'] = tree.xpath("string(//img[contains(@class, 'db ipp w-100')]/@alt)")
    except Exception as error:
        logging.warning(error)
        data['Name'] = 'N/A'
    try:
        data['Age'] = tree.xpath("string(//*[contains(@class, 'dib us-none')])").split(' ')[0][0:2]
    except Exception as error:
        logging.warning(error)
        data['Age'] = 'N/A'
    try:
        data['Role'] = tree.xpath("string(//*[contains(@class, 'dib us-none')])").split(' ')[1]
    except Exception as error:
        logging.warning(error)
        data['Role'] = 'N/A'
    try:
        data['Location'] = ', '.join([i for i in tree.xpath("//*[contains(@class, 'mt0-s mt3 tl')]//p//text()")])
    except Exception as error:
        logging.warning(error)
        data['Location'] = 'N/A'
    try:
        d_s_first = [i.strip() for i in tree.xpath(
            "//*[text()='D/s Relationships']/following-sibling::div//div/text()")]
        d_s_last = [i.strip() for i in tree.xpath(
            "//*[text()='D/s Relationships']/following-sibling::div//span//text()")]
        if d_s_last:
            data['D/s Relationship Status'] = '; '.join(list(map(': '.join, list(zip(d_s_first, d_s_last)))))
        else:
            data['D/s Relationship Status'] = '; '.join(d_s_first)
    except Exception as error:
        logging.warning(error)
        data['D/s Relationship Status'] = 'N/A'
    try:
        d_s_first = [i.strip() for i in tree.xpath("//*[text()='Relationships']/following-sibling::div//div/text()")]
        d_s_last = [i.strip() for i in tree.xpath(
            "//*[text()='Relationships']/following-sibling::div//span//text()")]
        if d_s_last:
            data['Relationship Status'] = '; '.join(list(map(': '.join, list(zip(d_s_first, d_s_last)))))
        else:
            data['Relationship Status'] = '; '.join(d_s_first)
    except Exception as error:
        logging.warning(error)
        data['Relationship Status'] = 'N/A'
    try:
        data['Orientation'] = '; '.join([i.xpath("string(.)")
                                         for i in
                                         tree.xpath("//*[text()='Orientation']//following-sibling::div")])
    except Exception as error:
        logging.warning(error)
        data['Orientation'] = 'N/A'
    try:
        data['Active'] = '; '.join([i.xpath("string(.)")
                                    for i in
                                    tree.xpath("//*[text()='Active']//following-sibling::div")])
    except Exception as error:
        logging.warning(error)
        data['Active'] = 'N/A'
    try:
        data['Is Looking For'] = '; '.join([i.xpath("string(.)")
                                            for i in
                                            tree.xpath("//*[text()='Looking for']/following-sibling::div//div")])
    except Exception as error:
        logging.warning(error)
        data['Is Looking For'] = 'N/A'
    try:
        data['Groups member of'] = '; '.join([i.xpath("./text()")[0].strip() for i in
                                              tree.xpath("//ul[contains(@class, 'list bb b-gray-800')]//li/a")])
    except Exception as error:
        logging.warning(error)
        data['Groups member of'] = 'N/A'
    try:
        data['About me'] = tree.xpath("string(//h2[text()='About ']/following-sibling::div)")
    except Exception as error:
        logging.warning(error)
        data['About me'] = 'N/A'
    try:
        data['Fetishes'] = tree.xpath("string(//h2[text()='Fetishes ']/following-sibling::div)")
    except Exception as error:
        logging.warning(error)
        data['Fetishes'] = 'N/A'
    return data


def start_session(link, driver, first_time=False):
    """Looped main script function."""
    if not link.endswith('members') and not link.endswith('kinksters'):
        link = link.rstrip('/') + '/members'
    logging.info('Parser initialization...OK')
    if first_time:
        driver.get('https://fetlife.com/users/sign_in')
        username = driver.find_element_by_id("user_login")
        username.send_keys('CHANGEME')
        sleep(1)
        password = driver.find_element_by_id("user_password")
        password.send_keys('CHANGEME')
        sleep(1)
        logging.info('Login procedure started...')
        driver.find_element_by_xpath('//button').click()
        sleep(5)
    f_name = '{}.csv'.format('-'.join(link.split('/')[3:]))
    names = []
    # if os.path.exists(f_name):
    #     logging.warning('Found existing "{}" list'.format(f_name))
    #     with open(f_name, 'r') as f:
    #         reader = csv.DictReader(f)
    #         for i in reader:
    #             names.append(i['Name'])
    with open(f_name,
              'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Name', 'Link to profile', 'Age', 'Role', 'Location',
                      'D/s Relationship Status', 'Relationship Status',
                      'Orientation', 'Active', 'Is Looking For',
                      'Groups member of', 'About me', 'Fetishes']
        writer = csv.DictWriter(csvfile,
                                fieldnames=fieldnames)
        writer.writeheader()
        logging.info('Parsing started...')
        n = 1
        while True:
            if n % 100 == 0:
                logging.info("Reached another hundred")
                driver.close()
                driver.quit()
                sleep(5)
                logging.info('Parser initialization...OK')
                driver = webdriver.Chrome(os.path.join('modules', 'chromedriver'), options=options)
                driver.get('https://fetlife.com/users/sign_in')
                username = driver.find_element_by_id("user_login")
                username.send_keys('CHANGEME')
                sleep(1)
                password = driver.find_element_by_id("user_password")
                password.send_keys('CHANGEME')
                sleep(1)
                logging.info('Login procedure started...')
                driver.find_element_by_xpath('//button').click()
                sleep(5)
            logging.info(f'Parsing page {n}')
            driver.get(link +
                       '?page={}'.format(n))
            users = html.fromstring(driver.page_source).xpath("//div[@class='nl1 nr1 flex flex-wrap']//div[@class='w-50-ns w-100 ph1']")
            if not users:
                logging.warning(f"Group's final page reached")
                break
            else:
                n += 1
            for i in users:
                name = i.xpath("string(.//a[@class='link f5 font-bold secondary mr1'])")
                if name in names:
                    logging.info('{} is already enlisted!'.format(name))
                    continue
                sex = i.xpath("string(.//span[@class='f6 font-bold gray-300'])")
                iff = sex.strip().split('\n')[0].split(' ')[0]
                if len(iff) == 3 and iff.endswith('F'):
                    logging.info('Found {}'.format(name))
                    logging.info(URL + i.xpath("string(.//a[@class='link f5 font-bold secondary mr1']/@href)"))
                    sleep(1)
                    writer.writerow(write_data(URL +
                                               i.xpath("string(.//a[@class='link f5 font-bold secondary mr1']/@href)"), driver
                                               ))


def print_menu():
    """Print user menu."""
    print(30 * "-", "MENU", 30 * "-")
    print("1. Generate members list")
    print("2. Exit")
    print(66 * "-")


if __name__ == '__main__':
    first_time = True
    while True:
        print()
        print_menu()
        choice = input("Enter your choice [1-2]: ")
        if choice == '1':
            try:
                print()
                start_session(input('Paste URL and press "Enter":\n'), driver, first_time)
                first_time = False
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logging.critical('{} on line {}'.format(
                    e, str(exc_tb.tb_lineno)))
                input('Press any key to exit...')
                driver.close()
                exit(1)
        elif choice == '2':
            driver.close()
            exit(0)
