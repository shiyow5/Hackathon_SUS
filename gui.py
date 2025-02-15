import streamlit as st
import time
import threading

# キャラクター情報のリスト [0]は表示名
char_data = [
    {"char_name": "ずんだもん", "model_name": "zundamon"},
    {"char_name": "どらえもん"}
]


# サイドバーのメニューセクション
st.sidebar.write("### Main Menu")
menu_selected = st.sidebar.radio("Select an option", ["Search & Learning", "Characters"])

# キャラクターセクションを表示（"characters" が選択された場合）
page_selected = None
if menu_selected == "Characters":
    st.sidebar.markdown("---")  # 区切り線
    st.sidebar.write("### Choose a Character")
    page_selected = st.sidebar.radio("", [p["char_name"] for p in char_data])


data = [
    {"text": "Google", "url": "https://www.google.com"},
    {"text": "YouTube", "url": "https://www.youtube.com"},
    {"text": "GitHub", "url": "https://github.com"},
    {"text": "OpenAI", "url": "https://openai.com"},
    {"text": "Streamlit", "url": "https://streamlit.io"},
]
def menu():
    if "input" not in st.session_state:
        st.session_state.input = False
    if "search" not in st.session_state:
        st.session_state.search = False

    if user_input := st.text_input("Enter you need char", placeholder="ずんだもん"):
        st.session_state.input = True
    if st.button("Search"):
        st.session_state.search = True

        # if user_input is not invalid:
        #     data = serch_function(user_input)
        st.write(user_input) # 消して

    if st.session_state.input:
        checkbox(data)

def checkbox(data):
    # チェックボックスの状態を保存する辞書
    if "checked" not in st.session_state:
        st.session_state.checked = {item["text"]: False for item in data}
    if "running" not in st.session_state:
        st.session_state.running = False

    # 表の作成
    st.write("#### Which article is appropriate for the character you want")
    for item in data:
        cols = st.columns([4, 1])  # 4:1 の比率で分割
        with cols[0]:  # 左側（リンク）
            st.markdown(f'<a href="{item["url"]}" target="_blank">{item["text"]}</a>', unsafe_allow_html=True)
        with cols[1]:  # 右側（チェックボックス）
            st.session_state.checked[item["text"]] = st.checkbox("", value=st.session_state.checked[item["text"]], key=item["text"])
    selected_links = [item["url"] for item in data if st.session_state.checked[item["text"]]]
    if selected_links:
        if st.button("Start learning!"):
            thread = threading.Thread(target=function, args=()) # funciton(selected_links)
            thread.start()
            time.sleep(5)
    else:
        st.button("Start learning!", disabled=True)
    
    if st.session_state.running:
        with st.spinner("Please wait...", show_time=True):
            while st.session_state["running"]:
                time.sleep(0.1)
    


def function():
    st.session_state.running = True
    time.sleep(500)
    st.session_state.running = False


def chat(name = "ずんだもん", model_name = None):
    # セッションステートを初期化
    if "messages" not in st.session_state or st.button("Reset", type="primary"):
        st.session_state.messages = [{"role": "assistant", "content": f"My name is {name}."}]
    
    # メッセージ履歴を表示
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
        st.session_state.messages.append({"role": "assistant", "content": response})
        # チャットメッセージとして表示
        with st.chat_message("assistant"):
            st.markdown(response)



# ページの処理
if menu_selected == "Search & Learning":
    # st.session_state.input = False
    menu()
elif page_selected:
    chat(page_selected)