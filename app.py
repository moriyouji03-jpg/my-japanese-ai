import streamlit as st
from groq import Groq
import json
from gtts import gTTS
import io

# 1. 核心配置与 FUSION 顶级美学样式
API_KEY = "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"
client = Groq(api_key=API_KEY)

st.markdown("""
    <style>
    .header-container { display: flex; align-items: center; justify-content: space-between; border-bottom: 3px solid #1E3A8A; padding-bottom: 10px; margin-bottom: 30px; }
    .fusion-banner { color: #1E3A8A; font-size: 2.2rem; font-weight: 800; white-space: nowrap; }
    /* 核心单词卡片：纯净悬浮 */
    .word-box { background: white; padding: 25px; border-radius: 18px; box-shadow: 0 10px 20px rgba(0,0,0,0.05); border: 1px solid #E5E7EB; margin-bottom: 25px; }
    /* 色阶渐变例句卡片 - 3px加粗边框 */
    .card-1 { background-color: #DBEafe; border: 3px solid #3B82F6; padding: 20px; border-radius: 12px; margin-bottom: 15px; }
    .card-2 { background-color: #EFF6FF; border: 3px solid #60A5FA; padding: 20px; border-radius: 12px; margin-bottom: 15px; }
    .card-3 { background-color: #F8FAFC; border: 3px solid #93C5FD; padding: 20px; border-radius: 12px; margin-bottom: 15px; }
    .index-circle { background: #1E3A8A; color: white; width: 28px; height: 28px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-weight: bold; margin-right: 12px; }
    .kana-sub { background: white; color: #6B7280; padding: 3px 8px; border-radius: 5px; font-size: 0.85rem; }
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

if (user_input or search_btn) and user_input:
    if not st.session_state.last_result or st.session_state.last_result.get('input') != user_input:
        with st.spinner('和服萌娘正在严谨检索...'):
            try:
                # 强力约束 Prompt：强制语义对齐，防止鸭子变鸡
                prompt = f"""
                Translate '{user_input}' to Japanese correctly. 
                Hallucination is forbidden (e.g., 鸭=アヒル/鴨, NOT 鸡).
                Return ONLY JSON with EXACTLY 3 sentences. 
                Structure: {{'word': 'Kanji', 'reading': 'Kana', 'pos': 'part', 'level': 'N1-N5', 'pitch': '0', 'sentences': [{{'jp':'S', 'kana':'K', 'cn':'C', 'en':'E'}}]}}
                """
                comp = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are a Japanese-Chinese dictionary. Accuracy is your priority. No empty fields allowed."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0, 
                    response_format={"type": "json_object"}
                )
                res = json.loads(comp.choices[0].message.content)
                res['input'] = user_input
                st.session_state.last_result = res
                # 自动朗读衔接语
                st.session_state.audio_config = {"text": "これについて、以下の日本語が考えられます。", "slow": False, "key": 999}
            except: st.error("数据获取失败，请重试")

# 3. 结果渲染 (物理去除多余空框逻辑)
if st.session_state.last_result:
    r = st.session_state.last_result
    # 衔接语
    st.markdown("#### 💡 これについて、以下の日本語が考えられます。")
    
    # 核心单词卡片
    st.markdown('<div class="word-box">', unsafe_allow_html=True)
    cw1, cw2 = st.columns([0.7, 0.3])
    with cw1:
        word = r.get('word', '未获取')
        reading = r.get('reading', '')
        st.markdown(f"<h2 style='margin:0; color:#1E3A8A;'>{word} ({reading})</h2>", unsafe_allow_html=True)
        st.write(f"🏷️ {r.get('pos','名词')} | {r.get('level','N3')} | 声调: {r.get('pitch','0')}")
    with cw2:
        st.write("")
        if st.button("🔊 播放单词", key="v_main", use_container_width=True):
            st.session_state.audio_config = {"text": word, "slow": False, "key": st.session_state.audio_config["key"]+1}
    st.markdown('</div>', unsafe_allow_html=True)

    # 3个例句色阶卡片渲染
    st.markdown("<h3 style='color:#1E3A8A;'>参考文例 (3つの例文)</h3>", unsafe_allow_html=True)
    sentences = r.get('sentences', [])[:3]
    for idx, s in enumerate(sentences, 1):
        st.markdown(f"""
        <div class="card-{idx}">
            <div style="display:flex; align-items:flex-start;">
                <div class="index-circle">{idx}</div>
                <div style="flex:1;">
                    <div style="font-size:1.15rem; font-weight:bold; color:#1E293B;">{s.get('jp','')}</div>
                    <div style="color:#64748B; font-size:0.9rem; margin-bottom:8px;">{s.get('kana','')}</div>
                    <div style="color:#059669; font-weight:500;">🇨🇳 {s.get('cn','')}</div>
                    <div style="color:#2563EB; font-size:0.85rem;">🇺🇸 {s.get('en','')}</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)
        
        cb1, cb2, cb3 = st.columns([0.5, 0.25, 0.25])
        with cb2:
            if st.button(f"🟢 标准", key=f"n_{idx}", use_container_width=True):
                st.session_state.audio_config = {"text": s.get('jp'), "slow": False, "key": st.session_state.audio_config["key"]+1}
        with cb3:
            if st.button(f"🔴 慢速", key=f"s_{idx}", use_container_width=True):
                st.session_state.audio_config = {"text": s.get('jp'), "slow": True, "key": st.session_state.audio_config["key"]+1}

# 4. 全局发音执行
if st.session_state.audio_config["text"]:
    aud = get_audio(st.session_state.audio_config["text"], slow=st.session_state.audio_config["slow"])
    if aud: st.audio(aud, format="audio/mp3", autoplay=True)
