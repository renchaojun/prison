import hashlib
from pathlib import Path
import os
import json
import pickle
import numpy as np 
import datetime

def cosine_distance(x1, x2):
        minimal = 1/1e12
        c = (np.inner(x1, x2)) / (np.linalg.norm(x1) * np.linalg.norm(x2) + minimal)
        return 1 - c

def isfile(p):
    return os.path.isfile(p)


def hashstr(s: str):
    return hashlib.sha224(s.encode()).hexdigest()


def pwd(f):
    return Path(f).parent


def dump_json(filepath, obj):
    with open(filepath, 'w', encoding="utf-8") as fp:
        json.dump(obj, fp, ensure_ascii=False)
        fp.flush()
        fp.close()


def load_json(filepath):
    if os.path.isfile(filepath):
        with open(filepath, 'r', encoding='utf-8') as fp:
            try:
                data = json.load(fp)
            except:
                raise Exception('Error parse json')
            fp.close()
            return data

    raise Exception('File does not exit!')


def dump_pickle(data, file):
    with open(file, 'wb') as fp:
        pickle.dump(data, fp)
        fp.flush()
        fp.close()


def load_pickle(file):
    with open(file, 'rb') as fp:
        data = pickle.load(fp)
        fp.close()
        return data




def now():
    return ''.join(str((datetime.datetime.now())).split(" "))

if __name__ == "__main__":
    print(hashstr("hello"))
    print(pwd(__file__))
    print(now())

