import requests
import json
import pandas as pd
from pdf_generation.task import import_data
import json

month_dict = [
    "months",
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


def generate_csv(report_data, event_data):
    report_data = json.loads(report_data)[0]
    event_data = json.loads(event_data)[0]
    df = pd.DataFrame.from_dict(report_data)
    pf = pd.DataFrame.from_dict(event_data)
    y = []
    print(report_data)
    for i in range(len(report_data["image"])):
        z = requests.get(report_data["image"][i])
        z = z.json()
        y.append(z["image"])
    df["image"][0] = y
    df = df.drop(range(1, len(report_data["event_data"])))
    df = df.drop(range(1, len(report_data["image"])))
    yf = pf.merge(df,how='outer')
    yf.to_csv("media/csv/{}.csv".format(event_data["name"]))
    file = "media/csv/{}.csv".format(event_data["name"])
    import_data(file)
