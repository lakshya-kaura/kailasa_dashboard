import time
import pandas as pd
import numpy as np
import datetime
import warnings
import streamlit as st # web development
import numpy as np # np mean, np random 
import pandas as pd # read csv, df manipulation
import time # to simulate a real time data, time loop 
import plotly.express as px # interactive charts 
from PIL import Image
from login.login import login, login_all, login_window
import plotly.graph_objects as go

import warnings
warnings.filterwarnings('ignore')


##! LOGIN ##

credentials = pd.read_csv("login/credentials.csv")
print(credentials)
accounts = credentials['user_id'].to_list()
for user_id in accounts:
    if user_id is np.nan:
        continue
    try:
        account_login = login(user_id)
    except:
        print("Error logging into: ",user_id)
credentials = login_all()


##! Erase old data from df_pnl and df_roi CSV's (Empty dataframes) ##
users = list(credentials['user_id'])

df_pnl = pd.read_csv('df_pnl.csv',parse_dates=['date'])
df_roi = pd.read_csv('df_roi.csv',parse_dates=['date'])

try:
    if df_pnl['date'].iloc[0] != datetime.datetime.now().date():
        df_pnl.drop(df_pnl.index , inplace=True)
        df_pnl.to_csv('df_pnl.csv',index=False)
except:
    pass

try:
    if df_roi['date'].iloc[0] != datetime.datetime.now().date():
        df_roi.drop(df_roi.index , inplace=True)
        df_roi.to_csv('df_roi.csv',index=False)
except:
    pass


##! FUNCTIONS ##

def positions_pnl_margin_roi(object):
    df_pnl = pd.read_csv('df_pnl.csv')
    df_roi = pd.read_csv('df_roi.csv')
    df_table = pd.DataFrame(columns=['user_id','pnl','margin','Nifty CE','Nifty PE','BankNifty CE','BankNifty PE','object'])

    #! Filling values in some columns of (df_pnl, df_roi and df)
    users = list(credentials['user_id'])
    objects = list(credentials['object'])

    # df_table
    df_table['user_id'] = users
    df_table['object'] = objects

    # df_pnl and df_roi
    time_str = datetime.datetime.now().strftime("%H:%M")
    today_date = datetime.datetime.now().date()
    
    df_pnl_row = {'time': time_str,'date': today_date}
    df_pnl = df_pnl.append(df_pnl_row, ignore_index = True)
    df_roi = df_roi.append(df_pnl_row, ignore_index = True)

    for object in objects:
        user = credentials[credentials['object'] == object]['user_id'].iloc[0]

        try:

            #! number of positions
            try:
                list_orders = object.orders()
                list_orders = (list(filter(lambda d: d['status'] in ['COMPLETE'], list_orders)))

                list_positions = object.positions()['day']

                pnl = 0
                bn_ce_positions = 0
                bn_pe_positions = 0
                nifty_ce_positions = 0
                nifty_pe_positions = 0

                for position in list_positions:
                    if (position['tradingsymbol'][-2:] == "PE") & (position['tradingsymbol'][:4] == "BANK"):
                        bn_pe_positions = bn_pe_positions + position['quantity']

                    elif (position['tradingsymbol'][-2:] == "CE") & (position['tradingsymbol'][:4] == "BANK"):
                        bn_ce_positions = bn_ce_positions + position['quantity']
                    
                    elif (position['tradingsymbol'][-2:] == "PE") & (position['tradingsymbol'][:5] == "NIFTY"):
                        nifty_pe_positions = nifty_pe_positions + position['quantity']
                        
                    elif (position['tradingsymbol'][-2:] == "CE") & (position['tradingsymbol'][:5] == "NIFTY"):
                        nifty_ce_positions = nifty_ce_positions + position['quantity']

                #! pnl

                for order in list_orders:
                    for i in range(0,10):

                        try:
                            exchange = order['exchange']
                            tradingsymbol = exchange + ':' + str(order['tradingsymbol'])
                            avg_price = order['average_price']

                            last_price = object.ltp([tradingsymbol])[tradingsymbol]['last_price']
                        
                            transaction_type = order['transaction_type']
                            if transaction_type == 'SELL':
                                quantity = -(order['quantity'])
                            else:
                                quantity = order['quantity']

                            if quantity==0:
                                pnl_i = order['pnl']
                            else:
                                pnl_i = (last_price - avg_price) * quantity

                            pnl = pnl + pnl_i
                            break

                        except:
                            print(f"Trying Again for PNL {user}")

                pnl_final = round(pnl)

                df_pnl.loc[df_pnl['time']==time_str,user] = pnl_final
                df_pnl.drop_duplicates(inplace=True)
                df_pnl.to_csv('df_pnl.csv', index=False)
                
                #! ROI

                capital = credentials[credentials['object'] == object]['capital'].iloc[0]
                roi = (pnl_final/capital)*100
                df_roi.loc[df_roi['time']==time_str,user] = roi
                df_roi.drop_duplicates(inplace=True)
                df_roi.to_csv('df_roi.csv', index=False)

                #! Updating df with pnl and number of positions
                df_table.loc[df_table['object']==object,['pnl','Nifty CE','Nifty PE','BankNifty CE','BankNifty PE']] = pnl_final,nifty_ce_positions,nifty_pe_positions,bn_ce_positions,bn_pe_positions

            except Exception as e:
                print(f'Exception for {user} ::: ',e)

            #! margin

            for i in range(0,10):
                try:
                    #! updating df with margin
                    df_table.loc[df_table['object']==object,'margin'] = round(object.margins()['equity']['net'])
                    break
                except Exception as e:
                    print(f'Exception in margins for {user} ::: ',e)
                    print('Trying to find Margin Again')

        except Exception as e:
            print('Exception ::: ', e)
        
    return df_table,df_pnl,df_roi


