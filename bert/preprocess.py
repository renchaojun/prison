from utils2 import load_json, load_pickle, dump_json, dump_pickle, pwd
import os
import jieba

def is_chinese_char(cp):
    if ((cp >= 0x4E00 and cp <= 0x9FFF) or  #
            (cp >= 0x3400 and cp <= 0x4DBF) or  #
            (cp >= 0x20000 and cp <= 0x2A6DF) or  #
            (cp >= 0x2A700 and cp <= 0x2B73F) or  #
            (cp >= 0x2B740 and cp <= 0x2B81F) or  #
            (cp >= 0x2B820 and cp <= 0x2CEAF) or
            (cp >= 0xF900 and cp <= 0xFAFF) or  #
            (cp >= 0x2F800 and cp <= 0x2FA1F)):  #
        return True

    return False

def get_stop_words(file_dir=os.path.join(pwd(__file__),"./stopwords")) -> set:
    stop_wordss = set()
    for file in os.listdir(file_dir):
        if ".txt" in file:
            with open(os.path.join(file_dir, file), 'r', encoding='utf-8') as fp:
                words = set([w.strip() for w in fp.readlines()])
                for word in words:
                    stop_wordss.update(jieba.cut(word))
    return stop_wordss

def clean_none_chinese(text):
    text = ''.join([w if is_chinese_char(ord(w)) else '' for w in text])
    return text
def remove_str(s1,s2):
    flag = 1
    while flag == 1:  # 若无子字符串在内则跳出循环
        flag = 0
        if s2 in s1:
            s1 = s1.replace(s2, '')
            flag = 1
    return s1
def cutwords(docs:list):
    stopwords=get_stop_words()
    datas=[]
    for i,doc in enumerate(docs):
        docs[i]=remove_str(docs[i],"岁")
        docs[i]=remove_str(docs[i],"犯")
        docs[i]=remove_str(docs[i],"罪")
    for data in docs:
        data=clean_none_chinese(data)
        data=list(jieba.cut(data))
        datas.append([w for w in data if w not in stopwords])
    
    return datas

    


class DataLoader(object):
    def __init__(self, filepath=os.path.join(pwd(__file__), './data/data.json'), num_category=3, num_per_catetory=4):
        self.file = filepath
        self.num_category = num_category
        self.num_per_catetory = num_per_catetory

    def __call__(self)->list:
        datas = load_json(os.path.join(pwd(__file__), './data/data.json'))
        return datas


if __name__ == "__main__":
    loader=DataLoader()
    print(len(loader()))
    print(cutwords(['你好吗，我的名字是','你说的没错']))
    print(len(get_stop_words()))
    # datas = load_json(os.path.join(pwd(__file__), './data/data.json'))
    # categorys = set()
    # for data in datas:
    #     categorys.add(data['category'])
    # assert len(categorys) == 3
    # categorys = list(categorys)

    # assert len([data for data in datas if data['category'] == categorys[0]]) == \
    #     len([data for data in datas if data['category'] == categorys[1]]) == \
    #     len([data for data in datas if data['category'] == categorys[2]])
    # print(len(datas))
