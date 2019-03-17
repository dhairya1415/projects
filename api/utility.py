import requests
import json
import pandas as pd
from pdf_generation.task import import_data


def generate_csv(report_data, event_data):
    df = pd.DataFrame.from_dict(report_data)
    pf = pd.DataFrame.from_dict([event_data])
    df["image"][0] = report_data["image"]
    df = df.drop(range(1, len(report_data["image"])))
    yf = pf.join(df)
    yf.to_csv("media/csv/{}.csv".format(event_data["name"]))
    file = "media/csv/{}.csv".format(event_data["name"])
    import_data(file)
