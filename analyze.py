import register_to_db
import aozora_parser
import yaml
import sudachipy
from sudachipy import dictionary
import json
from pymongo import MongoClient


def build_tokenizer():
    """
    SudachiのTokenizerを作るよ
    """
    with open(sudachipy.config.SETTINGFILE, encoding="utf-8") as f:
        settings = json.load(f)
        dict_ = dictionary.Dictionary(settings)
    return dict_.create()


def analyze():
    """
    任意の単語が出現した最古の作品を調べるよ
    """
    # mongoDB接続
    with MongoClient(DB_HOST, DB_PORT) as client:
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
    morpheme_dict = dict()
    for doc in collection.find():
        filename = doc["filename"]
        year = doc["year"]
        morpheme_set = parse(filename)
        for m in morpheme_set:
            item = morpheme_dict.get(m, dict())
            min_year = item.get("year", 10000)
            if year < min_year:
                item["year"] = year
                item["ID"] = doc["ID"]
                morpheme_dict[m] = item
    # ファイル書き出し
    write(OUTPUT_FILE, morpheme_dict)

    # 適当に10個表示してみる
    import random
    selected = [(key, value) for key, value in morpheme_dict.items()]
    random.shuffle(selected)
    print(selected[:10])


def write(outputfile, morpheme_dict):
    """
    結果を書き出すよ
    :return:
    """
    with open(file=outputfile, mode="wt", encoding="UTF-8") as fw:
        for morpheme, item in morpheme_dict.items():
            fw.write(",".join([morpheme, str(item["year"]), item["ID"]]) + "\n")
            fw.flush()


def parse(file, encoding="shift_jisx0213"):
    """
    名詞単語の正規化した表現を抽出するよ
    :param file:
    :param encoding:
    :return:
    """
    lines = aozora_parser.get_context(file, encoding)
    morphehe_set = set()
    tokenized = [tokenizer.tokenize(MODE, line) for line in lines]
    for mlist in tokenized:
        for m in mlist:
            # 品詞取得時にエラーを吐くことがある
            try:
                if m.part_of_speech()[0] == "名詞":
                    morphehe_set.add(m.normalized_form())
            except:
                pass
    return morphehe_set


CONFIG = yaml.load(open('config.yml', 'rt', encoding="utf-8"))
AOZORA_DIR = CONFIG["aozora"]["directory"]
LIST_PERSON_ALL_EXTENDED = CONFIG["aozora"]["list_person_all_extended"]
DB_HOST = CONFIG["mongoDB"].get("host", "localhost")
DB_PORT = CONFIG["mongoDB"].get("port", 27017)
DB_NAME = CONFIG["mongoDB"]["db_name"]
COLLECTION_NAME = CONFIG["mongoDB"]["collection_name"]
OUTPUT_FILE = CONFIG["outputfile"]

tokenizer = build_tokenizer()
MODE = tokenizer.SplitMode.C


def main():
    # 今後扱いやすいようにmongoDBに作品情報を登録しておく
    register_to_db.register(aozora_dir=AOZORA_DIR, list_person_all_extended=LIST_PERSON_ALL_EXTENDED)
    # DBの情報を元に解析する
    analyze()


if __name__ == '__main__':
    main()
