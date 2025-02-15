import streamlit as st
import time


# [0]は表示名
char_data = [
    {"char_name": "ずんだもん", "model_name": "zundamon"},
    {"char_name": "どらえもん"}
]


def page_output():
    # サイドバーのメニューセクション
    st.sidebar.write("### Main Menu")
    menu_selected = st.sidebar.radio("Select an option", ["Search & Learning", "Characters"])

    # キャラクターセクションを表示（"characters" が選択された場合）
    page_selected = None
    if menu_selected == "Characters":
        st.sidebar.markdown("---")  # 区切り線
        st.sidebar.write("### Choose a Character")
        page_selected = st.sidebar.radio("", [p["char_name"] for p in char_data])

    if menu_selected == "Search & Learning":
        # st.session_state.input = False
        menu()
    elif page_selected:
        chat(page_selected)


if "input" not in st.session_state:
    st.session_state.input = ""
if "search" not in st.session_state:
    st.session_state.search = False
if "data" not in st.session_state:
    st.session_state.data = []
if "checked" not in st.session_state:
    st.session_state.checked = {}


def serch_function(user_input = None): # ダミー
    data = [
        {"text": "Google", "url": "https://www.google.com"},
        {"text": "YouTube", "url": "https://www.youtube.com"},
        {"text": "GitHub", "url": "https://github.com"},
        {"text": "OpenAI", "url": "https://openai.com"},
        {"text": "Streamlit", "url": "https://streamlit.io"},
    ]
    return data



def menu():
    user_input = st.text_input("Enter you need char", value=st.session_state.input, placeholder="ずんだもん")
    st.session_state.input = user_input
    if st.button("Search") and user_input:
        st.session_state.search = True
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

if __name__ == "__main__":
    page_output()