import streamlit as st
from groq import Groq
import json
from gtts import gTTS
import io
import time

# 1. 配置两个可用模型作为冗余方案
API_KEY = "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"
client = Groq(api_key=API_KEY)
MODELS = ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"] # 备选模型列表

st.set_page_config(page_title="FUSION 日语助手", layout="centered", page_icon="👘")

st.markdown("""<style>
    .main-header { display:flex; align-items:center; justify-content:space-between; border-bottom:3px solid #1E3A8A; padding-bottom:10px; margin-bottom:20px; }
    .fusion-title { color:#1E3A8A; font-size:1.6rem; font-weight:800; }
    .word-box { background:white; padding:25px; border-radius:18px; box-shadow:0 8px 20px rgba(0,0,0,0.05); border:1px solid #E5E7EB; margin-bottom:25px; }
    .card-item { border:2px solid #3B82F6; padding:15px; border-radius:12px; margin-bottom:10px; }
    .idx { background:#1E3A8A; color:white; width:26px; height:26px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; font-weight:bold; margin-right:10px; }
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
user_input = c1.text_input("", placeholder="输入中文词，例如：铅笔、大家...", label_visibility="collapsed")
search_btn = c2.button("查询", type="primary", use_container_width=True)

if not user_input:
    st.info("🌸 您好，我是FUSION 智能助手。请输入想学习的中文词并点击查询。")

if (search_btn or (user_input and not st.session_state.last_result)) and user_input:
    # 强制清除旧结果，避免“查铅笔出工作”的错位
    if st.session_state.last_result and st.session_state.last_result.get('input') != user_input:
        st.session_state.last_result = None

    with st.spinner('FUSION 语义校对中...'):
        prompt = "Translate '" + user_input + "' to Japanese. Rules: N4/N5 level, Kun-yomi prioritized. JSON: {\"word\":\"\", \"reading\":\"\", \"pos\":\"\", \"level\":\"N4/N5\", \"pitch\":\"0\", \"sentences\":[{\"jp\":\"\", \"kana\":\"\", \"cn\":\"\", \"en\":\"\"}]}"
        
        success = False
        # 尝试轮询模型
        for m_name in MODELS:
            try:
                comp = client.chat.completions.create(
                    model=m_name,
                    messages=[{"role": "system", "content": "Professional Japanese Teacher. Anti-hallucination."}, {"role": "user", "content": prompt}],
                    temperature=0, response_format={"type": "json_object"}
                )
                res = json.loads(comp.choices[0].message.content)
                res['input'] = user_input
                st.session_state.last_result = res
                success = True
                break # 成功则跳出循环
            except Exception:
                time.sleep(1) # 失败则等待1秒尝试下一个模型
        
        if not success:
            st.error("👘 FUSION 引擎目前繁忙。原因：由于使用的是免费版 API，请求次数受限。建议：请等待 10 秒后再次点击查询。")

# 3. 结果渲染
if st.session_state.last_result and st.session_state.last_result.get('input') == user_input:
    r = st.session_state.last_result
    st.markdown("#### 💡 联想结果：")
    
    # 单词卡片
    if r.get('word'):
        st.markdown(f'<div class="word-box"><h2 style="margin:0;color:#1E3A8A;">{r["word"]} ({r.get("reading","")})</h2><div style="color:#3B82F6;">🏷️ {r.get("pos","")} | {r.get("level","")} | 声调:{r.get("pitch","")}</div></div>', unsafe_allow_html=True)
        if st.button("🔊 播放单词音", key="v_main", use_container_width=True):
            st.session_state.audio_config = {"text":r["word"],"slow":False,"key":st.session_state.audio_config["key"]+1}

    # 例句卡片
    sents = r.get('sentences', [])[:3]
    if sents:
        st.markdown("<h3 style='color:#1E3A8A;'>参考文例</h3>", unsafe_allow_html=True)
        for i, s in enumerate(sents, 1):
            st.markdown(f'<div class="card-item" style="background:#DBEafe if i==1 else #F8FAFC;"><div style="display:flex;"><div class="idx">{i}</div><div style="flex:1;"><b>{s.get("jp","")}</b><br><span style="font-size:0.85rem;color:#64748B;">{s.get("kana","")}</span><br><span style="color:#059669;">🇨🇳 {s.get("cn","")}</span></div></div></div>', unsafe_allow_html=True)
            ca, cb = st.columns(2)
            if ca.button(f"🟢 标准速 {i}", key=f"n_{i}", use_container_width=True): st.session_state.audio_config = {"text":s.get("jp"),"slow":False,"key":st.session_state.audio_config["key"]+1}
            if cb.button(f"🔴 慢速 {i}", key=f"s_{i}", use_container_width=True): st.session_state.audio_config = {"text":s.get("jp"),"slow":True,"key":st.session_state.audio_config["key"]+1}

# 4. 全局发音
if st.session_state.audio_config["text"]:
    aud = get_audio(st.session_state.audio_config["text"], st.session_state.audio_config["slow"])
    if aud: st.audio(aud, format="audio/mp3", autoplay=True)
