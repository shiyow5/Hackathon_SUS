import streamlit as st
import time
import json
import pandas as pd
from collections import OrderedDict

from CharacterChat.my_lib.search_character import CharacterFeature
from CharacterChat.my_lib.fine_tuning import CharacterTuning
from CharacterChat.my_lib.fine_tuning import save_serifu_data
from CharacterChat.my_lib.fine_tuning import create_model
import CharacterChat.my_lib.sql as sql


# [0]は表示名
with open("datas/model_datas.json", "r", encoding="utf-8") as f:
    char_data = json.load(f)


def page_output():
    # サイドバーのメニューセクション
    st.sidebar.write("# Main Menu")
    menu_selected = st.sidebar.radio("Select an option", ["Search & Learning", "Characters"])

    # キャラクターセクションを表示（"Characters" が選択された場合）
    if menu_selected == "Characters":
        st.sidebar.markdown("---")  # 区切り線
        st.sidebar.write("### Choose a Character")
        char_names = list(OrderedDict((p["char_name"], None) for p in char_data).keys())
        selected_char = st.sidebar.radio(f"If the search names are the same,choose a version.", char_names)
        matching_models = [p["model_name"] for p in char_data if p["char_name"] == selected_char]
        selected_model = st.sidebar.radio("choose version of the model", matching_models) if len(matching_models) > 1 else matching_models[0]

    if menu_selected == "Search & Learning":
        menu()
    elif selected_char:
        chat(selected_char, selected_model)


if "input" not in st.session_state:
    st.session_state.input = ""
if "data" not in st.session_state:
    st.session_state.data = []
if "checked" not in st.session_state:
    st.session_state.checked = {}
if "name" not in st.session_state:
    st.session_state.name = ""


def serch_function(user_input = None):
    cf = CharacterFeature(user_input)
    result = cf.get_search_results()
    
    data = []
    for title, url in zip(result["title"], result["url"]):
        data.append({"text": title, "url": url})
    
    return data


def get_message(model_name):
    message1 = [{"role": "user", "content": "こんにちは"},
               {"role": "assistant", "content": "はい、こんにちはなのだ"}]
    if model_name == "zundamon1":
        return message1
    return  []


def menu():
    user_input = st.text_input("Enter you need char", value=st.session_state.input, placeholder="ずんだもん")
    st.session_state.input = user_input
    if st.button("Search") and user_input:
        st.session_state.data = serch_function(user_input)
    if st.session_state.data and st.session_state.input:
        checkbox(st.session_state.data)


def checkbox(data):
    # 表の作成
    st.write("#### Which article is appropriate for the character you want")
    for item in data:
        cols = st.columns([4, 1])  # 4:1 の比率で分割
        with cols[0]:  # 左側（リンク）
            st.markdown(f'<a href="{item["url"]}" target="_blank">{item["text"]}</a>', unsafe_allow_html=True)
        with cols[1]:  # 右側（チェックボックス）
            if item["text"] not in st.session_state.checked:
                st.session_state.checked[item["text"]] = False
            st.session_state.checked[item["text"]] = st.checkbox("", value=st.session_state.checked[item["text"]], key=item["text"])
    
    selected_links = []
    for id, item in enumerate(data):
        if st.session_state.checked[item["text"]]:
            selected_links.append(id)

    if st.button("Start learning!", disabled=bool(not selected_links)):
        with st.spinner("Wait for it..."):
            time.sleep(3)
        st.success("Please wait for it to appear in the Character section.")
        model_name = save_serifu_data(characte_name=st.session_state.input, targets=selected_links)
        create_model(characte_name=st.session_state.input, model_name=model_name, serifu_filename=f"{model_name}.json")


def chat(name = "ずんだもん", model_name = "zundamon1"):
    left, _, right = st.columns(3)
    if left.button("Reset", type="primary") or "messages" not in st.session_state:
        st.session_state.messages = []
    else:
        st.session_state.messages = sql.get_messages(model_name)

    if model_name != "zundamon-202502160245":
        if right.button("delete this model"):
            delete(model_name)

    # メッセージ履歴を表示
    st.info(f"現在のキャラ： {name}")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ユーザーからの入力を受け取る
    if prompt := st.chat_input("What is up?", key="chat_input"):
        # ユーザーのメッセージを履歴に追加
        st.session_state.messages.append({"role": "user", "content": prompt})
        # チャットメッセージとして表示
        with st.chat_message("user"):
            st.markdown(prompt)

        # AIからの応答を生成 (ここでは例としてユーザーの入力をそのまま返す)
        cf = CharacterTuning(characte_name=name, model_name=model_name)
        response = cf.invoke(prompt)

        # AIのメッセージを履歴に追加
        st.session_state.messages.append({"role": "asistant", "content": response})
        sql.save_messages(model_name, st.session_state.messages)
        # チャットメッセージとして表示
        with st.chat_message("assistant"):
            st.markdown(response)

@st.dialog("本当に削除しますか？")
def delete(model):
    if st.button("YES. Delete.", type="primary"):
        ct = CharacterTuning(characte_name="", model_name=model)
        ct.delete_model()
        with open("datas/model_datas.json", "r", encoding="utf-8") as f:
            model_datas = json.load(f)
        for model_data in model_datas:
            if model_data["model_name"]==model:
                model_datas.remove(model_data)
        with open("datas/model_datas.json", "w", encoding="utf-8") as f:
            json.dump(model_datas, f, ensure_ascii=False, indent=2)
        st.rerun()

if __name__ == "__main__":
    page_output()