import datetime
import configparser

from kiteconnect import KiteTicker
from kiteconnect import KiteConnect

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os.path
from os import system

import json
import pyotp
import requests
import numpy as np
import pandas as pd
from time import sleep
import urllib.parse as urlparse

import telegram
import os

def login(user_id, method='standard'):
    """
    login method can be jugaad or standard
    """
    
    #give path to credentials file here
    credentials_file = pd.read_csv('login/credentials.csv')

    method = credentials_file[credentials_file['user_id'] == user_id]['method'].iloc[0]

    if method == 'standard':


        api_key = credentials_file[credentials_file['user_id'] == user_id]['api_key'].iloc[0]
        api_secret = credentials_file[credentials_file['user_id'] == user_id]['api_secret'].iloc[0]
        account_username = credentials_file[credentials_file['user_id'] == user_id]['user_id'].iloc[0]
        account_password = credentials_file[credentials_file['user_id'] == user_id]['password'].iloc[0]
        totp = credentials_file[credentials_file['user_id'] == user_id]['totp'].iloc[0]
        auth_key = pyotp.TOTP(totp)

        kite = KiteConnect(api_key=api_key)

        #check whether today's date is the same as the date saved in access token date in csv
        #checking for 2 date formats as sometimes after opening csv, excel changes format
        if ((credentials_file[credentials_file['user_id'] == user_id]['access_token_date'].iloc[0] == datetime.datetime.today().date().strftime('%d-%m-%Y')) | (credentials_file[credentials_file['user_id'] == user_id]['access_token_date'].iloc[0] == str(datetime.datetime.today().date()))):
            access_token = credentials_file[credentials_file['user_id'] == user_id]['access_token'].iloc[0]
            print(f'Access Token Generated Earlier Today for {user_id}')


        else:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            driver = webdriver.Chrome(executable_path='login/chromedriver.exe',options=options)
            #driver = webdriver.Chrome(ChromeDriverManager().install())
            driver.get(kite.login_url())
            sleep(2)
            form = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="login-form"]')))
            driver.find_element("xpath","//input[@type='text']").send_keys(account_username)
            driver.find_element("xpath","//input[@type='password']").send_keys(account_password)

            driver.find_element("xpath","//span[@class='su-checkbox-box']").click()
            driver.find_element("xpath","//button[@type='submit']").click()
            sleep(2)
            form = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="login-form"]//form')))
            driver.find_element("xpath","//input[@type='text']").send_keys(auth_key.now())
            driver.find_element("xpath","//button[@type='submit']").click()
            sleep(2)

            current_url = driver.current_url
            driver.close()

            parsed = urlparse.urlparse(current_url)
            request_token = urlparse.parse_qs(parsed.query)['request_token'][0]
            access_token = kite.generate_session(request_token=request_token,api_secret=api_secret)['access_token']

            #Writing access token, date and object to credentials file
            credentials_file.loc[credentials_file['user_id'] == user_id,'access_token_date'] = str(datetime.datetime.today().date())
            credentials_file.loc[credentials_file['user_id'] == user_id,'access_token'] = access_token
            credentials_file.loc[credentials_file['user_id'] == user_id,'object'] = kite

            #save the config file
            try:
                credentials_file.to_csv('login/credentials.csv',index=False)
                print("Saved credentials csv for",user_id)
            except:
                print(f"Error while saving {user_id} access token to csv. Maybe the credentials csv file is open.")
                

                
        login_success_counter = 0 #to track whether account got logged in or not
        
        try:
            kite.set_access_token(access_token)
            kite_login_message = str(f"Login success for ID: {kite.profile()['user_id']}")
            print(kite_login_message)
            login_success_counter = "Yes"
        except:
            kite_login_message = str(f"ERROR logging into ID: {kite.profile()['user_id']}")
            print(kite_login_message)
            login_success_counter = "No"
            
    elif method == 'jugaad':
        pass
    
    return kite,kite_login_message,login_success_counter

def login_all():
    credentials = pd.read_csv('login/credentials.csv')
    #login process has already been done when initialising Raptor, but this process check login status once again
    #iterate over the accounts in the accounts dictionary and login each one of them, in case not already done
    #in case unable to login, print an error message and also send to the group
    
    for user_id in credentials['user_id'].to_list():
        try:
            credentials.loc[credentials['user_id'] == user_id,'object'] = login(user_id,credentials[credentials['user_id'] == user_id]['method'].iloc[0])[0]
            print('success')
        except:
            print("Could not login to",user_id)

    return credentials

def login_window(user_id):
    """
    login ina a new window
    """

    #give path to credentials file here
    try:
        credentials_file = pd.read_csv('login/credentials.csv')

        account_username = credentials_file[credentials_file['user_id'] == user_id]['user_id'].iloc[0]
        account_password = credentials_file[credentials_file['user_id'] == user_id]['password'].iloc[0]
        totp = credentials_file[credentials_file['user_id'] == user_id]['totp'].iloc[0]
        auth_key = pyotp.TOTP(totp)

        options = Options()
        options.add_argument('--disable-gpu')
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(executable_path='login/chromedriver.exe',options=options)
        driver.get('https://kite.zerodha.com/')
        driver.maximize_window()
        sleep(2)
        form = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="login-form"]')))
        driver.find_element("xpath","//input[@type='text']").send_keys(account_username)
        driver.find_element("xpath","//input[@type='password']").send_keys(account_password)
        driver.find_element("xpath","//button[@type='submit']").click()
        sleep(2)
        form = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="login-form"]//form')))
        driver.find_element("xpath","//input[@type='text']").send_keys(auth_key.now())
        driver.find_element("xpath","//button[@type='submit']").click()
        sleep(2)
    except Exception as e:
        print(f'Unable to login {user_id} : ',e)



if __name__ == '__main__':

    ## LOGIN ##

    credentials = pd.read_csv("login/credentials.csv")
    accounts = credentials['user_id'].to_list()

    for user_id in accounts:
        if user_id is np.nan:
            continue
        try:
            account_login = login(user_id)

        except:
            print("Error logging into: ",user_id)

    credentials = login_all()
