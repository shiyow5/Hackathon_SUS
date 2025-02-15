import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import google.generativeai as genai

from search_character import CharacterFeature

import google.auth
credentials, _ = google.auth.default()
genai.configure(credentials=credentials)

def convert_serifu2train(characte_name, serifu_data):
    train_data = []
    for serifu in serifu_data:
        text_input = f"あなたは{characte_name}です。{characte_name}になりきって会話してください。"
        output = serifu.get("serifu")
        if output:
            train_data.append({'text_input': text_input, 'output': output})
        
    return train_data


def get_model(model_name, train_data=None):
    if train_data:
        base_model = genai.get_base_model('models/gemini-1.5-flash-001-tuning')
        operation = genai.create_tuned_model(
            source_model = base_model.name,
            training_data = train_data,
            id = model_name,
            epoch_count = 100,
            batch_size = 1,
            learning_rate = 0.001,
        )
    
        for status in operation.wait_bar():
            time.sleep(30)
            
    else:
        operation = genai.get_operation(model_name)
        
    return operation.result()


def delete_model(model_name):
    genai.delete_tuned_model(f'tunedModels/{model_name}')
    

def plot_logloss(operation_name):
    model = genai.get_operation(operation_name).result()
    snapshots = pd.DataFrame(model.tuning_task.snapshots)
    sns.lineplot(data=snapshots, x = 'epoch', y='mean_loss')
    plt.show()

    
def invoke(model_name, text):
    model1 = genai.GenerativeModel("gemini-2.0-flash")
    response = model1.generate_content(text)
        
    model2 = genai.GenerativeModel(model_name=f'tunedModels/{model_name}')
    result = model2.generate_content(response.text)
        
    return result.text


# すべてのチューニングを取得
for o in genai.list_operations():
    print(o.name, o.done())

#plot_logloss("tunedModels/giaccho-2853/operations/xfev5862vk6b")
#delete_model("giaccho-202502160124")

#print(invoke("zundamon-202502160245", "好きな食べ物は何？"))

"""characte_name = "ジョジョ ギアッチョ"
cf = CharacterFeature(characte_name)    
serifu_data = cf.get_serifu()

from datetime import datetime, timedelta, timezone

timezone_jst = timezone(timedelta(hours=+9), 'JST')
now = datetime.now(timezone_jst)
time_tag = now.strftime('%Y%m%d%H%M')

model_name=f"giaccho-{time_tag}"
train_data = convert_serifu2train(characte_name, serifu_data)
print(train_data)
get_model(model_name=model_name, train_data=train_data)"""


"""text_input = f"あなたは{characte_name}です。{characte_name}になりきって会話してください。: "
text_input += "酸性雨について教えて。"
result = invoke(model_name, text_input)

print(result)"""