#!/usr/bin/env python
# coding: utf-8

import time
import json
from datetime import datetime, timedelta, timezone
import pykakasi
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
import google.auth

from my_lib.search_character import CharacterFeature


class CharacterTuning:
    def __init__(self, character_name, model_name):
        cf = CharacterFeature(character_name)
        self.character_feature = cf.get_feature()
        
        credentials, _ = google.auth.default()
        genai.configure(credentials=credentials)
        
        self.character_name = character_name
        self.model_name = model_name
        self.simple_llm = genai.GenerativeModel("gemini-2.0-flash")
        
    def _convert_serifu2standard_with_gemini(self, text, max_retries=10):
        for attempt in range(max_retries):
            try:
                response = self.simple_llm.generate_content(f"次の文章の特徴的な語尾や言い回しなどを適切に処理し、標準的な言葉遣いに直してください。出力は結果の文章のみにして下さい。:\n{text}")
                return response.text
            except ResourceExhausted:
                if attempt < max_retries - 1:
                    print(f"Quota exceeded. Retrying in {2**attempt} seconds...")
                    time.sleep(2**attempt)  # Exponential backoff
                else:
                    print("Quota exceeded. Please check API limits.")
                    return None
    
    def convert_serifu2train(self, serifu_data, save=True):
        train_data = []
        for serifu in serifu_data:
            output = serifu.get("serifu")
            if output:
                text_input = self._convert_serifu2standard_with_gemini(output)
                if text_input:
                    train_data.append({'text_input': text_input, 'output': output})
        
        if save:
            with open(f"datas/for_fine_tuning/{self.model_name}.json", "w", encoding="utf-8") as f:
                json.dump(train_data, f, ensure_ascii=False, indent=2)
        
        return train_data
        
    def get_model(self, train_data=None, debug=False):
        if train_data:
            batch_size = int(len(train_data) * 0.3)
            base_model = genai.get_base_model('models/gemini-1.5-flash-001-tuning')
            operation = genai.create_tuned_model(
                source_model = base_model.name,
                training_data = train_data,
                id = self.model_name,
                epoch_count = 100,
                batch_size = batch_size if batch_size < 64 else 64,
                learning_rate = 0.001,
            )
            if debug:
                for status in operation.wait_bar():
                    time.sleep(30)
            
        else:
            operation = genai.get_operation(self.model_name)
        
        return operation.result()
    
    def delete_model(self):
        genai.delete_tuned_model(f'tunedModels/{self.model_name}')
    
    def plot_logloss(self):
        model = genai.GenerativeModel(model_name=f'tunedModels/{self.model_name}')
        snapshots = pd.DataFrame(model.tuning_task.snapshots)
        sns.lineplot(data=snapshots, x = 'epoch', y='mean_loss')
        plt.show()
        
    def invoke(self, text):
        query = f"""あなたは{self.character_name}です。{self.character_name}になりきって会話してください。
                {self.character_name}の特徴は以下の通りです。：{self.character_feature}
                以下の内容に答えてください。：{text}
            """
        response = self.simple_llm.generate_content(query)
        
        try:
            model = genai.GenerativeModel(model_name=f'tunedModels/{self.model_name}')
            result = model.generate_content(response.text)
            return result.text
        
        except ValueError as e:
            print(f"ポリシー違反の可能性あり-> {e}")
            result = response
        
        return result.text
    
    
def get_train_state():
    for o in genai.list_operations():
        if not o.done():
            return -1
    return 0


def to_roman_alphabet(text):
    kakasi = pykakasi.kakasi()
    kakasi.setMode("H", "a")  # Hiragana to ascii
    kakasi.setMode("K", "a")  # Katakana to ascii
    kakasi.setMode("J", "a")  # Japanese(kanji) to ascii
    kakasi.setMode("r", "Hepburn")  # Use Hepburn romanization
    
    conv = kakasi.getConverter()
    romaji = conv.do(text)
    
    return romaji


def save_serifu_data(character_name, targets=[0]):
    cf = CharacterFeature(character_name)    
    serifu_data = cf.get_serifu(targets=targets)
    
    timezone_jst = timezone(timedelta(hours=+9), 'JST')
    now = datetime.now(timezone_jst)
    time_tag = now.strftime('%Y%m%d%H%M')
    
    model_name=f"{to_roman_alphabet(character_name)}-{time_tag}"
    ct = CharacterTuning(character_name, model_name)

    ct.convert_serifu2train(serifu_data)
    
    return model_name


def create_model(character_name, model_name, serifu_filename):
    ct = CharacterTuning(character_name, model_name)
    
    with open(f"datas/for_fine_tuning/{serifu_filename}", "r", encoding="utf-8") as f:
        training_data = json.load(f)
    
    with open("datas/model_datas.json", "r", encoding="utf-8") as f:
        models = json.load(f)
    models.append({"char_name": character_name, "model_name": model_name})
    
    with open("datas/model_datas.json", "w", encoding="utf-8") as f:
        json.dump(models, f, ensure_ascii=False, indent=2)

    ct.get_model(training_data)


def test_usecase1():
    chara_name = "ずんだもん"
    save_serifu_data(chara_name)
    

def test_usecase2():
    chara_name = "ずんだもん"
    model_name = "zundamon-special"
    serifu_filename = "zundamon-special.json"
    create_model(chara_name, model_name, serifu_filename)