def color_negative_red(val):
    color = 'red' if val < 0 else 'green'
    return 'color: %s' % color


def create_plotly_graph(dataframe,title,xaxis_title,yaxis_title,y_axis_min,y_axis_max):
    fig = go.Figure()

    #! Add 0 line
    fig.add_hline(y=0,line=dict(color="#FFFFFF"),line_dash="dash",opacity=0.75)

    #! Add color on positive and negative zones
    fig.add_hrect(y0=0, y1=y_axis_min, line_width=0, fillcolor="Red",opacity=0.1,layer="below")
    fig.add_hrect(y0=0, y1=y_axis_max, line_width=0, fillcolor="Green",opacity=0.1,layer="below")

    #! Add a line trace for 'PNL' for AJ1440  
    fig.add_trace(go.Scatter(x=dataframe.index, y=dataframe['AJ1440'], mode='lines+markers+text', name='AJ1440', line=dict(color="#8676ff")))    # text=df_pnl['AJ1440'], textposition='top center'

    #! Add a line trace for 'PNL' for VR2386
    fig.add_trace(go.Scatter(x=dataframe.index, y=dataframe['VR2386'], mode='lines+markers+text', name='VR2386', line=dict(color="#fa76ff")))

    #! Add a line trace for 'PNL' for EBV374
    fig.add_trace(go.Scatter(x=dataframe.index, y=dataframe['EBV374'], mode='lines+markers+text', name='EBV374', line=dict(color="#FFD700")))

    #! Add a line trace for 'PNL' for TCX177
    fig.add_trace(go.Scatter(x=dataframe.index, y=dataframe['TCX177'], mode='lines+markers+text', name='TCX177', line=dict(color="#57f7e5")))

    #! Add a line trace for 'PNL' for ZOZ283
    fig.add_trace(go.Scatter(x=dataframe.index, y=dataframe['ZOZ283'], mode='lines+markers+text', name='ZOZ283', line=dict(color="#7CFC00")))

    #! Customize the plot
    fig.update_layout(
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        plot_bgcolor='rgba(32, 32, 32, 1)',
        height = 800,
        hovermode='x unified',
        hoverlabel=dict(
        font_size=20,
        font_family="Rockwell"
        ),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=True,
            linecolor='white'
        ),
        yaxis=dict(
            showgrid=False, 
            zeroline=False,
            showline=True,
            linecolor='white',
            dtick=0.5
        ),
        title_font=dict(color='white'),
        xaxis_title_font=dict(color='white'),
        yaxis_title_font=dict(color='white'),
    )

    fig.update_traces(marker=dict(color='rgba(255, 255, 255, 1)'), textfont=dict(color='white'))

    return fig


##! CSS to inject contained in a string ##
hide_table_row_index = """
            <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>
            """


##! STREAMLIT ##

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

placeholder = st.empty()

#! While loop #

