import streamlit as st
from openai import OpenAI
import json
from gtts import gTTS
import io

# --- 1. 商业级：极速精准语义引擎 ---
def get_fusion_business_pro(user_input):
    # 强制锁定语境，解决“工作”变“工作”的痛点
    prompt = f"""
    Translate Chinese '{user_input}' to Japanese.
    Context: Daily & Business Japanese for JLPT N4/N5 learners.
    Rules:
    - Avoid literal kanji translation if more common words exist (e.g., '工作' -> '仕事', NOT '工作').
    - Prioritize Kun-yomi (訓読み).
    Output JSON ONLY:
    {{
      "word": "汉字",
      "reading": "平假名",
      "pos": "词性",
      "level": "N4/N5",
      "pitch": "声调",
      "sentences": [
        {{"jp": "句子", "kana": "假名标注", "cn": "翻译"}}
      ]
    }}
    """
    
    try:
        client = OpenAI(
            api_key=st.secrets["NEW_API_KEY"],
            base_url=st.secrets["NEW_BASE_URL"]
        )
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        st.error("服务调度中，请稍候...")
        return None

# --- 2. 界面渲染与极致自动化 ---
st.set_page_config(page_title="FUSION Pro", layout="centered", page_icon="👘")

st.markdown("""<style>
    .header-box { border-bottom:3px solid #1E3A8A; padding:10px 0; margin-bottom:20px; display:flex; justify-content:space-between; align-items:center; }
    .guide-box { font-size:1.1rem; font-weight:bold; color:#1E3A8A; margin:15px 0; display:flex; align-items:center; }
    .word-box { background:white; padding:25px; border-radius:18px; box-shadow:0 8px 20px rgba(0,0,0,0.05); border:1px solid #E5E7EB; text-align:center; margin-bottom:20px; }
    .card-item { border:2px solid #3B82F6; padding:15px; border-radius:12px; margin-bottom:10px; background:#F8FAFC; }
    .idx { background:#1E3A8A; color:white; width:22px; height:22px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; font-weight:bold; margin-right:8px; font-size:12px; }
    .stAudio { display:none; }
</style>""", unsafe_allow_html=True)

if "audio_config" not in st.session_state: st.session_state.audio_config = {"text": None, "key": 0}
if "last_res" not in st.session_state: st.session_state.last_res = None

# 标题对齐
st.markdown('<div class="header-box"><span style="color:#1E3A8A;font-size:1.6rem;font-weight:bold;">FUSION 智能化日语助手 Pro</span><span>👘</span></div>', unsafe_allow_html=True)

u_in = st.text_input("", placeholder="输入中文词汇 (例如：工作)...", label_visibility="collapsed")

if st.button("查询", type="primary", use_container_width=True) and u_in:
    with st.spinner('FUSION 商业引擎正在全力检索...'):
        res = get_fusion_business_pro(u_in)
        if res:
            res['q'] = u_in
            st.session_state.last_res = res
            # --- 核心优化：查询成功立即自动播放“引导语+单词” ---
            guide_txt = "これについて、以下の日本語が考えられます。"
            st.session_state.audio_config = {
                "text": f"{guide_txt} {res['word']}", 
                "key": st.session_state.audio_config["key"]+1
            }

if st.session_state.last_res and st.session_state.last_res.get('q') == u_in:
    r = st.session_state.last_res
    st.markdown(f'<div class="guide-box">💡 これについて、以下の日本語が考えられます。</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="word-box">
        <h1 style="margin:0;color:#1E3A8A;font-size:2.8rem;">{r.get('word')}</h1>
        <h3 style="margin:5px 0;color:#3B82F6;font-weight:normal;">【{r.get('reading')}】</h3>
        <p style="color:#64748B;font-size:0.9rem;">🏷️ {r.get('pos')} | {r.get('level')} | 声调:{r.get('pitch')}</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button(f"🔊 重新播放主单词发音", key="v_main", use_container_width=True):
        st.session_state.audio_config = {"text": f"これについて、以下の日本語が考えられます。 {r['word']}", "key": st.session_state.audio_config["key"]+1}

    for i, s in enumerate(r.get('sentences', []), 1):
        st.markdown(f'<div class="card-item"><b><span class="idx">{i}</span>{s.get("jp")}</b><br><span style="color:#64748B;font-size:0.85rem;margin-left:30px;">{s.get("kana")}</span><br><span style="color:#059669;margin-left:30px;">🇨🇳 {s.get("cn")}</span></div>', unsafe_allow_html=True)
        ca, cb = st.columns(2)
        if ca.button(f"🟢 标准速 {i}", key=f"n_{i}", use_container_width=True): 
            st.session_state.audio_config = {"text": s.get("jp"), "key": st.session_state.audio_config["key"]+1}
        if cb.button(f"🔴 慢速 {i}", key=f"s_{i}", use_container_width=True): 
            st.session_state.audio_config = {"text": s.get("jp"), "key": st.session_state.audio_config["key"]+1}

# 发音核心逻辑
if st.session_state.audio_config["text"]:
    try:
        tts = gTTS(text=st.session_state.audio_config["text"], lang='ja')
        fp = io.BytesIO(); tts.write_to_fp(fp); fp.seek(0)
        st.audio(fp, format="audio/mp3", autoplay=True)
        st.session_state.audio_config["text"] = None # 播完即清空，防止循环播放
    except: pass
