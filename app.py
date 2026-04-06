import streamlit as st
from groq import Groq
import json
from gtts import gTTS
import io

# 1. 核心配置：API 钥匙
API_KEY = "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"
client = Groq(api_key=API_KEY)

# 初始化 Session State
if "playing_id" not in st.session_state:
    st.session_state.playing_id = None
if "last_result" not in st.session_state:
    st.session_state.last_result = None

# 定义发音生成器：强制使用 'ja' (日语) 语种
def get_audio(text):
    if not text or text in ["未获取", "None"]: return None
    try:
        tts = gTTS(text=text, lang='ja')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp
    except: return None

# 2. 页面设置
st.set_page_config(page_title="AI日语联想学习", layout="centered")
st.title("JP 日本語学習 - 智能联想系统 3.3")
st.caption("语种对齐版 - 修复朗读中文与汉字错误")
# 3. 交互与 AI 逻辑
user_input = st.text_input("📝 请输入中文单词或成语：", placeholder="例如：工作")

if user_input and (not st.session_state.last_result or st.session_state.last_result.get('input') != user_input):
    with st.spinner('专家正在精准校对日语汉字与发音...'):
        try:
            # 强化 Prompt：明确要求日语汉字（如：仕事），严禁使用中文简体
            prompt = f"""
            你是一位资深日语专家。
            输入中文：'{user_input}'。
            
            任务：
            1. 联想对应的日语词。汉字必须使用日本标准汉字（如：工作 -> 仕事，鸭 -> 鴨 或 アヒル）。
            2. 输出JSON必须包含：'word' (日语汉字), 'reading' (假名), 'pitch' (音调核数字), 'tip' (建议), 'sentences' (3个标准例句)。
            """
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "你只输出日语汉字和假名，严禁在word字段中使用中文简体字。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            raw = json.loads(completion.choices[0].message.content)
            st.session_state.last_result = {
                "input": user_input,
                "word": raw.get("word", "未获取"),
                "reading": raw.get("reading", "未获取"),
                "pitch": raw.get("pitch", "未知"),
                "tip": raw.get("tip", raw.get("pronunciation_tip", "注意发音")),
                "sentences": raw.get("sentences", [])
            }
            st.session_state.playing_id = None
        except:
            st.error("专家连接超时，请重试。")
            # 4. 界面渲染
if st.session_state.last_result:
    res = st.session_state.last_result
    st.success("✨ 专家联想成功")
    
    # 标题与主单词发音
    c1, c2 = st.columns([3, 1])
    with c1:
        # 显示联想后的日语词（如：仕事）
        st.header(f"{res['word']} ({res['reading']})")
        st.write(f"**音调核：** {res['pitch']}")
    with c2:
        if st.button("🔊 单词发音", key="btn_word"):
            st.session_state.playing_id = "word"
        
        if st.session_state.playing_id == "word":
            # 【核心修复】强制朗读联想后的日语词，而非原始输入
            audio_data = get_audio(res['word'])
            if audio_data:
                st.audio(audio_data, format='audio/mp3', autoplay=True)

    st.info(f"💡 专家建议：{res['tip']}")
    st.divider()
    
    # 例句排他播放
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