while datetime.datetime.now().time() < datetime.time(15,31):

    df_table,df_pnl,df_roi = positions_pnl_margin_roi(object)

    #! fig_pnl
    # df_pnl = df_pnl.set_index('time')
    # y_axis_max = (df_pnl.max(numeric_only=True)).max() + 1000
    # y_axis_min = (df_pnl.min(numeric_only=True)).min() - 1000

    # fig_pnl = create_plotly_graph(dataframe =df_pnl, title ='ACCOUNT PNL', xaxis_title='TIME', yaxis_title ='PNL')
    # fig_pnl.update_layout(yaxis_range=[y_axis_min, y_axis_max])
    
    #! fig_roi
    df_roi = df_roi.set_index('time')
    y_axis_max = (df_roi.max(numeric_only=True)).max() + 0.25

    y_axis_min = (df_roi.min(numeric_only=True)).min() 
    y_axis_min = abs(y_axis_min) + 0.25 

    if y_axis_max>y_axis_min:
        y_axis_max = y_axis_max
        y_axis_min = -(y_axis_max)
    else:
        y_axis_max = y_axis_min
        y_axis_min = -(y_axis_min)

    fig_roi = create_plotly_graph(dataframe =df_roi, title ='ACCOUNT ROI', xaxis_title='TIME', yaxis_title ='ROI',y_axis_min = y_axis_min, y_axis_max = y_axis_max)
    
    fig_roi.update_layout(yaxis_range=[y_axis_min, y_axis_max])

    #! Some operations on df_table
    df_table.drop(['object'],axis=1,inplace=True)
    df_table.rename(columns = {'user_id':'user'}, inplace = True)
    df_table.columns = df_table.columns.str.upper()
  
    #! Beautify the df_table
    border = '4px solid white'
    thick_border = '4px solid white'
    table_styles = [dict(selector='th', props=[('border', border), ('border-width', '4px'), ('text-align', 'center')]),
                    dict(selector='th.col_heading', props=[('border', thick_border), ('border-width', '4px')]),
                    dict(selector='td', props=[('border', border), ('border-width', '4px'), ('text-align', 'center')])]

    df_table = df_table.style.hide_index().applymap(color_negative_red, subset=['PNL'])
    df_table = df_table.set_properties(**{'font-weight': 'bold'})
    df_table = df_table.set_table_styles(table_styles)
    df_table = df_table.format({'PNL': '₹ {:,.0f}', 'MARGIN': '₹ {:,.0f}'}) 
    

    #! Inject CSS with Markdown
    st.markdown(hide_table_row_index, unsafe_allow_html=True)

    #! Placeholder
    with placeholder.container():        

        st.table(df_table)
        # st.plotly_chart(fig_pnl,use_container_width=True)
        st.plotly_chart(fig_roi,use_container_width=True,height = 800)  


else:
    df_pnl_eod = pd.read_csv('df_pnl_eod.csv')

    if df_pnl_eod['date'].iloc[-1] != datetime.datetime.now().date().strftime('%Y-%m-%d'):
 
        #! df_pnl_final
        df_pnl = pd.read_csv('df_pnl.csv')
        df_pnl_final = pd.read_csv('df_pnl_final.csv')
        df_pnl_final = pd.concat([df_pnl_final, df_pnl])
        df_pnl_final.to_csv('df_pnl_final.csv',index=False)


        #! df_pnl_eod and credentials 
        users = list(credentials['user_id'])
        objects = list(credentials['object'])

        date_today = datetime.datetime.now().date().strftime('%Y-%m-%d')
        df_pnl_eod_row = {'date': date_today}
        df_pnl_eod = df_pnl_eod.append(df_pnl_eod_row, ignore_index = True)
        
        for object in objects:
            user = credentials[credentials['object'] == object]['user_id'].iloc[0]
            capital = credentials[credentials['object'] == object]['capital'].iloc[0]   

            df_table = pd.DataFrame(object.positions()['day'])
            pnl = df_table['pnl'].sum()
            capital_new = capital + pnl

            df_pnl_eod.loc[df_pnl_eod['date']==date_today,user] = pnl
            credentials.loc[credentials['user_id']==user,'capital'] = capital_new
            
        df_pnl_eod.to_csv('df_pnl_eod.csv', index=False)
        credentials.to_csv('login/credentials.csv', index=False)

print('Done for the day')


 
