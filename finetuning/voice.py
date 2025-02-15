import requests
from pydub import AudioSegment
from io import BytesIO
import simpleaudio as sa

# APIリクエストの設定
url = "https://api.su-shiki.com/v2/voicevox/audio/"
params = {
    "text": "こんにちは。ずんだもんなのだ。もちもちずんだ。",  # ここに発音させたいテキストを入れてください
    "key": "w-7-3-w5y28861Q",
    "speaker": 1
}

# POSTリクエストを送信して音声データを取得
response = requests.post(url, params=params)

if response.status_code == 200:
    # 音声データを再生可能な形式に変換
    audio_data = BytesIO(response.content)
    audio = AudioSegment.from_wav(audio_data)

    # 音声を再生
    playback = sa.play_buffer(audio.raw_data, num_channels=audio.channels, bytes_per_sample=audio.sample_width, sample_rate=audio.frame_rate)
    playback.wait_done()
else:
    print("音声データの取得に失敗しました。")
