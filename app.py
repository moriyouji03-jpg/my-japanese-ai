import streamlit as st
from openai import OpenAI
import json
from gtts import gTTS
import io

# --- 1. 顶流水平：语义精准引擎 ---
def get_fusion_professional(user_input):
    # 强化指令：禁止生词，强制地道日语表达
    prompt = f"""
    Translate Chinese '{user_input}' to natural Japanese (JLPT N4/N5).
    Rules:
    - DO NOT use literal kanji translation (e.g., avoid '努力学ぶ').
    - Use real-life phrases (e.g., '一生懸命勉強する').
    - Provide EXACTLY 3 example sentences.
    JSON format:
    {{
      "word": "地道词汇",
      "reading": "平假名",
      "pos": "词性",
      "level": "N4/N5",
      "pitch": "声调",
      "sentences": [
        {{"jp": "句子1", "kana": "假名", "cn": "翻译"}},
        {{"jp": "句子2", "kana": "假名", "cn": "翻译"}},
        {{"jp": "句子3", "kana": "假名", "cn": "翻译"}}
      ]
    }}
    """
    try:
        client = OpenAI(api_key=st.secrets["NEW_API_KEY"], base_url=st.secrets["NEW_BASE_URL"])
        comp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            timeout=8.0
        )
        return json.loads(comp.choices[0].message.content)
    except:
        return None

# --- 2. 紧凑型界面设计 ---
st.set_page_config(page_title="FUSION Pro", layout="centered")

st.markdown("""<style>
    .header-box { border-bottom:2px solid #1E3A8A; padding:5px 0; margin-bottom:15px; display:flex; justify-content:space-between; align-items:center; }
    .guide-box { font-size:0.95rem; font-weight:bold; color:#1E3A8A; margin:10px 0; }
    .word-box { background:white; padding:15px; border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.05); border:1px solid #E5E7EB; text-align:center; margin-bottom:10px; }
    .card-item { border:1.5px solid #3B82F6; padding:10px; border-radius:8px; margin-bottom:8px; background:#F8FAFC; }
    .idx { background:#1E3A8A; color:white; width:18px; height:18px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; font-weight:bold; margin-right:6px; font-size:10px; }
    .stAudio { display:none; }
</style>""", unsafe_allow_html=True)

if "audio_text" not in st.session_state: st.session_state.audio_text = None
if "res_cache" not in st.session_state: st.session_state.res_cache = None

st.markdown('<div class="header-box"><span style="color:#1E3A8A;font-size:1.3rem;font-weight:bold;">FUSION 智能化日语助手 Pro</span><span>👘</span></div>', unsafe_allow_html=True)

u_in = st.text_input("", placeholder="输入词汇...", label_visibility="collapsed")

if u_in and (not st.session_state.res_cache or st.session_state.res_cache.get('q') != u_in):
    with st.spinner('正在地道化处理中...'):
        res = get_fusion_professional(u_in)
        if res:
            res['q'] = u_in
            st.session_state.res_cache = res
            st.session_state.audio_text = f"これについて、以下の日本語が考えられます。{res['word']}"

if st.session_state.res_cache and st.session_state.res_cache.get('q') == u_in:
    r = st.session_state.res_cache
    st.markdown(f'<div class="guide-box">💡 これについて、以下の日本語が考えられます。</div>', unsafe_allow_html=True)
    
    # 紧凑型词条显示
    st.markdown(f"""
    <div class="word-box">
        <h2 style="margin:0;color:#1E3A8A;font-size:1.8rem;">{r.get('word')}</h2>
        <h4 style="margin:2px 0;color:#3B82F6;font-weight:normal;">【{r.get('reading')}】</h4>
        <p style="color:#64748B;font-size:0.8rem;margin:0;">🏷️ {r.get('pos')} | {r.get('level')} | 声调:{r.get('pitch')}</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button(f"🔊 重新播报引导语和单词", use_container_width=True):
        st.session_state.audio_text = f"これについて、以下の日本語が考えられます。{r['word']}"

    # 渲染 3 个句子
    for i, s in enumerate(r.get('sentences', []), 1):
        st.markdown(f'<div class="card-item"><b><span class="idx">{i}</span>{s.get("jp")}</b><br><span style="color:#64748B;font-size:0.75rem;margin-left:24px;">{s.get("kana")}</span><br><span style="color:#059669;margin-left:24px;font-size:0.8rem;">🇨🇳 {s.get("cn")}</span></div>', unsafe_allow_html=True)
        ca, cb = st.columns(2)
        if ca.button(f"🟢 标准速 {i}", key=f"n_{i}", use_container_width=True): 
            st.session_state.audio_text = s.get("jp")
        if cb.button(f"🔴 慢速 {i}", key=f"s_{i}", use_container_width=True): 
            st.session_state.audio_text = s.get("jp")

# 发音核心逻辑
if st.session_state.audio_text:
    try:
        tts = gTTS(text=st.session_state.audio_text, lang='ja')
        fp = io.BytesIO(); tts.write_to_fp(fp); fp.seek(0)
        st.audio(fp, format="audio/mp3", autoplay=True)
        st.session_state.audio_text = None
    except: pass
