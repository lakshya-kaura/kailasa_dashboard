import undetected_chromedriver as uc
import time
import pandas as pd
import numpy as np
import time
import datetime
from datetime import date
import warnings
import streamlit as st # web development
import numpy as np # np mean, np random 
import pandas as pd # read csv, df manipulation
import time # to simulate a real time data, time loop 
import plotly.express as px # interactive charts 
from PIL import Image
from login.login import login, login_all, login_window
from csv import DictWriter
import plotly.graph_objects as go
import plotly.express as px
import termplotlib as tpl
from kill_switch import cancel_all_pending_orders,close_all_open_positions, kill_orders
import json

warnings.filterwarnings("ignore",category=FutureWarning)

##! LOGIN ##


credentials = pd.read_csv("login\\credentials.csv")
accounts = credentials['user_id'].to_list()
for user_id in accounts:
    if user_id is np.nan:
        continue
    try:
        account_login = login(user_id)
    except:
        print("Error logging into: ",user_id)
credentials = login_all()


##! Streamlit ##


logo =  Image.open("Kailasa Favicon.png")
full_logo = Image.open("Kailasa Full Logo.png")

st.set_page_config(
    page_title = 'KAILASA CAPITAL',
    page_icon = logo,
    layout = 'wide'
)

col1, col2, col3 = st.columns(3)

with col1:
    st.write(' ')

with col2:
    st.image(full_logo)

with col3:
    st.write(' ')


##! Login from app ##


list_accounts = list(credentials['user_id'])

with st.form("Login Form"):
    account = st.selectbox("Select Account for login :", list_accounts)
    submit_button = st.form_submit_button(label="Login")

if submit_button:
    login_window(account)


##! Kill Switch ##


list_accounts = list(credentials['user_id'])
list_kite_objects = list(credentials['object'])

with st.form("Kill Positions"):
    account = st.multiselect("Select Account to kill all its positions :", list_accounts)

    try:
        kite = list(credentials.loc[credentials['user_id'].isin(account)]['object'])    # This is a list of objects
    except Exception as e:
        print('Exception : ',e)
        pass

    kill_orders_button = st.form_submit_button(label="Kill all orders")


if kill_orders_button:
    kill_orders(kite)

    print(f"Kill all orders for user {account}")
    st.write(f"Killed all orders for user {account}")

    #! JSON   

    for user in account:
        f = open('removed_accounts.json')
        data = json.load(f)
        removed_accounts = data['accounts']
        removed_accounts.append(user)
        removed_accounts = list(set(removed_accounts))

    jsonFile = open('removed_accounts.json', "r+")
    removed_accounts = json.dumps(removed_accounts)
    entry = str({json.dumps('accounts'):removed_accounts}) 
    entry = entry.replace("'","")
    jsonFile.write(entry)
    jsonFile.close()




# streamlit run 'c:/Users/Kailasa Capital/Desktop/Trial/Dashboard/Dashboard_login.py'