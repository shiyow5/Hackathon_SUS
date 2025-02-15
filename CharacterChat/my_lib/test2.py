import google.generativeai as genai
import json

base_model = genai.get_base_model('models/gemini-1.5-flash-001-tuning')

import random

with open("giaccho-202502160103.json", "r", encoding="utf-8") as f:
    training_data = json.load(f)

def get_model(train_data):
    name = f'giaccho-{random.randint(0,10000)}'
    operation = genai.create_tuned_model(
        # チューニング済みのモデルも`source_model="tunedModels/..."`で指定可能。
        source_model=base_model.name,
        # training_data='path/to/training_data.csv',
        # training_data='path/to/training_data.json'でも可能
        training_data=train_data,
        id = name,
        epoch_count = 100,
        batch_size=int(len(train_data) * 0.3),
        learning_rate=0.001,
    )

    import time

    for status in operation.wait_bar():
        time.sleep(30)
        
get_model(training_data)