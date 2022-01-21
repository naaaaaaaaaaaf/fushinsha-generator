from flask_apscheduler import APScheduler
from flask import Flask, request, redirect, url_for, abort, jsonify, render_template
from flask_cors import CORS # <-追加
import os
import configparser
import time
import threading
import pandas
import markovify
import requests
import getdata
import exportModel

# コンフィグの読み込み
config_ini = configparser.ConfigParser()
config_ini.read('config/config.ini', encoding='utf-8')
elements = ['serihu', 'joukyou']

app = Flask(__name__)
CORS(app)

def genModel(elements):
    date_index = pandas.date_range(start="2018-01", end="2022-01", freq="M").to_series().dt.strftime("%Y%m")
    for i in elements:
        path = 'chainfiles/' + i + '.json'
        size = 2 if i == 'iti' else 3
        list = getdata.getData(i, date_index)
        exportModel.generateAndExport(list, path, size)


def genText(elements):
    result = []
    for i in elements:
        path = 'chainfiles/' + i + '.json'
        with open(path) as f:
            textModel = markovify.Text.from_json(f.read())
            sentence = textModel.make_sentence(tries=500)
            if i == 'serihu':
                sentence = '「' + sentence + '」'
            result.append(sentence)
    return result

def worker():
    # モデルの作成について
    print("開始します…")
    if (os.path.isfile('chainfiles/serihu.json')):
        print("モデルは再生成されません")
    else:
        genModel(elements)
    domain = config_ini['read']['domain']
    write_access_token = config_ini['write']['access_token']
    result = genText(elements)
    sentence = result[0] + '\n' + result[1]
    sentence = sentence.replace(' ', '') + ' #bot'
    try:
        post_toot(domain, write_access_token, {"status": sentence})
        print("投稿しました。 内容: " + sentence)
    except Exception as e:
        print("投稿エラー: {}".format(e))

@app.route('/api/genText', methods=["GET"])
def api_genText():
    result = genText(elements)
    sentence = result[0] + '\n' + result[1]
    sentence = sentence.replace(' ', '')
    return jsonify({"message": sentence}), 200


if __name__ == "__main__":
    app.run(use_reloader=False,host = "0.0.0.0")
