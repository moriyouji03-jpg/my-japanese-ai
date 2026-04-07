import streamlit as st
from groq import Groq
import json
from gtts import gTTS
import io

# 1. 配置与样式
API_KEY = "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"
client = Groq(api_key=API_KEY)

st.markdown("""<style>
    .header-container { display:flex; align-items:center; justify-content:space-between; border-bottom:3px solid #1E3A8A; padding-bottom:10px; margin-bottom:20px; }
    .fusion-banner { color:#1E3A8A; font-size:1.4rem; font-weight:800; }
    .word-box { background:white; padding:20px; border-radius:15px; box-shadow:0 8px 20px rgba(0,0,0,0.05); border:1px solid #E5E7EB; margin-bottom:20px; }
    .card-1 { background:#DBEafe; border:3px solid #3B82F6; padding:15px; border-radius:12px; margin-bottom:10px; }
    .card-2 { background:#EFF6FF; border:3px solid #60A5FA; padding:15px; border-radius:12px; margin-bottom:10px; }
    .card-3 { background:#F8FAFC; border:3px solid #93C5FD; padding:15px; border-radius:12px; margin-bottom:10px; }
    .idx { background:#1E3A8A; color:white; width:26px; height:26px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; font-weight:bold; margin-right:10px; }
    /* 移动端优化：放大按钮点击区域 */
    .stButton>button { height: 3em; font-weight: bold; }
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

# 2. 头部视觉 (和服少女👘)
st.markdown('<div class="header-container"><div class="fusion-banner">FUSION 智能化日语学习助手 1.0</div><div style="font-size:30px;">👘</div></div>', unsafe_allow_html=True)

c1, c2 = st.columns([3, 1])
with c1: user_input = st.text_input("", placeholder="输入中文...", label_visibility="collapsed")
with c2: search_btn = st.button("查询", type="primary", use_container_width=True)

target = user_input
if not st.session_state.last_result and not user_input:
    st.info("🌸 你好，我是FUSION 智能语言小助手，请多多关照。")
    target = "你好"

if target:
    if not st.session_state.last_result or st.session_state.last_result.get('input') != target:
        with st.spinner('检索中...'):
            try:
                p = f"Translate '{target}' to Japanese. JSON: {{'word':'','reading':'','pos':'','level':'N4/N5','pitch':'0','sentences':[{{'jp':'','kana':'','cn':'','en':''}}]}}"
                comp = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": "You are a Japanese dictionary. Accurate translation."}, {"role": "user", "content": p}],
                    temperature=0, response_format={"type": "json_object"}
                )
                res = json.loads(comp.choices[0].message.content)
                res['input'] = target
                st.session_state.last_result = res
                # 移动端建议：取消进入时的自动播放，改为由用户触发，或者仅在点击查询后播放
                if user_input: st.session_state.audio_config = {"text":"これについて、以下の日本語が考えられます。","slow":False,"key":999}
            except: st.error("网络波动")

# 3. 渲染逻辑
if st.session_state.last_result:
    r = st.session_state.last_result
    st.markdown("#### 💡 结果如下：")
    wd = r.get('word','').strip()
    if wd and wd != "()":
        st.markdown(f'<div class="word-box"><h2 style="margin:0;color:#1E3A8A;">{wd} ({r.get("reading","")})</h2><div style="color:#3B82F6;">🏷️ {r.get("pos","")} | {r.get("level","")} | 声调:{r.get("pitch","")}</div></div>', unsafe_allow_html=True)
        if st.button("🔊 点击播放单词", key="v_main", use_container_width=True):
            st.session_state.audio_config = {"text":wd,"slow":False,"key":st.session_state.audio_config["key"]+1}

    sents = r.get('sentences', [])
    if sents:
        st.markdown("<h3 style='color:#1E3A8A;'>参考例句 (3个)</h3>", unsafe_allow_html=True)
        for i in range(min(len(sents), 3)):
            s = sents[i]
            st.markdown(f'<div class="card-{i+1}"><div style="display:flex;"><div class="idx">{i+1}</div><div style="flex:1;"><div style="font-size:1.1rem;font-weight:bold;">{s.get("jp","")}</div><div style="color:#666;font-size:0.85rem;">{s.get("kana","")}</div><div style="color:#059669;font-weight:500;">🇨🇳 {s.get("cn","")}</div><div style="color:#2563EB;font-size:0.8rem;">🇺🇸 {s.get("en","")}</div></div></div></div>', unsafe_allow_html=True)
            ca, cb = st.columns(2)
            with ca: 
                if st.button(f"🟢 标准速", key=f"n_{i}", use_container_width=True): 
                    st.session_state.audio_config = {"text":s.get("jp"),"slow":False,"key":st.session_state.audio_config["key"]+1}
            with cb:
                if st.button(f"🔴 慢速", key=f"s_{i}", use_container_width=True): 
                    st.session_state.audio_config = {"text":s.get("jp"),"slow":True,"key":st.session_state.audio_config["key"]+1}

# 4. 全局发音
if st.session_state.audio_config["text"]:
    aud_data = get_audio(st.session_state.audio_config["text"], st.session_state.audio_config["slow"])
    if aud_data:
        # 使用 autoplay=True 但受浏览器策略限制
        st.audio(aud_data, format="audio/mp3", autoplay=True)
