import streamlit as st
from groq import Groq
import json
from gtts import gTTS
import io
import time

# 1. 核心安全配置：从 Streamlit Secrets 动态读取您的专属 Key
try:
    if "GROQ_API_KEY" in st.secrets:
        current_api_key = st.secrets["GROQ_API_KEY"]
        client = Groq(api_key=current_api_key)
    else:
        st.error("🔑 秘钥未配置：请在 Streamlit 控制台的 Secrets 中添加 GROQ_API_KEY。")
        st.stop()
except Exception as e:
    st.error(f"🔑 秘钥读取异常，请检查配置：{e}")
    st.stop()

# 定义双模型冗余，确保极致稳定性
MODELS = ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"]

st.set_page_config(page_title="FUSION 日语助手", layout="centered", page_icon="👘")

# 2. FUSION 顶级美学样式表
st.markdown("""<style>
    .main-header { display:flex; align-items:center; justify-content:space-between; border-bottom:3px solid #1E3A8A; padding-bottom:10px; margin-bottom:20px; }
    .fusion-title { color:#1E3A8A; font-size:1.6rem; font-weight:800; }
    .word-box { background:white; padding:25px; border-radius:18px; box-shadow:0 8px 20px rgba(0,0,0,0.05); border:1px solid #E5E7EB; margin-bottom:25px; }
    .card-item { border:2px solid #3B82F6; padding:18px; border-radius:12px; margin-bottom:12px; background:#F8FAFC; }
    .idx { background:#1E3A8A; color:white; width:22px; height:22px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; font-weight:bold; margin-right:8px; font-size:12px; vertical-align:middle; }
    .stAudio { display:none; }
</style>""", unsafe_allow_html=True)

# 状态管理：发音配置与结果持久化
if "audio_config" not in st.session_state: st.session_state.audio_config = {"text": None, "slow": False, "key": 0}
if "last_result" not in st.session_state: st.session_state.last_result = None

def get_audio(text, slow=False):
    try:
        tts = gTTS(text=text, lang='ja', slow=slow)
        fp = io.BytesIO(); tts.write_to_fp(fp); fp.seek(0)
        return fp
    except: return None

# 3. 界面交互区
st.markdown('<div class="main-header"><div class="fusion-title">FUSION 智能化日语学习助手 1.0</div><div style="font-size:35px;">👘</div></div>', unsafe_allow_html=True)

c1, c2 = st.columns([4, 1])
user_input = c1.text_input("", placeholder="输入中文词，获取顶流水平教案...", label_visibility="collapsed")
search_btn = c2.button("查询", type="primary", use_container_width=True)

# 4. 核心逻辑：智能联想与三例句生成
if search_btn and user_input:
    st.session_state.last_result = None # 检索前清理，确保数据安全
    with st.spinner('FUSION 顶流教案生成中...'):
        # 严格约束 Prompt：锁死语义、强制3句、N4/N5级
        prompt = "Identify the most NATURAL Japanese for: '" + user_input + "'. "
        prompt += "CRITICAL RULES:\n"
        prompt += "1. MUST provide EXACTLY 3 example sentences (N4/N5 level).\n"
        prompt += "2. If '狐狸' then '狐(きつね)', If '大家' then '皆さん'.\n"
        prompt += "3. Focus on daily practical usage.\n"
        prompt += "Return JSON: {\"word\":\"\", \"reading\":\"\", \"pos\":\"\", \"level\":\"N4/N5\", \"pitch\":\"0\", \"sentences\":[{\"jp\":\"\", \"kana\":\"\", \"cn\":\"\"}, {\"jp\":\"\", \"kana\":\"\", \"cn\":\"\"}, {\"jp\":\"\", \"kana\":\"\", \"cn\":\"\"}]}"
        
        success = False
        for m in MODELS:
            try:
                comp = client.chat.completions.create(
                    model=m,
                    messages=[{"role": "system", "content": "Professional Japanese Teacher. Precision is life."}, {"role": "user", "content": prompt}],
                    temperature=0, response_format={"type": "json_object"}
                )
                res = json.loads(comp.choices[0].message.content)
                res['input_key'] = user_input
                st.session_state.last_result = res
                success = True
                break
            except Exception:
                time.sleep(1) # 容错避让
                continue
        
        if not success:
            st.error("👘 访问频率触达上限，请稍后再次尝试。")

# 5. 渲染结果：顶流水平的 3 例句展示
if st.session_state.last_result and st.session_state.last_result.get('input_key') == user_input:
    r = st.session_state.last_result
    st.markdown("#### 💡 联想结果：")
    
    # 核心单词卡
    if r.get('word'):
        st.markdown(f'<div class="word-box"><h2 style="margin:0;color:#1E3A8A;">{r["word"]} ({r.get("reading","")})</h2><div style="color:#3B82F6;">🏷️ {r.get("pos","")} | {r.get("level","")} | 声调:{r.get("pitch","")}</div></div>', unsafe_allow_html=True)
        if st.button("🔊 播放单词音", key="v_main", use_container_width=True):
            st.session_state.audio_config = {"text":r["word"],"slow":False,"key":st.session_state.audio_config["key"]+1}

    # 3组精选例句卡
    sents = r.get('sentences', [])
    if sents:
        st.markdown("<h3 style='color:#1E3A8A;margin-top:10px;'>参考文例 (3个)</h3>", unsafe_allow_html=True)
        for i, s in enumerate(sents, 1):
            st.markdown(f'<div class="card-item"><div><b><span class="idx">{i}</span>{s.get("jp","")}</b><br><span style="font-size:0.85rem;color:#64748B;margin-left:30px;">{s.get("kana","")}</span><br><span style="color:#059669;margin-left:30px;">🇨🇳 {s.get("cn","")}</span></div></div>', unsafe_allow_html=True)
            ca, cb = st.columns(2)
            if ca.button(f"🟢 标准速 {i}", key=f"n_{i}", use_container_width=True): 
                st.session_state.audio_config = {"text":s.get("jp"),"slow":False,"key":st.session_state.audio_config["key"]+1}
            if cb.button(f"🔴 慢速 {i}", key=f"s_{i}", use_container_width=True): 
                st.session_state.audio_config = {"text":s.get("jp"),"slow":True,"key":st.session_state.audio_config["key"]+1}

# 6. 全局异步发音引擎
if st.session_state.audio_config["text"]:
    aud = get_audio(st.session_state.audio_config["text"], st.session_state.audio_config["slow"])
    if aud: st.audio(aud, format="audio/mp3", autoplay=True)
