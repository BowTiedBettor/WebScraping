from datetime import date, timedelta
import requests
import json
from traceback import print_exc

"""
A simple example of how you could use web scraping to collect online data
"""

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

def process_data(json_input: str):
    """
    DO SOMETHING
    """
    return 

data = []

start_date = date(2022, 1, 1)
end_date = date(2022, 12, 5)

for single_date in daterange(start_date, end_date):
    date = single_date.strftime("%Y-%m-%d")
    response = requests.get(f"https://www.atg.se/services/racinginfo/v1/api/calendar/day/{date}").json()
    try:
        data.append(process_data(response))
    except Exception as e:
        # print_exc()
        continue

with open('horsedata.json', 'w') as file:
    jsonobj = json.dumps(data)
    file.write(jsonobj)


