import streamlit as st
from openai import OpenAI
import json
from gtts import gTTS
import io

# --- 1. 极致响应引擎 (API 调优版) ---
def get_fusion_fast(user_input):
    # 极简 Prompt，减少模型思考时间
    prompt = f"Translate '{user_input}' to Japanese (JLPT N4/N5). Prioritize '仕事' for '工作'. JSON: {{\"word\":\"\",\"reading\":\"\",\"pos\":\"\",\"level\":\"N4/N5\",\"pitch\":\"\",\"sentences\":[{{\"jp\":\"\",\"kana\":\"\",\"cn\":\"\"}}]}}"
    
    try:
        client = OpenAI(
            api_key=st.secrets["NEW_API_KEY"],
            base_url=st.secrets["NEW_BASE_URL"]
        )
        # 增加 stream=False 以确保 JSON 一次性快速返回
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            timeout=5.0 # 强制 5 秒内返回
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        return None

# --- 2. 界面渲染 ---
st.set_page_config(page_title="FUSION Pro", layout="centered")

st.markdown("""<style>
    .header-box { border-bottom:3px solid #1E3A8A; padding:10px 0; margin-bottom:20px; display:flex; justify-content:space-between; align-items:center; }
    .guide-box { font-size:1.1rem; font-weight:bold; color:#1E3A8A; margin:15px 0; display:flex; align-items:center; }
    .word-box { background:white; padding:20px; border-radius:18px; box-shadow:0 8px 20px rgba(0,0,0,0.05); border:1px solid #E5E7EB; text-align:center; margin-bottom:15px; }
    .card-item { border:2px solid #3B82F6; padding:12px; border-radius:10px; margin-bottom:8px; background:#F8FAFC; }
    .idx { background:#1E3A8A; color:white; width:20px; height:20px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; font-weight:bold; margin-right:8px; font-size:11px; }
    .stAudio { display:none; }
</style>""", unsafe_allow_html=True)

# 状态初始化
if "audio_text" not in st.session_state: st.session_state.audio_text = None
if "res_cache" not in st.session_state: st.session_state.res_cache = None

st.markdown('<div class="header-box"><span style="color:#1E3A8A;font-size:1.6rem;font-weight:bold;">FUSION 智能化日语助手 Pro</span><span>👘</span></div>', unsafe_allow_html=True)

# 输入框
u_in = st.text_input("", placeholder="输入中文词汇...", label_visibility="collapsed")

if u_in:
    # 如果是新词，才触发查询
    if not st.session_state.res_cache or st.session_state.res_cache.get('q') != u_in:
        with st.spinner('FUSION 极速检索中...'):
            res = get_fusion_fast(u_in)
            if res:
                res['q'] = u_in
                st.session_state.res_cache = res
                # 设置自动播放文本
                st.session_state.audio_text = f"これについて、以下の日本語が考えられます。{res['word']}"

# 显示结果
if st.session_state.res_cache and st.session_state.res_cache.get('q') == u_in:
    r = st.session_state.res_cache
    st.markdown(f'<div class="guide-box">💡 这について、以下の日本語が考えられます。</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="word-box">
        <h1 style="margin:0;color:#1E3A8A;font-size:2.5rem;">{r.get('word')}</h1>
        <h3 style="margin:5px 0;color:#3B82F6;font-weight:normal;">【{r.get('reading')}】</h3>
        <p style="color:#64748B;font-size:0.85rem;">🏷️ {r.get('pos')} | {r.get('level')} | 声调:{r.get('pitch')}</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button(f"🔊 重新播放", use_container_width=True):
        st.session_state.audio_text = f"これについて、以下の日本語が考えられます。{r['word']}"

    for i, s in enumerate(r.get('sentences', []), 1):
        st.markdown(f'<div class="card-item"><b><span class="idx">{i}</span>{s.get("jp")}</b><br><span style="color:#64748B;font-size:0.8rem;margin-left:28px;">{s.get("kana")}</span><br><span style="color:#059669;margin-left:28px;font-size:0.85rem;">🇨🇳 {s.get("cn")}</span></div>', unsafe_allow_html=True)
        ca, cb = st.columns(2)
        if ca.button(f"🟢 标准速 {i}", key=f"n_{i}", use_container_width=True): 
            st.session_state.audio_text = s.get("jp")
        if cb.button(f"🔴 慢速 {i}", key=f"s_{i}", use_container_width=True): 
            st.session_state.audio_text = s.get("jp")

# --- 极速发音执行器 ---
if st.session_state.audio_text:
    try:
        tts = gTTS(text=st.session_state.audio_text, lang='ja')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        st.audio(fp, format="audio/mp3", autoplay=True)
        # 播完重置状态，防止循环
        st.session_state.audio_text = None
    except:
        pass
