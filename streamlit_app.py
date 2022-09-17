## 前処理
### ライブラリのインポート
import streamlit as st
import requests
import json

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
input_data = None
input_data = st.text_input("検索語句を入力してください")

if input_data is not None:
    "検索語句：", input_data
    
    if st.button("検索実行"):
        "実行しました。"
