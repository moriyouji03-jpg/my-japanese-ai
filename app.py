import streamlit as st
from groq import Groq
from openai import OpenAI
import json
import time
from gtts import gTTS
import io

# --- 1. 引擎调度：响应提速与精准引导 ---
def get_fusion_pro(user_input):
    # 强化 N4/N5 训读优先指令
    prompt = f"""
    Target: Japanese for '{user_input}' (JLPT N4/N5 level).
    Rule: Prioritize 'Kun-yomi' (訓読み) for nouns. 
    Format: JSON only.
    {{
      "word": "汉字",
      "reading": "平假名",
      "pos": "词性",
      "level": "N4/N5",
      "pitch": "声调",
      "sentences": [
        {{"jp": "日语汉字句子", "kana": "全假名标注", "cn": "中文翻译"}}
      ]
    }}
    """
    
    g_keys = st.secrets.get("GROQ_KEYS", [])
    g_key = g_keys[0] if g_keys else None
    o_key = st.secrets.get("OPENAI_API_KEY")

    # 策略 A：Groq 高速尝试（缩短超时时间以提高整体响应感）
    if g_key:
        try:
            client = Groq(api_key=g_key)
            comp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                response_format={"type": "json_object"},
                timeout=6.0  # 6秒不回立刻切保险，不让用户久等
            )
            return json.loads(comp.choices[0].message.content)
        except:
            pass # 静默进入 B 计划

    # 策略 B：OpenAI 商业级稳定防线
    if o_key:
        try:
            o_client = OpenAI(api_key=o_key)
            comp = o_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return json.loads(comp.choices[0].message.content)
        except: pass
    return None

# --- 2. 界面与布局优化 ---
st.set_page_config(page_title="FUSION Pro", layout="centered")

st.markdown("""<style>
    .header-box { border-bottom:3px solid #1E3A8A; padding:10px 0; margin-bottom:20px; display:flex; justify-content:space-between; align-items:center; }
    .guide-text { color:#64748B; font-size:0.9rem; margin-bottom:15px; font-style:italic; }
    .word-box { background:white; padding:25px; border-radius:18px; box-shadow:0 8px 20px rgba(0,0,0,0.05); border:1px solid #E5E7EB; text-align:center; margin-bottom:20px; }
    .card-item { border:2px solid #3B82F6; padding:18px; border-radius:12px; margin-bottom:12px; background:#F8FAFC; }
    .idx { background:#1E3A8A; color:white; width:22px; height:22px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; font-weight:bold; margin-right:8px; font-size:12px; }
    .stAudio { display:none; }
</style>""", unsafe_allow_html=True)

if "audio_config" not in st.session_state: st.session_state.audio_config = {"text": None, "slow": False, "key": 0}
if "last_res" not in st.session_state: st.session_state.last_res = None

# 标题恢复：和服在右
st.markdown('<div class="header-box"><span style="color:#1E3A8A;font-size:1.6rem;font-weight:bold;">FUSION 智能化日语助手 Pro</span><span>👘</span></div>', unsafe_allow_html=True)

query = st.text_input("", placeholder="输入词汇 (例如：鸭)...", label_visibility="collapsed")

if st.button("查询", type="primary", use_container_width=True) and query:
    with st.spinner('FUSION 引擎正在智能检索中...'):
        res = get_pro_response(query)
        if res:
            res['q'] = query
            st.session_state.last_res = res

if st.session_state.last_res and st.session_state.last_res.get('q') == query:
    r = st.session_state.last_res
    
    # 引导语回归
    st.markdown('<p class="guide-text">これをみると、以下の日本語が考えられます：</p>', unsafe_allow_html=True)
    
    # 核心展示：汉字 + 假名 + 訓読み优先效果
    st.markdown(f"""
    <div class="word-box">
        <h1 style="margin:0;color:#1E3A8A;font-size:2.8rem;">{r.get('word')}</h1>
        <h3 style="margin:5px 0;color:#3B82F6;font-weight:normal;">【{r.get('reading')}】</h3>
        <p style="color:#64748B;font-size:0.9rem;">🏷️ {r.get('pos')} | JLPT {r.get('level')} | 声调:{r.get('pitch')}</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button(f"🔊 播放主单词发音", key="v_main", use_container_width=True):
        st.session_state.audio_config = {"text":r["word"],"slow":False,"key":st.session_state.audio_config["key"]+1}

    for i, s in enumerate(r.get('sentences', []), 1):
        st.markdown(f'<div class="card-item"><b><span class="idx">{i}</span>{s.get("jp")}</b><br><span style="color:#64748B;font-size:0.85rem;margin-left:30px;">{s.get("kana")}</span><br><span style="color:#059669;margin-left:30px;">🇨🇳 {s.get("cn")}</span></div>', unsafe_allow_html=True)
        ca, cb = st.columns(2)
        if ca.button(f"🟢 标准速 {i}", key=f"n_{i}", use_container_width=True): 
            st.session_state.audio_config = {"text":s.get("jp"),"slow":False,"key":st.session_state.audio_config["key"]+1}
        if cb.button(f"🔴 慢速 {i}", key=f"s_{i}", use_container_width=True): 
            st.session_state.audio_config = {"text":s.get("jp"),"slow":True,"key":st.session_state.audio_config["key"]+1}

# 发音核心
if st.session_state.audio_config["text"]:
    try:
        tts = gTTS(text=st.session_state.audio_config["text"], lang='ja', slow=st.session_state.audio_config["slow"])
        fp = io.BytesIO(); tts.write_to_fp(fp); fp.seek(0)
        st.audio(fp, format="audio/mp3", autoplay=True)
    except: pass
