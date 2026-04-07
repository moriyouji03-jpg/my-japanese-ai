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
    /* 核心单词区：纯净悬浮卡片 */
    .word-box { background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05); border: 1px solid #E5E7EB; margin-bottom: 30px; }
    /* 例句卡片色阶渐变与加粗边框 */
    .example-container { padding: 25px; border-radius: 15px; background-color: #FAFAFA; border: 1px solid #F3F4F6; }
    .example-card-1 { background-color: #DBEafe; padding: 20px; border-radius: 12px; border: 3px solid #3B82F6; margin-bottom: 15px; } /* 深蓝 */
    .example-card-2 { background-color: #EFF6FF; padding: 20px; border-radius: 12px; border: 3px solid #60A5FA; margin-bottom: 15px; } /* 蓝 */
    .example-card-3 { background-color: #F8FAFC; padding: 20px; border-radius: 12px; border: 3px solid #93C5FD; margin-bottom: 15px; } /* 浅蓝 */
    .index-circle { background: #3B82F6; color: white; width: 28px; height: 28px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-weight: bold; margin-right: 12px; }
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

# 2. 头部视觉与查询区 (和服漫画女孩图标)
st.markdown('<div class="header-container"><div class="fusion-banner">FUSION 智能化日语学习系统 1.0</div><div style="font-size: 40px;">👘</div></div>', unsafe_allow_html=True)
c_s1, c_s2 = st.columns([4, 1])
with c_s1: user_input = st.text_input("", placeholder="输入中文词，开启和服萌娘的智慧联想...", label_visibility="collapsed")
with c_s2: search_btn = st.button("查询结果", type="primary", use_container_width=True)

if (user_input or search_btn) and user_input:
    if not st.session_state.last_result or st.session_state.last_result.get('input') != user_input:
        with st.spinner('和服萌娘正在为您构思...'):
            prompt = f"联想 '{user_input}' 的日语词及3个例句。JSON: word, reading, pos, level, pitch, sentences(jp, kana, cn, en)。"
            comp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":prompt}], temperature=0.2, response_format={"type":"json_object"})
            res = json.loads(comp.choices[0].message.content)
            res['input'] = user_input; st.session_state.last_result = res
            # 自动播放衔接语
            st.session_state.audio_config = {"text": "これについて、以下の日本語が考えられます。", "slow": False, "key": 999}

# 3. 结果渲染
if st.session_state.last_result:
    res = st.session_state.last_result
    st.markdown(f"#### 💡 これについて、以下の日本語が考えられます。")
    
    # 核心词汇展示区 (极简卡片)
    st.markdown('<div class="word-box">', unsafe_allow_html=True)
    cw1, cw2 = st.columns([0.7, 0.3])
    with cw1:
        st.markdown(f"<h1 style='color:#1E3A8A; margin:0;'>{res['word']}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:1.4rem; color:#475569;'>（{res['reading']}）</p>", unsafe_allow_html=True)
        st.markdown(f"<span style='color:#3B82F6; font-weight:bold;'>🏷️ {res.get('pos','名词')} | {res.get('level','N2')} | 声调: {res.get('pitch','[0]')}</span>", unsafe_allow_html=True)
    with cw2:
        st.write(""); if st.button("🔊 播放单词", key="v_main", use_container_width=True): st.session_state.audio_config = {"text": res['word'], "slow": False, "key": st.session_state.audio_config["key"]+1}
    st.markdown('</div>', unsafe_allow_html=True)

    # 参考例句练习区 (色阶渐变卡片)
    st.markdown('<div class="example-container">', unsafe_allow_html=True)
    st.markdown("<h3 style='color:#1E3A8A; margin-top:0;'>参考文例 (3つの例文)</h3>", unsafe_allow_html=True)
    for idx, s in enumerate(res['sentences'], 1):
        # 动态选择 CSS 类实现色阶渐变
        card_class = f"example-card-{idx}"
        st.markdown(f"""
        <div class="{card_class}">
            <div style="display: flex; align-items: flex-start;">
                <div class="index-circle">{idx}</div>
                <div style="flex: 1;">
                    <div style="font-size: 1.25rem; font-weight: 600; color: #1E293B;">{s['jp']}</div>
                    <div style="margin-top: 5px;"><span class="kana-sub">{s['kana']}</span></div>
                    <div style="color: #059669; margin-top: 10px; border-left: 3px solid #93C5FD; padding-left: 12px; font-size: 0.95rem;">{s['cn']}</div>
                    <div style="color: #64748b; font-size: 0.85rem; padding-left: 15px;">{s['en']}</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)
        
        cb1, cb2, cb3 = st.columns([0.5, 0.25, 0.25])
        with cb2:
            if st.button(f"🟢 标准速", key=f"norm_{idx}", use_container_width=True): st.session_state.audio_config = {"text": s['jp'], "slow": False, "key": st.session_state.audio_config["key"]+1}
        with cb3:
            if st.button(f"🔴 慢速", key=f"slow_{idx}", use_container_width=True): st.session_state.audio_config = {"text": s['jp'], "slow": True, "key": st.session_state.audio_config["key"]+1}
    st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.audio_config["text"]:
    with st.empty():
        aud = get_audio(st.session_state.audio_config["text"], slow=st.session_state.audio_config["slow"])
        if aud: st.audio(aud, format="audio/mp3", autoplay=True)
