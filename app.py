import streamlit as st
from groq import Groq
import json
from gtts import gTTS
import io

# 1. 核心配置：API 钥匙
API_KEY = "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"
client = Groq(api_key=API_KEY)

# 初始化 Session State，用于实现“排他性播放”逻辑
if "playing_id" not in st.session_state:
    st.session_state.playing_id = None
if "last_result" not in st.session_state:
    st.session_state.last_result = None

# 定义发音生成器
def get_audio(text):
    if not text: return None
    try:
        tts = gTTS(text=text, lang='ja')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp
    except: return None

# 2. 页面美化
st.set_page_config(page_title="AI日语联想学习", layout="centered")
st.title("JP 日本語学習 - 智能联想系统 3.1")
st.caption("语义精准版 - 解决错误联想与排他播放")
# 3. 交互与 AI 逻辑
user_input = st.text_input("📝 请输入中文单词或成语：", placeholder="例如：鸭")

# 只有当输入变化时，才调用 AI，避免重复消耗额度
if user_input and (not st.session_state.last_result or st.session_state.last_result['input'] != user_input):
    with st.spinner('专家正在进行双语语义对齐，严防幻觉...'):
        try:
            # 强化指令：通过 System Message 和极低温度控制 AI 逻辑
            prompt = f"请针对 '{user_input}' 联想一个准确的常用日语单词（严禁出错，如：鸭不可联想为鸡）。提供假名、数字音调及3个N5-N4水平例句。只输出格式正确的JSON。"
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "你是一个严谨的日语词典老师，只输出100%语义对齐的JSON。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1, # 极低随机性，确保不乱想
                response_format={"type": "json_object"}
            )
            
            res_data = json.loads(completion.choices[0].message.content)
            res_data['input'] = user_input
            st.session_state.last_result = res_data
            st.session_state.playing_id = None # 换词时停止所有声音
        except Exception as e:
            st.error("❌ 逻辑模块波动，请尝试刷新。")
            # 4. 界面渲染
if st.session_state.last_result:
    res = st.session_state.last_result
    st.success(f"✨ 专家联想成功")
    
    # 单词主内容
    c_w1, c_w2 = st.columns([3, 1])
    with c_w1:
        st.header(f"{res.get('word')} ({res.get('reading')})")
        st.write(f"**音调核：** {res.get('pitch')}")
    with c_w2:
        if st.button("🔊 单词发音", key="btn_word"):
            st.session_state.playing_id = "word"
        
        # 只有 ID 匹配时才渲染播放器并自动播放
        if st.session_state.playing_id == "word":
            st.audio(get_audio(res.get('word')), format='audio/mp3', autoplay=True)

    st.info(f"💡 专家建议：{res.get('tip', '注意发音细节')}")
    st.divider()
    
    # 例句分行展示
    st.subheader("📖 专家级例句练习")
    sentences = res.get('sentences', [])
    for idx, s in enumerate(sentences, 1):
        col_a, col_b = st.columns([0.7, 0.3])
        with col_a:
            st.write(f"**{idx}.** {s}")
        with col_b:
            if st.button(f"播放例句 {idx}", key=f"btn_{idx}"):
                st.session_state.playing_id = f"sent_{idx}"
            
            # 排他性播放控制
            if st.session_state.playing_id == f"sent_{idx}":
                st.audio(get_audio(s), format='audio/mp3', autoplay=True)
