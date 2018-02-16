import re

# 青空文庫形式のファイルの冒頭にある説明部分の記号行
HYPHEN = "-------------------------------------------------------"


def get_title_and_author(file, encoding="shift_jisx0213"):
    """
    青空文庫形式のファイルから作品名と作者名を抽出するよ
    :param file:ファイルパス
    :param encoding:エンコード
    :return:作品名(副題含む)と作者名
    """
    with open(file=file, encoding=encoding) as f:
        lines = f.readlines()
        current_row = 1
        for line in lines:
            if line == "\n":
                break
            current_row += 1
        else:
            # 改行のみの行が存在しなかった場合
            print("青空文庫の形式じゃないな？")
            return
        title = re.sub("[\r\n]", "", lines[0])
        if current_row > 3:
            title = title + "\t" + re.sub("[\r\n]", "", lines[1])
            author = re.sub("[\r\n]", "", lines[2])
        else:
            author = re.sub("[\r\n]", "", lines[1])
        return title, author


def get_context(file, encoding="shift_jisx0213", use_trimming_ruby=True):
    """
    青空文庫形式ファイルから物語の本文を抽出するよ
    :param file: ファイルパス
    :param encoding: エンコード
    :param use_trimming_ruby: ルビを取り除くか(デフォルトは取り除く)
    :return: 本文のリスト
    """
    with open(file=file, encoding=encoding) as f:
        lines = f.readlines()
        is_context = False
        context_lines = []
        for i, line in enumerate(lines):
            # 本文の終了判定
            if line.startswith("底本："):
                break
            if line == "\n":
                continue
            if not is_context:
                if re.match(".*" + HYPHEN + ".*", line) and i > 10:
                    is_context = True
            elif use_trimming_ruby:
                context_lines += trim_ruby(line).split("。")
            else:
                context_lines += line.split("。")
        return context_lines


def trim_ruby(text):
    """
    ルビを取り除くよ
    :param text:
    :return:
    """
    return re.sub(pattern="[《［].+?[》］]", string=text, repl="")


if __name__ == '__main__':
    text = "宇宙《そら》よりも遠い場所"
    print(trim_ruby(text))
