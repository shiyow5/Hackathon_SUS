import google.generativeai as genai

base_model = genai.get_base_model('models/gemini-1.5-flash-001-tuning')

import random

name = f'generate-num-{random.randint(0,10000)}'
operation = genai.create_tuned_model(
    # チューニング済みのモデルもsource_model="tunedModels/..."で指定可能。
    source_model=base_model.name,
    # training_data='path/to/training_data.csv',
    # training_data='path/to/training_data.json'でも可能
    training_data=[
        {
             'text_input': '1',
             'output': '2',
        },{
             'text_input': '3',
             'output': '4',
        },{
             'text_input': '-3',
             'output': '-2',
        },{
             'text_input': 'twenty two',
             'output': 'twenty three',
        },{
             'text_input': 'two hundred',
             'output': 'two hundred one',
        },{
             'text_input': 'ninety nine',
             'output': 'one hundred',
        },{
             'text_input': '8',
             'output': '9',
        },{
             'text_input': '-98',
             'output': '-97',
        },{
             'text_input': '1,000',
             'output': '1,001',
        },{
             'text_input': '10,100,000',
             'output': '10,100,001',
        },{
             'text_input': 'thirteen',
             'output': 'fourteen',
        },{
             'text_input': 'eighty',
             'output': 'eighty one',
        },{
             'text_input': 'one',
             'output': 'two',
        },{
             'text_input': 'three',
             'output': 'four',
        },{
             'text_input': 'seven',
             'output': 'eight',
        }
    ],
    id = name,
    epoch_count = 100,
    batch_size=4,
    learning_rate=0.001,
)

import time

for status in operation.wait_bar():
  time.sleep(30)
