import streamlit as st
from groq import Groq
import json
from gtts import gTTS
import io

# 1. 核心配置
API_KEY = "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"
client = Groq(api_key=API_KEY)

# 封装发音函数：将文字转为音频流
def get_audio(text):
    tts = gTTS(text=text, lang='ja')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp

# 2. 页面美化设置
st.set_page_config(page_title="AI日语联想学习", layout="centered")
st.title("JP 日本語学習 - 智能联想系统 2.1")
st.caption("基于 Llama-3.3 驱动 + 全环境交互语音")
