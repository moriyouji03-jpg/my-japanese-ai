import streamlit as st
from groq import Groq
import json
from gtts import gTTS
import io
import pandas as pd
import os

# 1. 核心安全配置：多模型冗余机制
API_KEY = "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"
client = Groq(api_key=API_KEY)

st.set_page_config(page_title="FUSION 日语助手", layout="wide", page_icon="👘")

# 注入 FUSION 顶级美学样式：极致去框 + 响应式布局
st.markdown("""<style>
    .stSidebar { background-color: #F8FAFC; border-right: 1px solid #E2E8F0; }
    .main-title { color: #1E3A8A; font-size: 1.8rem; font-weight: 800; border-bottom: 3px solid #1E3A8A; padding-bottom: 10px; margin-bottom: 20px; }
    .word-box { background: white; padding: 25px; border-radius: 18px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); border: 1px solid #E5E7EB; margin-bottom: 25px; }
    .card-1 { background:#DBEafe; border:2px solid #3B82F6; padding:15px; border-radius:12px; margin-bottom:10px; }
    .card-2 { background:#EFF6FF; border:2px solid #60A5FA; padding:15px; border-radius:12px; margin-bottom:10px; }
    .card-3 { background:#F8FAFC; border:3px solid #93C5FD; padding:15px; border-radius:12px; margin-bottom:10px; }
    .idx { background:#1E3A8A; color:white; width:26px; height:26px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; font-weight:bold; margin-right:10px; }
    .stAudio { display:none; }
</style>""", unsafe_allow_html=True)

# 状态初始化
if "audio_config" not in st.session_state: st.session_state.audio_config = {"text": None, "slow": False, "key": 0}
if "last_result" not in st.session_state: st.session_state.last_result = None

def get_audio(text, slow=False):
    try:
        tts = gTTS(text=text, lang='ja', slow=slow)
        fp = io.BytesIO(); tts.write_to_fp(fp); fp.seek(0)
        return fp
    except: return None

# 2. 侧边栏导航架构
with st.sidebar:
    st.markdown("## 👘 FUSION 导航")
    menu = st.radio("功能模块：", ["🏠 智能联想助手", "📅 每周精选 7 句", "🔤 五十音图"])
    st.divider()
    st.caption("FUSION 智能化日语学习助手 1.5")
    st.caption("针对 JLPT N4, N5 级别优化")

# --- 模块 1：智能联想助手 (语义锁死版) ---
if menu == "🏠 智能联想助手":
    st.markdown('<div class="main-title">FUSION 智能联想助手 1.5 (N4, N5)</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns([4, 1])
    user_input = c1.text_input("", placeholder="输入中文（例如：狐狸、大家、工作）", label_visibility="collapsed")
    search_btn = c2.button("开启联想", type="primary", use_container_width=True)

    if user_input or search_btn:
        if not st.session_state.last_result or st.session_state.last_result.get('input') != user_input:
            with st.spinner('FUSION 语义校对中...'):
                # 语义防错：硬编码纠正易错词汇
                prompt = f"""Identify the most NATURAL Japanese for: "{user_input}". 
                RULES: 
                - If '狐狸', output '狐 (きつね)', NOT '狐狸'. 
                - If '大家', output '皆さん (みなさん)', NOT '大家'. 
                - Prioritize N4/N5 high-frequency words.
                Return JSON only: {{"word":"", "reading":"", "pos":"", "level":"N4/N5", "pitch":"0", "sentences":[{"jp":"","kana":"","cn":"","en":""}]}}"""
                
                try:
                    comp = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": "You are a professional Japanese teacher. Direct Hanzi translation is forbidden."}, {"role": "user", "content": prompt}],
                        temperature=0, response_format={"type": "json_object"}
                    )
                    res = json.loads(comp.choices[0].message.content)
                    res['input'] = user_input
                    st.session_state.last_result = res
                except Exception:
                    st.error("👘 引擎响应波动，请刷新或稍后重试。")

    if st.session_state.last_result:
        r = st.session_state.last_result
        st.markdown("#### 💡 结果如下：")
        if r.get('word') and r['word'] != "()":
            st.markdown(f'<div class="word-box"><h2 style="margin:0;color:#1E3A8A;">{r["word"]} ({r.get("reading","")})</h2><div style="color:#3B82F6;">🏷️ {r.get("pos","")} | {r.get("level","")} | 声调:{r.get("pitch","")}</div></div>', unsafe_allow_html=True)
            if st.button("🔊 播放单词", key="v_main", use_container_width=True):
                st.session_state.audio_config = {"text":r["word"],"slow":False,"key":st.session_state.audio_config["key"]+1}

        sents = r.get('sentences', [])[:3]
        if sents:
            st.markdown("<h3 style='color:#1E3A8A;'>参考例句 (3个)</h3>", unsafe_allow_html=True)
            for idx, s in enumerate(sents, 1):
                st.markdown(f'<div class="card-{idx}"><div style="display:flex;"><div class="idx">{idx}</div><div style="flex:1;"><b>{s.get("jp","")}</b><br><span style="font-size:0.85rem;color:#64748B;">{s.get("kana","")}</span><br><span style="color:#059669;">🇨🇳 {s.get("cn","")}</span></div></div></div>', unsafe_allow_html=True)
                cols = st.columns(2)
                if cols[0].button(f"🟢 标准 {idx}", key=f"n_{idx}"): st.session_state.audio_config = {"text":s.get("jp"),"slow":False,"key":st.session_state.audio_config["key"]+1}
                if cols[1].button(f"🔴 慢速 {idx}", key=f"s_{idx}"): st.session_state.audio_config = {"text":s.get("jp"),"slow":True,"key":st.session_state.audio_config["key"]+1}

# --- 模块 2：每周精选 7 句 (防崩溃版) ---
elif menu == "📅 每周精选 7 句":
    st.markdown('<div class="main-title">📅 每周精选 7 句 (数据驱动)</div>', unsafe_allow_html=True)
    csv_file = "data.csv"
    if not os.path.exists(csv_file):
        df_demo = pd.DataFrame({'id':[1],'date':['2026-04-07'],'jp':['おはよう。'],'kana':['おはよう。'],'cn':['早上好。'],'tag':['日常']})
        df_demo.to_csv(csv_file, index=False)
    
    df = pd.read_csv(csv_file)
    for index, row in df.iterrows():
        with st.expander(f"Day {index+1}: {row['cn']}"):
            st.markdown(f"### {row['jp']}")
            if st.button(f"🔊 发音", key=f"ws_{index}"):
                st.session_state.audio_config = {"text":row['jp'],"slow":False,"key":st.session_state.audio_config["key"]+1}

# --- 模块 3：五十音图 ---
else:
    st.markdown('<div class="main-title">🔤 五十音图练习</div>', unsafe_allow_html=True)
    st.info("🚧 正在同步标准 NHK 音频库，即将开放...")

# 3. 发音执行
if st.session_state.audio_config["text"]:
    aud = get_audio(st.session_state.audio_config["text"], st.session_state.audio_config["slow"])
    if aud: st.audio(aud, format="audio/mp3", autoplay=True)
