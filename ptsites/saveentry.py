import json
import datetime


def save(entry):
    temp = {
        "site_name": entry["site_name"],
        "time": datetime.datetime.now().strftime("%Y/%m/%d %H:%M"),
    }
    temp.update(entry["details"])
    temp = json.dumps(temp)
    with open("./data.json", "a") as f:
        f.write(temp)
        f.write("\n")
