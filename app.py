import streamlit as st
from groq import Groq
import json
from gtts import gTTS
import io
import time

# 1. 核心安全与多模型配置
# 这里的模型顺序经过优化，优先使用高成功率模型
API_KEY = "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"
client = Groq(api_key=API_KEY)
REDUNDANT_MODELS = ["llama-3.3-70b-versatile", "mixtral-8x7b-32768", "llama3-70b-8192"]

st.set_page_config(page_title="FUSION 日语助手", layout="centered", page_icon="👘")

st.markdown("""<style>
    .main-header { display:flex; align-items:center; justify-content:space-between; border-bottom:3px solid #1E3A8A; padding-bottom:10px; margin-bottom:20px; }
    .fusion-title { color:#1E3A8A; font-size:1.6rem; font-weight:800; }
    .word-box { background:white; padding:25px; border-radius:18px; box-shadow:0 8px 20px rgba(0,0,0,0.05); border:1px solid #E5E7EB; margin-bottom:25px; }
    .card-item { border:2px solid #3B82F6; padding:15px; border-radius:12px; margin-bottom:10px; background:#F8FAFC; }
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
user_input = c1.text_input("", placeholder="输入中文词，开启专业日语联想...", label_visibility="collapsed")
search_btn = c2.button("查询", type="primary", use_container_width=True)

if not st.session_state.last_result and not user_input:
    st.info("🌸 您好，我是 FUSION 智能助手。请输入想学习的中文词。")

# 触发逻辑：点击按钮或更换输入时清空旧缓存并检索
if search_btn and user_input:
    st.session_state.last_result = None # 强制清除旧结果，确保数据安全
    
    with st.spinner('FUSION 智能引擎正在为您校对语义...'):
        # 稳健的 Prompt 设计
        prompt = f"Translate '{user_input}' to Japanese. Focus on N4/N5. If '狐狸' then '狐(きつね)', if '大家' then '皆さん'. Return JSON: {{\"word\":\"\", \"reading\":\"\", \"pos\":\"\", \"level\":\"N4/N5\", \"pitch\":\"0\", \"sentences\":[{{\"jp\":\"\", \"kana\":\"\", \"cn\":\"\", \"en\":\"\"}}]}}"
        
        success = False
        for m_name in REDUNDANT_MODELS:
            try:
                comp = client.chat.completions.create(
                    model=m_name,
                    messages=[{"role": "system", "content": "Professional Japanese Teacher. Accuracy is priority."}, {"role": "user", "content": prompt}],
                    temperature=0,
                    response_format={"type": "json_object"}
                )
                res = json.loads(comp.choices[0].message.content)
                res['input_key'] = user_input # 绑定输入，防止错位
                st.session_state.last_result = res
                success = True
                break
            except Exception:
                time.sleep(1.5) # 容错等待
                continue
        
        if not success:
            st.warning("👘 引擎繁忙提醒：由于教学服务器访问人数较多，请在 10 秒后点击“查询”重试。")

# 3. 结果渲染逻辑 (严格匹配输入词)
if st.session_state.last_result and st.session_state.last_result.get('input_key') == user_input:
    r = st.session_state.last_result
    st.markdown("#### 💡 联想结果：")
    
    if r.get('word'):
        st.markdown(f'<div class="word-box"><h2 style="margin:0;color:#1E3A8A;">{r["word"]} ({r.get("reading","")})</h2><div style="color:#3B82F6;">🏷️ {r.get("pos","")} | {r.get("level","")} | 声调:{r.get("pitch","")}</div></div>', unsafe_allow_html=True)
        if st.button("🔊 播放单词音", key="v_main", use_container_width=True):
            st.session_state.audio_config = {"text":r["word"],"slow":False,"key":st.session_state.audio_config["key"]+1}

    sents = r.get('sentences', [])[:3]
    if sents:
        st.markdown("<h3 style='color:#1E3A8A;'>参考文例</h3>", unsafe_allow_html=True)
        for i, s in enumerate(sents, 1):
            st.markdown(f'<div class="card-item"><div style="display:flex;"><div class="idx">{i}</div><div style="flex:1;"><b>{s.get("jp","")}</b><br><span style="font-size:0.85rem;color:#64748B;">{s.get("kana","")}</span><br><span style="color:#059669;">🇨🇳 {s.get("cn","")}</span></div></div></div>', unsafe_allow_html=True)
            ca, cb = st.columns(2)
            if ca.button(f"🟢 标准速 {i}", key=f"n_{i}", use_container_width=True): 
                st.session_state.audio_config = {"text":s.get("jp"),"slow":False,"key":st.session_state.audio_config["key"]+1}
            if cb.button(f"🔴 慢速 {i}", key=f"s_{i}", use_container_width=True): 
                st.session_state.audio_config = {"text":s.get("jp"),"slow":True,"key":st.session_state.audio_config["key"]+1}

# 4. 发音
if st.session_state.audio_config["text"]:
    aud = get_audio(st.session_state.audio_config["text"], st.session_state.audio_config["slow"])
    if aud: st.audio(aud, format="audio/mp3", autoplay=True)
