import streamlit as st
from groq import Groq
import json
from gtts import gTTS
import io

# 1. 基础配置
API_KEY = "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"
client = Groq(api_key=API_KEY)

if "playing_id" not in st.session_state:
    st.session_state.playing_id = None
if "last_result" not in st.session_state:
    st.session_state.last_result = None

def get_audio(text):
    if not text or text == "None": return None
    try:
        tts = gTTS(text=text, lang='ja')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp
    except: return None
        # 2. 界面与逻辑
st.set_page_config(page_title="AI日语联想学习", layout="centered")
st.title("JP 日本語学習 - 智能联想系统 3.2")
st.caption("强力纠错版 - 解决 None 报错与排他播放")

user_input = st.text_input("📝 请输入中文单词或成语：", placeholder="例如：鸭")

if user_input and (not st.session_state.last_result or st.session_state.last_result.get('input') != user_input):
    with st.spinner('专家正在进行最后一次逻辑校准...'):
        try:
            # 强化 Prompt：明确要求字段名，并给出一个空值填充逻辑
            prompt = f"""
            你是一位顶尖日语专家。请针对 '{user_input}' 返回 JSON。
            必须包含这5个键，严禁改名：'word', 'reading', 'pitch', 'tip', 'sentences'。
            'sentences' 必须是一个包含3个句子的列表。
            示例：输入'秋' -> {{"word":"秋","reading":"あき","pitch":"[1]","tip":"注意开口","sentences":["秋ですね","红葉です","涼しい"]}}
            """
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "你是一个严谨的机器人，只输出符合要求的JSON。"},
                          {"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            raw_data = json.loads(completion.choices[0].message.content)
            # 关键：手动赋能，防止 None 出现
            st.session_state.last_result = {
                "input": user_input,
                "word": raw_data.get("word", "未获取"),
                "reading": raw_data.get("reading", "未获取"),
                "pitch": raw_data.get("pitch", "未知"),
                "tip": raw_data.get("tip", raw_data.get("pronunciation_tip", "注意发音")),
                "sentences": raw_data.get("sentences", ["生成失败", "生成失败", "生成失败"])
            }
            st.session_state.playing_id = None
        except:
            st.error("专家走神了，请按回车重试。")
    # 3. 渲染
if st.session_state.last_result:
    res = st.session_state.last_result
    st.success("✨ 专家联想成功")
    
    c1, c2 = st.columns([3, 1])
    with c1:
        st.header(f"{res['word']} ({res['reading']})")
        st.write(f"**音调核：** {res['pitch']}")
    with c2:
        if st.button("🔊 单词发音", key="btn_word"):
            st.session_state.playing_id = "word"
        if st.session_state.playing_id == "word":
            st.audio(get_audio(res['word']), format='audio/mp3', autoplay=True)

    st.info(f"💡 专家建议：{res['tip']}")
    st.divider()
    
    st.subheader("📖 专家级例句练习")
    for idx, s in enumerate(res['sentences'], 1):
        col_a, col_b = st.columns([0.7, 0.3])
        with col_a:
            st.write(f"**{idx}.** {s}")
        with col_b:
            if st.button(f"播放例句 {idx}", key=f"btn_{idx}"):
                st.session_state.playing_id = f"sent_{idx}"
            if st.session_state.playing_id == f"sent_{idx}":
                st.audio(get_audio(s), format='audio/mp3', autoplay=True)        
