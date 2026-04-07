import streamlit as st
from groq import Groq
import json
from gtts import gTTS
import io

# 1. 核心配置与样式
API_KEY = "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"
client = Groq(api_key=API_KEY)

st.markdown("""
    <style>
    .header-container { display: flex; align-items: center; justify-content: space-between; border-bottom: 3px solid #1E3A8A; padding-bottom: 10px; margin-bottom: 30px; }
    .fusion-banner { color: #1E3A8A; font-size: 2.2rem; font-weight: 800; white-space: nowrap; }
    .word-box { background: white; padding: 25px; border-radius: 18px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); border: 1px solid #E5E7EB; margin-bottom: 25px; }
    .card-1 { background-color: #DBEafe; border: 3px solid #3B82F6; padding: 20px; border-radius: 12px; margin-bottom: 15px; }
    .card-2 { background-color: #EFF6FF; border: 3px solid #60A5FA; padding: 20px; border-radius: 12px; margin-bottom: 15px; }
    .card-3 { background-color: #F8FAFC; border: 3px solid #93C5FD; padding: 20px; border-radius: 12px; margin-bottom: 15px; }
    .index-circle { background: #1E3A8A; color: white; width: 28px; height: 28px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-weight: bold; margin-right: 12px; }
    .stAudio { display: none; } 
    </style>
    """, unsafe_allow_html=True)

if "audio_config" not in st.session_state: st.session_state.audio_config = {"text": None, "slow": False, "key": 0}
if "last_result" not in st.session_state: st.session_state.last_result = None

def get_audio(text, slow=False):
    if not text: return None
    try:
        tts = gTTS(text=text, lang='ja', slow=slow)
        fp = io.BytesIO(); tts.write_to_fp(fp); fp.seek(0)
        return fp
    except: return None

# 2. 头部视觉 (和服少女 👘)
st.markdown('<div class="header-container"><div class="fusion-banner">FUSION 智能化日语学习系统 1.0</div><div style="font-size: 40px;">👘</div></div>', unsafe_allow_html=True)

# 搜索组件
c_s1, c_s2 = st.columns([4, 1])
with c_s1: user_input = st.text_input("", placeholder="输入中文词，开启专业日语联想...", label_visibility="collapsed")
with c_s2: search_btn = st.button("查询结果", type="primary", use_container_width=True)

# 初始页面逻辑
target_input = user_input
if not st.session_state.last_result and not user_input:
    st.info("🌸 你好，我是FUSION 智能语言小助手，请多多关照。")
    target_input = "你好" # 预设演示

# 3. 逻辑引擎
if target_input:
    if not st.session_state.last_result or st.session_state.last_result.get('input') != target_input:
        with st.spinner('和服萌娘校对中...'):
            try:
                # 严厉约束：必须返回完整字段，如果是你好/再见也必须有word
                prompt = f"Identify '{target_input}'. Hallucination forbidden (鸭=アヒル, NOT 鸡). Return JSON: {{'word': 'Kanji/Phrase', 'reading': 'Kana', 'pos': 'Part', 'level': 'N1-N5', 'pitch': '0', 'sentences': [{{'jp':'S', 'kana':'K', 'cn':'C', 'en':'E'}}]}}"
                comp = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": "You are a Japanese expert. Never return empty word/reading fields."}, {"role": "user", "content": prompt}],
                    temperature=0, 
                    response_format={"type": "json_object"}
                )
                res = json.loads(comp.choices[0].message.content)
                res['input'] = target_input
                st.session_state.last_result = res
                if user_input: # 仅搜索时自动朗读
                    st.session_state.audio_config = {"text": "これについて、以下の日本語が考えられます。", "slow": False, "key": 999}
            except: st.error("和服萌娘忙碌中")

# 4. 渲染逻辑 (物理除框版)
if st.session_state.last_result:
    r = st.session_state.last_result
    st.markdown("#### 💡 これについて、以下の日本語が考えられます。")
    
    # 核心单词卡片 (只有当有word数据时才渲染框)
    if r.get('word') and r['word'] != "()":
        st.markdown('<div class="word-box">', unsafe_allow_html=True)
        cw1, cw2 = st.columns([0.7, 0.3])
        with cw1:
            st.markdown(f"<h2 style='margin:0; color:#1E3A8A;'>{r['word']} ({r.get('reading', '--')})</h2>", unsafe_allow_html=True)
            st.write(f"🏷️ {r.get('pos','-')} | {r.get('level','-')} | 声调: {r.get('pitch','-')}")
        with cw2:
            st.write("")
            if st.button("🔊 播放单词", key="v_main", use_container_width=True):
                st.session_state.audio_config = {"text": r['word'], "slow": False, "key": st.session_state.audio_config["key"]+1}
        st.markdown('</div>', unsafe_allow_html=True)

    # 例句渲染 (只有当有sentences时才显示)
    sentences = r.get('sentences', [])[:3]
    if sentences:
        st.markdown("<h3 style='color:#
