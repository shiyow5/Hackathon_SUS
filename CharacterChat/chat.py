from langchain_core.language_models import LLM
from langchain_core.messages import HumanMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import SQLChatMessageHistory
from pydantic import Field
from sqlalchemy import create_engine

from .my_lib.fine_tuning import CharacterTuning


class CustomGoogleGenerativeAI(LLM):
    model_name: str = Field(default="giaccho-202502160142", alias="model")
    
    @property
    def _llm_type(self) -> str:
        """LangChain に必要な LLM の種類を指定"""
        return "google_generative_ai"

    def _call(self, prompt: str, **kwargs) -> str:
        model = CharacterTuning(characte_name=None, model_name=self.model_name)
        response = model.invoke(prompt)
        return response

model = CustomGoogleGenerativeAI(model_name="giaccho-202502160142")

# セッションIDに基づいて履歴を取得する関数を定義
def get_session_history(session_id):
    engine = create_engine("sqlite:///datas/chat_history/memory.db")
    history = SQLChatMessageHistory(session_id, connection=engine)
    print(f"DEBUG: Retrieved history for session {session_id}: {history}")
    return history

# メッセージ履歴を持つチャットボットを作成
with_message_history = RunnableWithMessageHistory(
    model,
    get_session_history,
)

# コンフィグを設定し、チャットボットにメッセージを送信
response = with_message_history.invoke(
    HumanMessage(content="私の名前は？"),
    config={"configurable": {"session_id": "1"}},
)

print(response)