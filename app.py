import streamlit as st
from groq import Groq
import json
from gtts import gTTS
import io

# 1. 核心配置与样式 (极致去框 + 3px粗边框色阶)
API_KEY = "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"
client = Groq(api_key=API_KEY)

st.markdown("""<style>
    .header-container { display:flex; align-items:center; justify-content:space-between; border-bottom:3px solid #1E3A8A; padding-bottom:10px; margin-bottom:20px; }
    .fusion-banner { color:#1E3A8A; font-size:1.8rem; font-weight:800; }
    .word-box { background:white; padding:25px; border-radius:18px; box-shadow:0 8px 20px rgba(0,0,0,0.05); border:1px solid #E5E7EB; margin-bottom:20px; }
    .card-1 { background:#DBEafe; border:3px solid #3B82F6; padding:15px; border-radius:12px; margin-bottom:10px; }
    .card-2 { background:#EFF6FF; border:3px solid #60A5FA; padding:15px; border-radius:12px; margin-bottom:10px; }
    .card-3 { background:#F8FAFC; border:3px solid #93C5FD; padding:15px; border-radius:12px; margin-bottom:10px; }
    .idx { background:#1E3A8A; color:white; width:26px; height:26px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; font-weight:bold; margin-right:10px; }
    .stAudio { display:none; }
</style>""", unsafe_allow_html=True)

if "audio_config" not in st.session_state: st.session_state.audio_config = {"text": None, "slow": False, "key": 0}
if "last_result" not in st.session_state: st.session_state.last_result = None

def get_audio(text, slow=False):
    if not text: return None
    try:
        tts = gTTS(text=text, lang='ja', slow=slow)
        fp = io.BytesIO(); tts.write_to_fp(fp); fp.seek(0)
        return fp
    except: return None

# 2. 头部视觉 (和服少女 👘)
st.markdown('<div class="header-container"><div class="fusion-banner">FUSION 智能化日语学习系统 1.0</div><div style="font-size:35px;">👘</div></div>', unsafe_allow_html=True)

# 搜索组件
c1, c2 = st.columns([4, 1])
with c1: user_input = st.text_input("", placeholder="输入中文词，开启专业日语联想...", label_visibility="collapsed")
with c2: search_btn = st.button("查询", type="primary", use_container_width=True)

# 初始界面逻辑
target = user_input
if not st.session_state.last_result and not user_input:
    st.info("🌸 你好，我是FUSION 智能语言小助手，请多多关照。")
    target = "你好"

if target:
    if not st.session_state.last_result or st.session_state.last_result.get('input') != target:
        with st.spinner('检索中...'):
            try:
                p = f"Translate '{target}' to Japanese. Hallucination forbidden (鸭=アヒル). Return JSON: {{'word':'Kanji','reading':'Kana','pos':'part','level':'N3','pitch':'0','sentences':[{{'jp':'S1','kana':'K1','cn':'C1','en':'E1'}},{{'jp':'S2','kana':'K2','cn':'C2','en':'E2'}},{{'jp':'S3','kana':'K3','cn':'C3','en':'E3'}}]}}"
                comp = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role":"system","content":"Dict expert. Must provide exactly 3 sentences in the list."}, {"role":"user","content":p}],
                    temperature=0, response_format={"type":"json_object"}
                )
                res = json.loads(comp.choices[0].message.content)
                res['input'] = target
                st.session_state.last_result = res
                if user_input: st.session_state.audio_config = {"text":"これについて、以下の日本語が考えられます。","slow":False,"key":999}
            except: st.error("连接异常")

# 3. 动态渲染 (物理除框版)
if st.session_state.last_result:
    r = st.session_state.last_result
    st.markdown("#### 💡 これについて、以下の日本語が考えられます。")
    
    # 核心单词卡片
    wd = r.get('word','').strip()
    if wd and wd != "()":
        st.markdown(f'<div class="word-box"><h2 style="margin:0;color:#1E3A8A;">{wd} ({r.get("reading","")})</h2><div style="color:#3B82F6;">🏷️ {r.get("pos","")} | {r.get("level","")} | 声调:{r.get("pitch","")}</div></div>', unsafe_allow_html=True)
        if st.button("🔊 播放单词词", key="v_main", use_container_width=True):
            st.session_state.audio_config = {"text":wd,"slow":False,"key":st.session_state.audio_config["key"]+1}

    # 3例句卡片渲染 (严格执行3次循环)
    sents = r.get('sentences', [])
    if sents:
        st.markdown("<h3 style='color:#1E3A8A;margin-top:20px;'>参考文例 (3つの例文)</h3>", unsafe_allow_html=True)
        # 使用 min 确保不会越界，同时保证尝试渲染3个
        for i in range(min(len(sents), 3)):
            s = sents[i]
            st.markdown(f'<div class="card-{i+1}"><div style="display:flex;"><div class="idx">{i+1}</div><div style="flex:1;"><div style="font-size:1.1rem;font-weight:bold;">{s.get("jp","")}</div><div style="color:#666;font-size:0.85rem;">{s.get("kana","")}</div><div style="color:#059669;font-weight:500;">🇨🇳 {s.get("cn","")}</div><div style="color:#2563EB;font-size:0.8rem;">🇺🇸 {s.get("en","")}</div></div></div></div>', unsafe_allow_html=True)
            
            # 使用列表解构来确保 columns 的稳定性
            cols = st.columns([1, 1])
            if cols[0].button(f"🟢 标准速", key=f"n_{i}", use_container_width=True):
                st.session_state.audio_config = {"text":s.get("jp"),"slow":False,"key":st.session_state.audio_config["key"]+1}
            if cols[1].button(f"🔴 慢速", key=f"s_{i}", use_container_width=True):
                st.session_state.audio_config = {"text":s.get("jp"),"slow":True,"key":st.session_state.audio_config["key"]+1}

# 4. 全局发音
if st.session_state.audio_config["text"]:
    aud = get_audio(st.session_state.audio_config["text"], st.session_state.audio_config["slow"])
    if aud: st.audio(aud, format="audio/mp3", autoplay=True)
