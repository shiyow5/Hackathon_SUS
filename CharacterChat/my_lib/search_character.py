#!/usr/bin/env python
# coding: utf-8

import os
import json
import requests
from datetime import datetime, timedelta, timezone

from bs4 import BeautifulSoup
from dotenv import load_dotenv, find_dotenv
import pandas as pd
from googleapiclient.discovery import build
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser


load_dotenv(find_dotenv())


class CharacterFeature:
    API_KEY = os.getenv("Google_API_Key")
    CSE_ID = os.getenv("Google_Custom_Search_Engine_Id")
    GEMINI_KEY = os.getenv("Gemini_API_Key")
    
    def __init__(self, name):
        self.character_name = name
        self.search_query = f"{name} セリフ一覧"
        
    def _search_by_google(self, query, start_index=1):
        # Google Custom Search API
        service = build("customsearch",
                        "v1",
                        cache_discovery=False,
                        developerKey=CharacterFeature.API_KEY)
        # CSEの検索結果を取得
        result = service.cse().list(q=query,
                                    cx=CharacterFeature.CSE_ID,
                                    num=10,
                                    start=start_index).execute()
        # 検索結果(JSON形式)
        return result
    
    def _get_page_content(self, url):
        """指定したURLのページ本文を取得"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # HTTPエラーなら例外を発生させる
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        # ページ本文の候補（サイトによって異なる）
        candidates = ["article", "main", "div.content", "div.entry-content", "div.post-body"]

        for candidate in candidates:
            content = soup.select_one(candidate)
            if content:
                return content.get_text(strip=True)

        return soup.get_text(strip=True)[:1000]  # 全文が取れなかった場合、最初の1000文字だけ取得
    
    def _extract_serifu_with_gemini(self, text):
        # Gemini モデルの準備
        llm = GoogleGenerativeAI(model="gemini-2.0-flash", api_key=CharacterFeature.GEMINI_KEY)
    
        # プロンプトを定義
        system_template = """
            以下のinputはwebページから抽出した{chara}に関する文章です。{chara}のセリフと思われる記述を取り出してください。
            出力は次の形式でJSONにしてください：
            [
                {{"id": "セリフのID", "serifu": "セリフの内容"}}
            ]
            input：
            """
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_template),
            ("user", "{text}")
        ])

        # 出力パーサーを作成
        parser = JsonOutputParser()
    
        chain = prompt_template | llm | parser
    
        input_data = {"chara": self.character_name, "text": text}
        response = chain.invoke(input_data)
    
        return response
    
    def get_search_results(self):
        # Google検索 - Custom Search API
        data = self._search_by_google(self.search_query)
        
        # Google検索結果から任意の項目抽出 & rank付与
        items = data["items"]

        result = []
        num_items = len(items) if len(items) < 10 else 10
        for i in range(num_items):
            title = items[i].get("title", "")  # .get() を使用してキーがない場合のデフォルト値を設定
            link = items[i].get("link", "")
            snippet = items[i].get("snippet", "")
            result.append([i + 1, title, link, snippet])
            
        # List -> DataFrame
        df_search_results = pd.DataFrame(result, columns=["rank", "title", "url", "snippet"])
        
        return df_search_results
    
    def get_serifu(self, targets=[0], save_search_result=False):
        search_results = self.get_search_results()
        
        if save_search_result:
            # ExecDate
            timezone_jst = timezone(timedelta(hours=+9), 'JST')
            now = datetime.now(timezone_jst)
            
            # CSV出力
            dt_csv = now.strftime('%Y%m%d%H%M')
            output_csv = f'{self.search_query}_{dt_csv}.csv'
            search_results.to_csv(output_csv,
                                     sep=",",
                                     index=False,
                                     header=True,
                                     encoding="utf-8")
            pd.read_csv(output_csv, index_col=0)
        
        serifu_datas = []
        for target in targets:
            searched_target_url = search_results["url"][target]
            page_content = self._get_page_content(searched_target_url)
            serifu_data = self._extract_serifu_with_gemini(page_content)
            serifu_datas += serifu_data
        
        return serifu_datas


def test_usecase():
    characte_name = "ずんだもん"
    cf = CharacterFeature(characte_name)
    
    serifu_data = cf.get_serifu()
    
    save_path = "/home/satosho/GoogleHackathon/Hackathon_SUS/test.json"
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(serifu_data, f, ensure_ascii=False, indent=2)
