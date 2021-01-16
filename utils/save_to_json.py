import json
import datetime
import numpy as np
class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj,datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return json.JSONEncoder.default(self,obj)
def save_json(dic,path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(dic,cls=DateEncoder, indent=4,ensure_ascii=False))
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)