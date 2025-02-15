import streamlit as st
import time
from collections import OrderedDict


# [0]は表示名
char_data = [
    {"char_name": "ずんだもん", "model_name": "zundamon1"},
    {"char_name": "どらえもん", "model_name": "doraemon"},
    {"char_name": "ずんだもん", "model_name": "zundamon2"}
]


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


def serch_function(user_input = None): # ダミー
    data = [
        {"text": "Google", "url": "https://www.google.com"},
        {"text": "YouTube", "url": "https://www.youtube.com"},
        {"text": "GitHub", "url": "https://github.com"},
        {"text": "OpenAI", "url": "https://openai.com"},
        {"text": "Streamlit", "url": "https://streamlit.io"},
    ]
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
        st.write(user_input) # 消して
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
    
    selected_links = [item["url"] for item in data if st.session_state.checked[item["text"]]]

    if st.button("Start learning!", disabled=bool(not selected_links)):
        with st.spinner("Wait for it..."):
            time.sleep(3)
        success = -1 # start_train(selected_links)
        if success == -1:
            st.error("Currently, training another character.")
        else:
            st.success("Please wait for it to appear in the Character section.")


def chat(name = "ずんだもん", model_name = "zundamon1"):
    left, _, right = st.columns(3)
    if left.button("Reset", type="primary") or "messages" not in st.session_state:
        st.session_state.messages = []
    else:
        st.session_state.messages = get_message(model_name)

    if model_name != "zundamon1":
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
        response = f"Echo: {prompt}"

        # AIのメッセージを履歴に追加

        # チャットメッセージとして表示
        with st.chat_message("assistant"):
            st.markdown(response)

@st.dialog("本当に削除しますか？")
def delete(model):
    if st.button("YES. Delete.", type="primary"):
        pass # delete(model)
        st.rerun()

if __name__ == "__main__":
    page_output()