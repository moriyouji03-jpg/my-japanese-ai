import streamlit as st
from openai import OpenAI
import json
from gtts import gTTS
import io

# --- 1. NHK 级别：极致语义引擎 ---
def get_fusion_nhk_standard(user_input):
    # 设定 NHK 播音级指令
    prompt = f"""
    Role: Senior Japanese Translator & NHK News Anchor.
    Task: Translate Chinese '{user_input}' to Standard Japanese (JLPT N4/N5).
    Requirements:
    - Grammar must be 100% correct (Standard Tokyo dialect).
    - Provide EXACTLY 3 natural, high-quality example sentences.
    - Pitch accent should be accurate (e.g., 平坦, 頭高, 中高).
    JSON Format:
    {{
      "word": "汉字",
      "reading": "平假名",
      "pos": "词性",
      "level": "N4/N5",
      "pitch": "声调类型",
      "sentences": [
        {{"jp": "句子", "kana": "全假名", "cn": "中文翻译"}}
      ]
    }}
    """
    try:
        client = OpenAI(api_key=st.secrets["NEW_API_KEY"], base_url=st.secrets["NEW_BASE_URL"])
        comp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(comp.choices[0].message.content)
    except:
        return None

# --- 2. 界面美学与交互设计 ---
st.set_page_config(page_title="FUSION Pro", layout="centered")

st.markdown("""<style>
    .header-box { border-bottom:2px solid #1E3A8A; padding:5px 0; margin-bottom:15px; display:flex; justify-content:space-between; align-items:center; }
    .guide-box { font-size:1rem; font-weight:bold; color:#1E3A8A; margin:10px 0; border-left: 4px solid #3B82F6; padding-left:10px; }
    .word-box { background:white; padding:15px; border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.05); border:1px solid #E5E7EB; text-align:center; margin-bottom:10px; }
    .card-item { border:1.5px solid #3B82F6; padding:12px; border-radius:8px; margin-bottom:8px; background:#F8FAFC; border-left: 5px solid #1E3A8A; }
    .idx { background:#1E3A8A; color:white; width:20px; height:20px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; font-weight:bold; margin-right:8px; font-size:11px; }
    .stAudio { display:none; }
</style>""", unsafe_allow_html=True)

if "audio_text" not in st.session_state: st.session_state.audio_text = None
if "res_cache" not in st.session_state: st.session_state.res_cache = None

st.markdown('<div class="header-box"><span style="color:#1E3A8A;font-size:1.3rem;font-weight:bold;">FUSION 智能化日语助手 Pro</span><span>👘</span></div>', unsafe_allow_html=True)

u_in = st.text_input("", placeholder="输入词汇，开启专业日语联想...", label_visibility="collapsed")

# 初始加载逻辑：解决截图2的空旷感
if not u_in and not st.session_state.res_cache:
    st.info("🌸 您好，我是 FUSION 智能语言小助手，请多多关照。")
    # 默认显示一个欢迎界面或引导
    st.markdown('<p class="guide-box">💡 这里可以展示您的日语联想内容：</p>', unsafe_allow_html=True)

# 查询逻辑
if u_in and (not st.session_state.res_cache or st.session_state.res_cache.get('q') != u_in):
    with st.spinner('FUSION 商业引擎正在进行 NHK 标准化处理...'):
        res = get_fusion_nhk_standard(u_in)
        if res:
            res['q'] = u_in
            st.session_state.res_cache = res
            # 强化日语音频判断
            st.session_state.audio_text = f"これについて、以下の日本語が考えられます。{res['word']}"

# 结果渲染
if st.session_state.res_cache:
    r = st.session_state.res_cache
    st.markdown(f'<div class="guide-box">💡 これについて、以下の日本語が考えられます。</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="word-box">
        <h2 style="margin:0;color:#1E3A8A;font-size:2rem;">{r.get('word')}</h2>
        <h4 style="margin:4px 0;color:#3B82F6;font-weight:normal;">【{r.get('reading')}】</h4>
        <p style="color:#64748B;font-size:0.85rem;margin:0;">🏷️ {r.get('pos')} | {r.get('level')} | 声调:{r.get('pitch')}</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button(f"🔊 重新播报引导语和单词", use_container_width=True):
        st.session_state.audio_text = f"これについて、以下の日本語が考えられます。{r['word']}"

    for i, s in enumerate(r.get('sentences', []), 1):
        st.markdown(f'<div class="card-item"><b><span class="idx">{i}</span>{s.get("jp")}</b><br><span style="color:#64748B;font-size:0.8rem;margin-left:28px;">{s.get("kana")}</span><br><span style="color:#059669;margin-left:28px;font-size:0.85rem;">🇨🇳 {s.get("cn")}</span></div>', unsafe_allow_html=True)
        ca, cb = st.columns(2)
        if ca.button(f"🟢 标准速 {i}", key=f"n_{i}", use_container_width=True): 
            st.session_state.audio_text = s.get("jp")
        if cb.button(f"🔴 慢速 {i}", key=f"s_{i}", use_container_width=True): 
            st.session_state.audio_text = s.get("jp")

# 发音处理
if st.session_state.audio_text:
    try:
        # 强制指定日语环境进行语音合成
        tts = gTTS(text=st.session_state.audio_text, lang='ja', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        st.audio(fp, format="audio/mp3", autoplay=True)
        st.session_state.audio_text = None
    except: pass
