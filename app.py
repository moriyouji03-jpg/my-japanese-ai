import streamlit as st
from groq import Groq
from openai import OpenAI
import json
from gtts import gTTS
import io
import time

# 1. 引擎初始化
def init_clients():
    g_client, o_client = None, None
    if "GROQ_API_KEY" in st.secrets:
        g_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    if "OPENAI_API_KEY" in st.secrets:
        o_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    return g_client, o_client

groq_client, openai_client = init_clients()

st.set_page_config(page_title="FUSION 日语助手 Pro", layout="centered", page_icon="👘")

st.markdown("""<style>
    .main-header { border-bottom:3px solid #1E3A8A; padding-bottom:10px; margin-bottom:20px; }
    .word-box { background:white; padding:25px; border-radius:18px; box-shadow:0 8px 20px rgba(0,0,0,0.05); border:1px solid #E5E7EB; margin-bottom:25px; }
    .card-item { border:2px solid #3B82F6; padding:18px; border-radius:12px; margin-bottom:12px; background:#F8FAFC; }
    .idx { background:#1E3A8A; color:white; width:22px; height:22px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; font-weight:bold; margin-right:8px; font-size:12px; }
    .stAudio { display:none; }
</style>""", unsafe_allow_html=True)

if "audio_config" not in st.session_state: st.session_state.audio_config = {"text": None, "slow": False, "key": 0}
if "last_result" not in st.session_state: st.session_state.last_result = None

def get_audio(text, slow=False):
    try:
        tts = gTTS(text=text, lang='ja', slow=slow)
        fp = io.BytesIO(); tts.write_to_fp(fp); fp.seek(0)
        return fp
    except: return None

# 2. 界面展示
st.markdown('<div class="main-header"><h1 style="color:#1E3A8A;font-size:1.6rem;">👘 FUSION 智能化日语学习助手 Pro</h1></div>', unsafe_allow_html=True)

c1, c2 = st.columns([4, 1])
user_input = c1.text_input("", placeholder="输入中文词，获取双引擎保障教案...", label_visibility="collapsed")
search_btn = c2.button("查询", type="primary", use_container_width=True)

# 3. 核心：静默熔断逻辑 (不报黄框，直接切换)
if search_btn and user_input:
    st.session_state.last_result = None 
    with st.spinner('FUSION 智能引擎正在调度最优路径...'):
        prompt = f"Japanese for '{user_input}'. N4/N5 level. 3 Examples. JSON: {{\"word\":\"\", \"reading\":\"\", \"pos\":\"\", \"level\":\"N4/N5\", \"pitch\":\"0\", \"sentences\":[{{\"jp\":\"\", \"kana\":\"\", \"cn\":\"\"}},{{\"jp\":\"\", \"kana\":\"\", \"cn\":\"\"}},{{\"jp\":\"\", \"kana\":\"\", \"cn\":\"\"}}]}}"
        
        final_res = None
        
        # 尝试 A：Groq (静默尝试)
        if groq_client:
            try:
                comp = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0, response_format={"type": "json_object"}
                )
                final_res = json.loads(comp.choices[0].message.content)
            except Exception:
                pass # 悄悄失败，不报错

        # 尝试 B：OpenAI (如果 A 没结果，立刻顶上)
        if not final_res and openai_client:
            try:
                comp = openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
                final_res = json.loads(comp.choices[0].message.content)
            except Exception as e:
                st.error(f"OpenAI 引擎报错: {e}")

        if final_res:
            final_res['input_key'] = user_input
            st.session_state.last_result = final_res
        else:
            st.warning("👘 当前所有教学线路繁忙，请等待 10 秒后再次查询。")

# 4. 渲染
if st.session_state.last_result and st.session_state.last_result.get('input_key') == user_input:
    r = st.session_state.last_result
    st.markdown(f'<div class="word-box"><h2 style="margin:0;color:#1E3A8A;">{r.get("word")} ({r.get("reading")})</h2><p style="color:#3B82F6;">🏷️ {r.get("pos")} | {r.get("level")} | 声调:{r.get("pitch")}</p></div>', unsafe_allow_html=True)
    if st.button("🔊 播放单词音", key="v_main", use_container_width=True):
        st.session_state.audio_config = {"text":r["word"],"slow":False,"key":st.session_state.audio_config["key"]+1}

    for i, s in enumerate(r.get('sentences', []), 1):
        st.markdown(f'<div class="card-item"><b><span class="idx">{i}</span>{s.get("jp")}</b><br><span style="color:#64748B;font-size:0.85rem;margin-left:30px;">{s.get("kana")}</span><br><span style="color:#059669;margin-left:30px;">🇨🇳 {s.get("cn")}</span></div>', unsafe_allow_html=True)
        ca, cb = st.columns(2)
        if ca.button(f"🟢 标准速 {i}", key=f"n_{i}", use_container_width=True): st.session_state.audio_config = {"text":s.get("jp"),"slow":False,"key":st.session_state.audio_config["key"]+1}
        if cb.button(f"🔴 慢速 {i}", key=f"s_{i}", use_container_width=True): st.session_state.audio_config = {"text":s.get("jp"),"slow":True,"key":st.session_state.audio_config["key"]+1}

if st.session_state.audio_config["text"]:
    aud = get_audio(st.session_state.audio_config["text"], st.session_state.audio_config["slow"])
    if aud: st.audio(aud, format="audio/mp3", autoplay=True)
