from pymongo import MongoClient, ASCENDING
import csv
import yaml
import os
import re
import aozora_parser

mongodb_config = yaml.load(open('config.yml', 'rt', encoding="utf-8"))["mongoDB"]
DB_HOST = mongodb_config.get("host", "localhost")
DB_PORT = mongodb_config.get("port", 27017)
DB_NAME = mongodb_config["db_name"]
COLLECTION_NAME = mongodb_config["collection_name"]


def get_filename_dict(aozora_dir):
    if not os.path.isdir(aozora_dir):
        raise Exception("指定されたパスはディレクトリじゃないようです。")
    filename_dict = dict()
    for f in os.listdir(aozora_dir):
        f = aozora_dir + f
        if not os.path.isfile(f):
            continue
        title, author = aozora_parser.get_title_and_author(f)
        if title and author:
            filename_dict[(title, author)] = f
    return filename_dict


def register(aozora_dir, list_person_all_extended, encoding="UTF-8"):
    filename_dict = get_filename_dict(aozora_dir)

    # 青空文庫のメタデータ読み込み
    with open(file=list_person_all_extended, encoding=encoding) as fi:
        ci = csv.reader(fi)
        extended = [row for row in ci][1:]

    # mongoDB接続
    with MongoClient(DB_HOST, DB_PORT) as client:
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        collection.create_index([("ID", ASCENDING)])
    for row in extended:
        title = row[1]
        sub_title = row[4]
        if len(sub_title) > 0:
            title = title + "\t" + sub_title  # 副題があれば付ける
        author = row[15] + row[16]
        # print("register:", title, author)
        filename = filename_dict.get((title, author), "not found")
        if filename == "not found":
            continue

        # 初版情報のあるものに限定させてください
        first_pub = row[7]
        m = re.search(pattern="[0-9]{4}(?=（)", string=first_pub)
        if not m:
            continue

        doc = dict()
        doc["ID"] = row[0]
        doc["title"] = title
        doc["filename"] = filename
        doc["year"] = int(m.group())
        doc["author"] = author
        collection.insert_one(doc)
