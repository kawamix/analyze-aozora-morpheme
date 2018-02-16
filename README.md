# 任意の単語が青空文庫で初出した年と作品を特定する

## 概要

任意の単語が青空文庫で初出した年と作品を特定するプログラムです。
青空文庫の作品情報を一旦MongoDBに登録したうえで、テキストファイルの本文と作品情報を照らし合わせて特定します。
実行にはPyMongoとSudachiPyが必要です。
詳しくは[こちら](http://kawami.hatenablog.jp/entry/2018/02/16/175531)をご覧ください。

## 実行方法
config.ymlにMongoDBと青空文庫のディレクトリ・ファイルパス、結果書き出しファイルの情報を記述し、

> python analyze.py

を実行してください。
なお既に実行して書き出した結果ファイルはresult.csvです。

### config.ymlについて
mongoDB…MongoDBに関する情報を記述します。
* db_name…データベース名
* collection_name…コレクション名
aozora…青空文庫のデータのパスを記述します。
* directory…青空文庫のテキストファイルのパス
* list_person_all_extended…青空文庫の作家別作品一覧拡充版ファイルのパス
outputfile…結果を書き出すファイル