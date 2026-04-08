import streamlit as st
from groq import Groq
from openai import OpenAI
import json
import time
from gtts import gTTS
import io

# --- 1. 商业级：智能调度与抗压引擎 ---
def get_fusion_response(user_input):
    prompt = f"Japanese for '{user_input}'. Rules: N4/N5 level. 3 Examples. JSON: {{\"word\":\"\", \"reading\":\"\", \"pos\":\"\", \"level\":\"N4/N5\", \"pitch\":\"0\", \"sentences\":[{{\"jp\":\"\", \"kana\":\"\", \"cn\":\"\"}},{{\"jp\":\"\", \"kana\":\"\", \"cn\":\"\"}},{{\"jp\":\"\", \"kana\":\"\", \"cn\":\"\"}}]}}"
    
    # 获取 Secrets 中的 Key
    g_keys = st.secrets.get("GROQ_KEYS", [])
    g_key = g_keys[0] if g_keys else None
    o_key = st.secrets.get("OPENAI_API_KEY")

    # 策略 A：优先尝试 Groq (带一次静默重试机制，应对 30 人并发)
    if g_key:
        for attempt in range(2):
            try:
                client = Groq(api_key=g_key)
                comp = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0,
                    response_format={"type": "json_object"},
                    timeout=10.0
                )
                return json.loads(comp.choices[0].message.content)
            except Exception as e:
                if "rate_limit" in str(e).lower():
                    time.sleep(1.5) # 遇到频率限制，静默等待并重试
                    continue
                break # 其他错误直接切保险线路

    # 策略 B：OpenAI 终极兜底 (商业稳定性的核心)
    if o_key:
        try:
            o_client = OpenAI(api_key=o_key)
            comp = o_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return json.loads(comp.choices[0].message.content)
        except Exception:
            pass
            
    return None

# --- 2. 顶级美学界面渲染 ---
st.set_page_config(page_title="FUSION Pro", layout="centered", page_icon="👘")

st.markdown("""<style>
    .main-header { border-bottom:3px solid #1E3A8A; padding-bottom:10px; margin-bottom:20px; }
    .word-box { background:white; padding:25px; border-radius:18px; box-shadow:0 8px 20px rgba(0,0,0,0.05); border:1px solid #E5E7EB; margin-bottom:20px; }
    .card-item { border:2px solid #3B82F6; padding:18px; border-radius:12px; margin-bottom:12px; background:#F8FAFC; }
    .idx { background:#1E3A8A; color:white; width:22px; height:22px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; font-weight:bold; margin-right:8px; font-size:12px; }
    .stAudio { display:none; }
</style>""", unsafe_allow_html=True)

if "audio_config" not in st.session_state: st.session_state.audio_config = {"text": None, "slow": False, "key": 0}
if "last_res" not in st.session_state: st.session_state.last_res = None

def get_audio(text, slow=False):
    try:
        tts = gTTS(text=text, lang='ja', slow=slow)
        fp = io.BytesIO(); tts.write_to_fp(fp); fp.seek(0)
        return fp
    except: return None

st.markdown('<div class="main-header"><h1 style="color:#1E3A8A;font-size:1.6rem;">👘 FUSION 智能化日语助手 Pro</h1></div>', unsafe_allow_html=True)

query = st.text_input("", placeholder="输入词汇，开启双引擎教学...", label_visibility="collapsed")
if st.button("查询", type="primary", use_container_width=True) and query:
    with st.spinner('FUSION 智能引擎正在调度最优路径...'):
        res = get_fusion_response(query)
        if res:
            res['q_key'] = query
            st.session_state.last_res = res
        else:
            st.error("👘 线路异常繁忙，请联系管理员或稍后再试。")

# 渲染结果
if st.session_state.last_res and st.session_state.last_res.get('q_key') == query:
    r = st.session_state.last_res
    st.markdown(f'<div class="word-box"><h2 style="margin:0;color:#1E3A8A;">{r.get("word")} ({r.get("reading")})</h2><p style="color:#3B82F6;">🏷️ {r.get("pos")} | {r.get("level")} | 声调:{r.get("pitch")}</p></div>', unsafe_allow_html=True)
    if st.button("🔊 播放单词音", key="v_main", use_container_width=True):
        st.session_state.audio_config = {"text":r["word"],"slow":False,"key":st.session_state.audio_config["key"]+1}

    for i, s in enumerate(r.get('sentences', []), 1):
        st.markdown(f'<div class="card-item"><b><span class="idx">{i}</span>{s.get("jp")}</b><br><span style="color:#64748B;font-size:0.85rem;margin-left:30px;">{s.get("kana")}</span><br><span style="color:#059669;margin-left:30px;">🇨🇳 {s.get("cn")}</span></div>', unsafe_allow_html=True)
        ca, cb = st.columns(2)
        if ca.button(f"🟢 标准速 {i}", key=f"n_{i}", use_container_width=True): 
            st.session_state.audio_config = {"text":s.get("jp"),"slow":False,"key":st.session_state.audio_config["key"]+1}
        if cb.button(f"🔴 慢速 {i}", key=f"s_{i}", use_container_width=True): 
            st.session_state.audio_config = {"text":s.get("jp"),"slow":True,"key":st.session_state.audio_config["key"]+1}

if st.session_state.audio_config["text"]:
    aud = get_audio(st.session_state.audio_config["text"], st.session_state.audio_config["slow"])
    if aud: st.audio(aud, format="audio/mp3", autoplay=True)
