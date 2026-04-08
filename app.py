import streamlit as st
from groq import Groq
from openai import OpenAI
import json
import time
from gtts import gTTS
import io

# --- 1. 极致响应与语义加固引擎 ---
def get_fusion_ultimate(user_input):
    # 强化 Prompt：明确禁止“伪汉字”，强制 JLPT 常用词义
    prompt = f"""
    Translate Chinese '{user_input}' to Japanese.
    Context: Daily life & Business (JLPT N4/N5).
    Rules: 
    - Use common words (e.g., '工作' -> '仕事', NOT '工作').
    - Prioritize Kun-yomi.
    Format: JSON ONLY.
    {{
      "word": "汉字",
      "reading": "平假名",
      "pos": "词性",
      "level": "N4/N5",
      "pitch": "声调",
      "sentences": [
        {{"jp": "句子", "kana": "假名", "cn": "翻译"}}
      ]
    }}
    """
    
    g_key = st.secrets.get("GROQ_KEYS", [None])[0]
    o_key = st.secrets.get("OPENAI_API_KEY")

    # 极速策略：2.5秒熔断机制
    if g_key:
        try:
            client = Groq(api_key=g_key)
            comp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                response_format={"type": "json_object"},
                timeout=2.5 
            )
            return json.loads(comp.choices[0].message.content)
        except: pass

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

# --- 2. 界面与自动发音逻辑 ---
st.set_page_config(page_title="FUSION Pro", layout="centered")

st.markdown("""<style>
    .header-box { border-bottom:3px solid #1E3A8A; padding:10px 0; margin-bottom:20px; display:flex; justify-content:space-between; align-items:center; }
    .guide-box { font-size:1.1rem; font-weight:bold; color:#1E3A8A; margin:15px 0; display:flex; align-items:center; }
    .word-box { background:white; padding:25px; border-radius:18px; box-shadow:0 8px 20px rgba(0,0,0,0.05); border:1px solid #E5E7EB; text-align:center; margin-bottom:20px; }
    .card-item { border:2px solid #3B82F6; padding:18px; border-radius:12px; margin-bottom:12px; background:#F8FAFC; }
    .idx { background:#1E3A8A; color:white; width:22px; height:22px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; font-weight:bold; margin-right:8px; font-size:12px; }
    .stAudio { display:none; }
</style>""", unsafe_allow_html=True)

if "audio_config" not in st.session_state: st.session_state.audio_config = {"text": None, "slow": False, "key": 0, "auto": False}
if "last_res" not in st.session_state: st.session_state.last_res = None

st.markdown('<div class="header-box"><span style="color:#1E3A8A;font-size:1.6rem;font-weight:bold;">FUSION 智能化日语助手 Pro</span><span>👘</span></div>', unsafe_allow_html=True)

u_in = st.text_input("", placeholder="输入中文词汇...", label_visibility="collapsed")

if st.button("查询", type="primary", use_container_width=True) and u_in:
    with st.spinner('FUSION 引擎加速调度中...'):
        res = get_fusion_ultimate(u_in)
        if res:
            res['q'] = u_in
            st.session_state.last_res = res
            # --- 自动播放触发器 ---
            guide_txt = "これについて、以下の日本語が考えられます。"
            st.session_state.audio_config = {
                "text": f"{guide_txt} {res['word']}", 
                "slow": False, 
                "key": st.session_state.audio_config["key"]+1,
                "auto": True
            }

if st.session_state.last_res and st.session_state.last_res.get('q') == u_in:
    r = st.session_state.last_res
    st.markdown(f'<div class="guide-box">💡 これについて、以下の日本語が考えられます。</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="word-box">
        <h1 style="margin:0;color:#1E3A8A;font-size:2.8rem;">{r.get('word')}</h1>
        <h3 style="margin:5px 0;color:#3B82F6;font-weight:normal;">【{r.get('reading')}】</h3>
        <p style="color:#64748B;font-size:0.9rem;">🏷️ {r.get('pos')} | JLPT {r.get('level')} | 声调:{r.get('pitch')}</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button(f"🔊 重新播放单词音", key="v_main", use_container_width=True):
        st.session_state.audio_config = {"text": f"これについて、以下の日本語が考えられます。 {r['word']}", "slow": False, "key": st.session_state.audio_config["key"]+1, "auto": True}

    for i, s in enumerate(r.get('sentences', []), 1):
        st.markdown(f'<div class="card-item"><b><span class="idx">{i}</span>{s.get("jp")}</b><br><span style="color:#64748B;font-size:0.85rem;margin-left:30px;">{s.get("kana")}</span><br><span style="color:#059669;margin-left:30px;">🇨🇳 {s.get("cn")}</span></div>', unsafe_allow_html=True)
        ca, cb = st.columns(2)
        if ca.button(f"🟢 标准速 {i}", key=f"n_{i}", use_container_width=True): 
            st.session_state.audio_config = {"text": s.get("jp"), "slow": False, "key": st.session_state.audio_config["key"]+1, "auto": True}
        if cb.button(f"🔴 慢速 {i}", key=f"s_{i}", use_container_width=True): 
            st.session_state.audio_config = {"text": s.get("jp"), "slow": True, "key": st.session_state.audio_config["key"]+1, "auto": True}

# 发音处理
if st.session_state.audio_config["text"]:
    try:
        tts = gTTS(text=st.session_state.audio_config["text"], lang='ja', slow=st.session_state.audio_config["slow"])
        fp = io.BytesIO(); tts.write_to_fp(fp); fp.seek(0)
        st.audio(fp, format="audio/mp3", autoplay=True)
    except: pass
