## 前処理
### ライブラリのインポート
import streamlit as st
import requests
import json
import numpy as np

### ユーザー情報ファイルの取得
with open("secret.json") as f:
    secret = json.load(f)

### ユーザー情報の設定
bearer_token = secret["BEARER_TOKEN"]
search_url = secret["SEARCH_URL"]
base_url = secret["BASE_URL"]
client_id = secret["CLIENT_ID"]
client_secret = secret["CLIENT_SECRET"]

## 処理の定義
### Twitter の Bearer OAuth 認証
def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

### 検索ツイートの取得
def connect_to_endpoint(url, params):
    response = requests.get(url, auth=bearer_oauth, params=params)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

### COTOHA APIアクセストークン取得
def get_cotoha_acces_token():

    token_url = "https://api.ce-cotoha.com/v1/oauth/accesstokens"

    headers = {
        "Content-Type": "application/json",
        "charset": "UTF-8"
    }

    data = {
        "grantType": "client_credentials",
        "clientId": client_id,
        "clientSecret": client_secret
    }

    response = requests.post(token_url,
                        headers=headers,
                        data=json.dumps(data))

    access_token = response.json()["access_token"]

    return access_token

### 感情分析データ取得
def cotoha_sentiment_analyze(access_token, sentence):
    headers = {
        "Content-Type": "application/json",
        "charset": "UTF-8",
        "Authorization": "Bearer {}".format(access_token)
    }
    data = {
        "sentence": sentence,
    }
    response = requests.post(base_url + "nlp/v1/sentiment",
                      headers=headers,
                      data=json.dumps(data))
    return response.json()

## 処理の実行
### タイトルの表示
st.title("検索語句を含むツイートの感情分析")

### 検索語句の取得
input_data = st.text_input("検索語句を入力してください")
"検索語句：", input_data

if st.button("検索実行"):
    if len(input_data) > 0:
        ### クエリ パラメータの設定
        query_params = {
            "query": input_data + " -is:retweet",
            "max_results": 20,
            "tweet.fields": "author_id",
        }
        
        ### ツイート取得
        json_response = connect_to_endpoint(search_url, query_params)
        
        ### 感情分析用変数の設定
        senti_res = []
        accses_token = get_cotoha_acces_token()
        posi_nega = np.zeros(3)
        score_total = 0.0
        emo_phrase = []
        err_flg = False
        err_msg = ""
        
        ### 感情分析データ取得
        for i in json_response["data"]:
            senti_res.append(cotoha_sentiment_analyze(accses_token, i["text"]))
        
        ### データの整形
        for j in senti_res:
            if j["status"] == 0:
                if j["result"]["sentiment"] == "Positive":
                    posi_nega[0] += 1
                elif j["result"]["sentiment"] == "Negative":
                    posi_nega[2] += 1
                else:
                    posi_nega[1] += 1
                score_total += j["result"]["score"]
                if len(j["result"]["emotional_phrase"]) > 0:
                    for k in j["result"]["emotional_phrase"]:
                        emo_phrase.append(k["form"])
            else:
                err_flg = True
                err_msg = j["message"]
        
        max_cnt = posi_nega.sum()
        rate = posi_nega / posi_nega.sum(keepdims=True) * 100
        st.write("ポジティブ：", posi_nega[0], "(", rate[0], "%) 普通：", posi_nega[1], "(", rate[1], "%)　ネガティブ：",  posi_nega[2], "(", rate[2], "%)")
        st.write("データ件数：", max_cnt)
        st.write("評価スコア：", score_total / max_cnt)
        st.write("感情ワード")
        st.write(" ".join(emo_phrase))
        
        if err_flg:
            st.error(err_msg)
    else:
        st.error("検索語句がありません")
