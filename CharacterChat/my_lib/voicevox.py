import os
import requests
from pydub import AudioSegment
from io import BytesIO
import simpleaudio as sa
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


class VoiceVox:
    def __init__(self):
        self.url = "https://api.su-shiki.com/v2/voicevox/audio/"
        self.key = os.getenv("VOICEVOX_API_KEY")
        self.speaker = 1
        
    def speak(self, text):
        params = {
            "text": text,
            "key": self.key,
            "speaker": self.speaker
        }
        
        # POSTリクエストを送信して音声データを取得
        response = requests.post(self.url, params=params)
        
        if response.status_code == 200:
            # 音声データを再生可能な形式に変換
            audio_data = BytesIO(response.content)
            audio = AudioSegment.from_wav(audio_data)

            # 音声を再生
            playback = sa.play_buffer(audio.raw_data, num_channels=audio.channels, bytes_per_sample=audio.sample_width, sample_rate=audio.frame_rate)
            playback.wait_done()
        else:
            print("音声データの取得に失敗しました。")
