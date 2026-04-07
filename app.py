import streamlit as st
from groq import Groq
import json
from gtts import gTTS
import io

# 1. 配置
API_KEY = "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"
client = Groq(api_key=API_KEY)

if "playing_id" not in st.session_state:
    st.session_state.playing_id = None
if "last_result" not in st.session_state:
    st.session_state.last_result = None

def get_audio(text):
    if not text or text in ["未获取", "None"]: return None
    try:
        tts = gTTS(text=text, lang='ja')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp
    except: return None
  # 2. 界面与逻辑
st.set_page_config(page_title="AI日语联想学习", layout="centered")
st.title("JP 日本語学習 - 智能联想系统 3.4")
st.caption("三语对照版 - 日/中/英专家级同步学习")

user_input = st.text_input("📝 请输入中文单词或成语：", placeholder="例如：工作")

if user_input and (not st.session_state.last_result or st.session_state.last_result.get('input') != user_input):
    with st.spinner('专家正在进行多语种语义对齐与翻译...'):
        try:
            # 强化 Prompt：要求 AI 为每个例句提供中英翻译
            prompt = f"""
            你是一位精通中、日、英三语的教育专家。输入：'{user_input}'。
            要求：
            1. 联想标准日语词。汉字使用日本汉字（如：工作 -> 仕事）。
            2. 输出JSON必须包含：'word', 'reading', 'pitch', 'tip'。
            3. 'sentences' 必须是一个包含3个对象的列表，每个对象包含：
               'jp' (日文例句), 'cn' (中文翻译), 'en' (英文翻译)。
            """
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "你只输出结构完美的JSON，确保翻译精准。"},
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
                "tip": raw.get("tip", "注意发音"),
                "sentences": raw.get("sentences", [])
            }
            st.session_state.playing_id = None
        except:
            st.error("专家连接超时，请重试。")
# 3. 结果渲染
if st.session_state.last_result:
    res = st.session_state.last_result
    st.success("✨ 专家三语教案生成成功")
    
    # 主单词
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
    
    # 例句三语展示
    st.subheader("📖 专家级例句练习 (日/中/英)")
    for idx, s in enumerate(res['sentences'], 1):
        col_a, col_b = st.columns([0.8, 0.2])
        with col_a:
            # 采用层级展示：日文加粗，中英次之
            st.write(f"**{idx}. {s.get('jp', '')}**")
            st.write(f"🇨🇳 {s.get('cn', '')}")
            st.write(f"🇺🇸 {s.get('en', '')}")
        with col_b:
            if st.button(f"播放", key=f"btn_{idx}"):
                st.session_state.playing_id = f"sent_{idx}"
            if st.session_state.playing_id == f"sent_{idx}":
                st.audio(get_audio(s.get('jp')), format='audio/mp3', autoplay=True)
        st.write("") # 增加间距
