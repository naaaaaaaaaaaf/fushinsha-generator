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
elements = ['serihu', 'joukyou', 'iti']

app = Flask(__name__)
CORS(app)
class Config(object):
    JOBS = [
        {
            'id': 'job1',
            'func': 'app:worker',
            'trigger': 'interval',
            'seconds': 60
        }
    ]

    SCHEDULER_API_ENABLED = True

def genModel(elements):
    date_index = pandas.date_range(start="2018-01", end="2021-01", freq="M").to_series().dt.strftime("%Y%m")
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


def post_toot(domain, access_token, params):
    headers = {'Authorization': 'Bearer {}'.format(access_token)}
    url = "https://{}/api/v1/statuses".format(domain)
    response = requests.post(url, headers=headers, json=params)
    if response.status_code != 200:
        raise Exception('リクエストに失敗しました。')
    return response

def worker():
    # モデルの作成について
    print("開始します…")
    if (os.path.isfile('chainfiles/iti.json')):
        print("モデルは再生成されません")
    else:
        genModel(elements)
    domain = config_ini['read']['domain']
    write_access_token = config_ini['write']['access_token']
    result = genText(elements)
    sentence = result[0] + '\n' + result[1] + '\n【' + result[2] + '】にて'
    sentence = sentence.replace(' ', '') + ' #bot'
    try:
        post_toot(domain, write_access_token, {"status": sentence})
        print("投稿しました。 内容: " + sentence)
    except Exception as e:
        print("投稿エラー: {}".format(e))

@app.route('/api/genText', methods=["GET"])
def api_genText():
    result = genText(elements)
    sentence = result[0] + '\n' + result[1] + '\n【' + result[2] + '】にて'
    sentence = sentence.replace(' ', '')
    return jsonify({"message": sentence}), 200


if __name__ == "__main__":
    # 定期実行部分
    app.config.from_object(Config())

    scheduler = APScheduler()
    # scheduler.api_enabled = True
    scheduler.init_app(app)
    scheduler.start()
    app.run(use_reloader=False,debug=True)
