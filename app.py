import streamlit as st
from groq import Groq
import json
from gtts import gTTS
import io

# 1. 配置
API_KEY = "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"
client = Groq(api_key=API_KEY)

# 2. 注入 FUSION 顶级 UI (物理去框版)
st.markdown("""
    <style>
    .header-container { display: flex; align-items: center; justify-content: space-between; border-bottom: 3px solid #1E3A8A; padding-bottom: 10px; margin-bottom: 30px; }
    .fusion-banner { color: #1E3A8A; font-size: 2.2rem; font-weight: 800; }
    /* 彻底重写卡片样式，不再使用可能导致空框的 container */
    .word-box { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); border: 1px solid #E5E7EB; margin-top: 15px; }
    .card-1 { background-color: #DBEafe; border: 3px solid #3B82F6; padding: 15px; border-radius: 12px; margin-top: 10px; }
    .card-2 { background-color: #EFF6FF; border: 3px solid #60A5FA; padding: 15px; border-radius: 12px; margin-top: 10px; }
    .card-3 { background-color: #F8FAFC; border: 3px solid #93C5FD; padding: 15px; border-radius: 12px; margin-top: 10px; }
    .index-circle { background: #3B82F6; color: white; width: 24px; height: 24px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-weight: bold; margin-right: 10px; }
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

# 3. 头部视觉 (和服少女 👘)
st.markdown('<div class="header-container"><div class="fusion-banner">FUSION 智能化日语学习系统 1.0</div><div style="font-size: 40px;">👘</div></div>', unsafe_allow_html=True)

# 搜索区
c_s1, c_s2 = st.columns([4, 1])
with c_s1: user_input = st.text_input("", placeholder="输入中文词，开启和服萌娘的智慧联想...", label_visibility="collapsed")
with c_s2: search_btn = st.button("查询结果", type="primary", use_container_width=True)

if (user_input or search_btn) and user_input:
    if not st.session_state.last_result or st.session_state.last_result.get('input') != user_input:
        with st.spinner('和服萌娘校对中...'):
            # 极限制约：防止鸭子变鸡
            prompt = f"""
            Identify '{user_input}' carefully. Translation must be accurate (e.g., 鸭=アヒル, NOT 鸡).
            Return ONLY JSON:
            {{
                "word": "Japanese Kanji", "reading": "Kana", "pos": "noun/verb", "level": "N1-N5", "pitch": "number",
                "sentences": [
                    {{"jp":"Natural JP sentence","kana":"Reading","cn":"CH translation","en":"EN translation"}}
                ]
            }}
            """
            comp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "You are a professional dictionary. Zero hallucination allowed."}, {"role": "user", "content": prompt}],
                temperature=0, # 强制确定性，不再乱写
                response_format={"type": "json_object"}
            )
            res = json.loads(comp.choices[0].message.content)
            res['input'] = user_input
            st.session_state.last_result = res
            st.session_state.audio_config = {"text": "これについて、以下の日本語が考えられます。", "slow": False, "key": 999}

# 4. 渲染逻辑
if st.session_state.last_result:
    r = st.session_state.last_result
    st.write(f"#### 💡 これについて、以下の日本語が考えられます。")
    
    # 核心卡片
    st.markdown('<div class="word-box">', unsafe_allow_html=True)
    cw1, cw2 = st.columns([0.7, 0.3])
    with cw1:
        st.markdown(f"<h2 style='margin:0;'>{r['word']} ({r['reading']})</h2>", unsafe_allow_html=True)
        st.write(f"🏷️ {r['pos']} | {r['level']} | 声调: {r['pitch']}")
    with cw2:
        if st.button("🔊 播放单词", key="v_main", use_container_width=True):
            st.session_state.audio_config = {"text": r['word'], "slow": False, "key": st.session_state.audio_config["key"]+1}
    st.markdown('</div>', unsafe_allow_html=True)

    # 色阶例句
    st.write("### 参考文例 (3つの例文)")
    for idx, s in enumerate(r['sentences'], 1):
        st.markdown(f"""
        <div class="card-{idx}">
            <div style="display:flex; align-items:flex-start;">
                <div class="index-circle">{idx}</div>
                <div style="flex:1;">
                    <div style="font-size:1.1rem; font-weight:bold;">{s['jp']}</div>
                    <div style="color:#666; font-size:0.85rem;">{s['kana']}</div>
                    <div style="color:#059669; margin-top:5px;">🇨🇳 {s['cn']}</div>
                    <div style="color:#2563EB; font-size:0.8rem;">🇺🇸 {s['en']}</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)
        cb1, cb2, cb3 = st.columns([0.5, 0.25, 0.25])
        with cb2:
            if st.button(f"🟢 标准", key=f"n_{idx}", use_container_width=True):
                st.session_state.audio_config = {"text": s['jp'], "slow": False, "key": st.session_state.audio_config["key"]+1}
        with cb3:
            if st.button(f"🔴 慢速", key=f"s_{idx}", use_container_width=True):
                st.session_state.audio_config = {"text": s['jp'], "slow": True, "key": st.session_state.audio_config["key"]+1}

# 语音执行
if st.session_state.audio_config["text"]:
    aud = get_audio(st.session_state.audio_config["text"], slow=st.session_state.audio_config["slow"])
    if aud: st.audio(aud, format="audio/mp3", autoplay=True)
