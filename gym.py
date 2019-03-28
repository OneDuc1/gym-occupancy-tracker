#!/usr/bin/env python3

import requests
import os
import datetime
import time
import json
import plotly
import plotly.graph_objs as go 
import pandas as pd

url = "https://www.st-andrews.ac.uk/sport/"
filename = "./data.json"

def main():
    initialise(filename)
    count=0
    while True:
        hour = int(str(datetime.datetime.now()).split(" ")[1][:6].replace(":",""))
        if hour < 2230 and hour > 630: 
            night = False
        else:
            night = True
        try:    
            read_web_and_add(night)
        except:
            print("reading from web failed. website might be down")
        if(count%12==0):
            update_plot(night)
            count=0
        time.sleep(300)
        count+=1

def read_web_and_add(night):
    if night:
        return
    hr_timestamp = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    r = requests.get(url)
    for line in r.text.split("\n"):
        if "Occupancy" in line:
            percentage = int(line.split("Occupancy: ")[1].split("<")[0][:-1])        
    entry = {'hr_t': hr_timestamp, 'p' : percentage}
    add_new_data(filename, entry)

def initialise(filename):
    if os.path.isfile(filename):
        return
    with open(filename, mode='w', encoding='utf-8') as f:
        f.write("")

def add_new_data(filename, entry):
    with open(filename, mode='a+', encoding='utf-8') as f:
        f.writelines(json.dumps(entry, sort_keys=True)+"\n")

def update_plot(night):
    if night:
        return
    df = pd.read_json(filename, lines=True)
    trace = go.Scatter(x=list(df.hr_t),
                   y=list(df.p))
    data = [trace]
    layout = dict(
                title='StA Gym occupancy (updated every hour)',
                xaxis=dict(
                    rangeselector=dict(
                        buttons=list([
                        dict(count=4,
                                label='4h',
                                step='hour',
                                stepmode='backward'),
                            dict(count=1,
                                label='1d',
                                step='day',
                                stepmode='backward'),
                            dict(count=7,
                                label='1w',
                                step='day',
                                stepmode='backward'),
                            dict(count=1,
                                label='1m',
                                step='month',
                                stepmode='backward'),
                            dict(count=6,
                                label='6m',
                                step='month',
                                stepmode='backward'),
                            dict(count=1,
                                label='1y',
                                step='year',
                                stepmode='backward'),
                            dict(step='all')
                        ])
                    ),
                    rangeslider=dict(
                        visible = True
                    ),
                    type='date'
                )
            )
    fig = dict(data=data, layout=layout)
    plotly.offline.plot(fig, filename='index.html', auto_open=False)

if __name__ == "__main__":
    main()
