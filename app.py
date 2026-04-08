import streamlit as st
from groq import Groq
import json
from gtts import gTTS
import io
import time

# 1. 核心配置
API_KEY = "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"
client = Groq(api_key=API_KEY)

st.set_page_config(page_title="FUSION 日语助手", layout="centered", page_icon="👘")

st.markdown("""<style>
    .main-header { display:flex; align-items:center; justify-content:space-between; border-bottom:3px solid #1E3A8A; padding-bottom:10px; margin-bottom:20px; }
    .fusion-title { color:#1E3A8A; font-size:1.6rem; font-weight:800; }
    .word-box { background:white; padding:25px; border-radius:18px; box-shadow:0 8px 20px rgba(0,0,0,0.05); border:1px solid #E5E7EB; margin-bottom:25px; }
    .card-1 { background:#DBEafe; border:2px solid #3B82F6; padding:15px; border-radius:12px; margin-bottom:10px; }
    .card-2 { background:#EFF6FF; border:2px solid #60A5FA; padding:15px; border-radius:12px; margin-bottom:10px; }
    .card-3 { background:#F8FAFC; border:2px solid #93C5FD; padding:15px; border-radius:12px; margin-bottom:10px; }
    .idx { background:#1E3A8A; color:white; width:26px; height:26px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; font-weight:bold; margin-right:10px; }
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

# 2. 界面头部
st.markdown('<div class="main-header"><div class="fusion-title">FUSION 智能化日语学习助手 1.0</div><div style="font-size:35px;">👘</div></div>', unsafe_allow_html=True)

c1, c2 = st.columns([4, 1])
user_input = c1.text_input("", placeholder="输入中文词，开启专业日语联想...", label_visibility="collapsed")
search_btn = c2.button("查询", type="primary", use_container_width=True)

if not st.session_state.last_result and not user_input:
    st.info("🌸 你好，我是FUSION 智能助手。请输入想学习的中文词。")

if user_input and (not st.session_state.last_result or st.session_state.last_result.get('input') != user_input):
    with st.spinner('FUSION 语义校对中...'):
        # 构造稳健的 Prompt
        prompt = "Translate '" + user_input + "' to natural Japanese. "
        prompt += "Rules: If '狐狸'->'狐(きつね)', If '大家'->'皆さん'. Use N4/N5 level. "
        prompt += "JSON: {\"word\":\"\", \"reading\":\"\", \"pos\":\"\", \"level\":\"N4/N5\", \"pitch\":\"0\", \"sentences\":[{\"jp\":\"\", \"kana\":\"\", \"cn\":\"\", \"en\":\"\"}]}"
        
        success = False
        for attempt in range(3): # 增加 3 次自动重试机制
            try:
                comp = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": "Professional Japanese Teacher."}, {"role": "user", "content": prompt}],
                    temperature=0, response_format={"type": "json_object"}
                )
                res = json.loads(comp.choices[0].message.content)
                res['input'] = user_input
                st.session_state.last_result = res
                success = True
                break
            except Exception as e:
                time.sleep(1) # 遇到繁忙时等待 1 秒再试
        
        if not success:
            st.error("👘 引擎请求繁忙，请稍微等待 5 秒后再次点击查询。")

# 3. 结果渲染 (只有当输入匹配时才显示结果)
if st.session_state.last_result and st.session_state.last_result.get('input') == user_input:
    r = st.session_state.last_result
    st.markdown("#### 💡 联想结果：")
    
    if r.get('word'):
        st.markdown(f'<div class="word-box"><h2 style="margin:0;color:#1E3A8A;">{r["word"]} ({r.get("reading","")})</h2><div style="color:#3B82F6;">🏷️ {r.get("pos","")} | {r.get("level","")} | 声调:{r.get("pitch","")}</div></div>', unsafe_allow_html=True)
        if st.button("🔊 播放单词音", key="v_main", use_container_width=True):
            st.session_state.audio_config = {"text":r["word"],"slow":False,"key":st.session_state.audio_config["key"]+1}

    sents = r.get('sentences', [])[:3]
    if sents:
        st.markdown("<h3 style='color:#1E3A8A;margin-top:10px;'>参考文例</h3>", unsafe_allow_html=True)
        for i, s in enumerate(sents, 1):
            st.markdown(f'<div class="card-{i}"><div style="display:flex;"><div class="idx">{i}</div><div style="flex:1;"><b>{s.get("jp","")}</b><br><span style="font-size:0.85rem;color:#64748B;">{s.get("kana","")}</span><br><span style="color:#059669;">🇨🇳 {s.get("cn","")}</span></div></div></div>', unsafe_allow_html=True)
            ca, cb = st.columns(2)
            if ca.button(f"🟢 标准速 {i}", key=f"n_{i}", use_container_width=True): st.session_state.audio_config = {"text":s.get("jp"),"slow":False,"key":st.session_state.audio_config["key"]+1}
            if cb.button(f"🔴 慢速 {i}", key=f"s_{i}", use_container_width=True): st.session_state.audio_config = {"text":s.get("jp"),"slow":True,"key":st.session_state.audio_config["key"]+1}

# 4. 全局发音
if st.session_state.audio_config["text"]:
    aud = get_audio(st.session_state.audio_config["text"], st.session_state.audio_config["slow"])
    if aud: st.audio(aud, format="audio/mp3", autoplay=True)
