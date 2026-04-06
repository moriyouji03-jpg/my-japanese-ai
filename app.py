import streamlit as st
from groq import Groq
import json
from gtts import gTTS
import io

# 1. 配置
API_KEY = "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"
client = Groq(api_key=API_KEY)

# 初始化 Session State，用于记录当前哪一行在发音
if "playing_id" not in st.session_state:
    st.session_state.playing_id = None
if "last_result" not in st.session_state:
    st.session_state.last_result = None

def get_audio(text):
    if not text: return None
    try:
        tts = gTTS(text=text, lang='ja')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp
    except: return None
        # 2. 页面设置
st.set_page_config(page_title="AI日语联想学习", layout="centered")
st.title("JP 日本語学習 - 智能联想系统 3.0")
st.caption("排他性语音控制版 - 一次只说一句话")

user_input = st.text_input("📝 请输入中文单词或成语：", placeholder="例如：名落孙山")

# 当输入变化时，重置播放状态
if user_input and (not st.session_state.last_result or st.session_state.last_result['input'] != user_input):
    with st.spinner('专家正在构思...'):
        prompt = f"针对 '{user_input}' 联想一个标准日语词并给3个例句。只输出JSON: {{'word':'','reading':'','pitch':'','tip':'','sentences':['','','']}}"
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        res_data = json.loads(completion.choices[0].message.content)
        res_data['input'] = user_input
        st.session_state.last_result = res_data
        st.session_state.playing_id = None # 换词时停止所有声音
# 3. 展现逻辑
if st.session_state.last_result:
    res = st.session_state.last_result
    st.success(f"✨ 专家联想成功")
    
    # 单词部分
    c_w1, c_w2 = st.columns([3, 1])
    with c_w1:
        st.header(f"{res.get('word')} ({res.get('reading')})")
        st.write(f"**音调核：** {res.get('pitch')}")
    with c_w2:
        if st.button("🔊 单词发音", key="btn_word"):
            st.session_state.playing_id = "word"
        if st.session_state.playing_id == "word":
            st.audio(get_audio(res.get('word')), format='audio/mp3', autoplay=True)

    st.info(f"💡 专家建议：{res.get('pronunciation_tip', '注意发音')}")
    st.divider()
    
    # 例句部分
    st.subheader("📖 专家级例句练习")
    for idx, s in enumerate(res.get('sentences', []), 1):
        col_a, col_b = st.columns([0.75, 0.25])
        with col_a:
            st.write(f"**{idx}.** {s}")
        with col_b:
            # 使用按钮触发播放
            if st.button(f"播放例句 {idx}", key=f"btn_{idx}"):
                st.session_state.playing_id = f"sent_{idx}"
            
            # 核心排他逻辑：只有 ID 匹配时才渲染播放器并自动播放
            if st.session_state.playing_id == f"sent_{idx}":
                st.audio(get_audio(s), format='audio/mp3', autoplay=True)
