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
# 3. 输入框交互
user_input = st.text_input("📝 请输入中文单词或成语：", placeholder="例如：名落孙山")

if user_input:
    with st.spinner('正在为您生成精美教案及例句语音...'):
        try:
            # 专家指令
            prompt = f"""
            你是一位精通中日双语的教育专家。请针对 '{user_input}' 联想一个N5-N4日语单词并生成3个例句。
            必须严格按JSON格式输出：
            {{
                "word": "单词",
                "reading": "假名",
                "pitch": "音调核",
                "pronunciation_tip": "建议",
                "sentences": ["例句1", "例句2", "例句3"]
            }}
            """
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(completion.choices[0].message.content)
            
            # --- 展现单词与主发音 ---
            st.success(f"✨ 联想成功：{result['word']}")
            col_w1, col_w2 = st.columns([3, 1])
            with col_w1:
                st.metric("单词/假名", f"{result['word']} ({result['reading']})")
                st.write(f"音调核：{result['pitch']}")
            with col_w2:
                st.write("📢 单词发音")
                st.audio(get_audio(result['word']), format='audio/mp3')

            st.info(f"💡 发音秘籍：{result['pronunciation_tip']}")
            st.divider()
            
            # --- 重点：例句 + 右侧声音按钮 ---
            st.subheader("📖 基础例句练习")
            for idx, sent in enumerate(result['sentences'], 1):
                # 创建两列：左边占 75% 放文字，右边占 25% 放播放条
                c1, c2 = st.columns([0.75, 0.25])
                with c1:
                    st.write(f"{idx}. {sent}")
                with c2:
                    # 为每一个例句实时生成对应的语音条
                    st.audio(get_audio(sent), format='audio/mp3')

        except Exception as e:
            st.error(f"❌ 运行出错：{str(e)}")
