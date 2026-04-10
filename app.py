import streamlit as st
from openai import OpenAI
import json
from gtts import gTTS
import io

# --- 1. NHK 标准与极速响应引擎 ---
def get_fusion_fast_pro(user_input):
    # 极简指令，减少 Token 消耗，并强制锁定 NHK 播音级语法
    prompt = f"NHK Style Translate '{user_input}' to JP (N4/N5). JSON only: {{\"word\":\"\",\"reading\":\"\",\"pos\":\"\",\"level\":\"N4/N5\",\"pitch\":\"\",\"sentences\":[{{\"jp\":\"\",\"kana\":\"\",\"cn\":\"\"}},{{\"jp\":\"\",\"kana\":\"\",\"cn\":\"\"}},{{\"jp\":\"\",\"kana\":\"\",\"cn\":\"\"}}]}}"
    
    try:
        # 使用您在 Secrets 中配置的商业 Key
        client = OpenAI(
            api_key=st.secrets["NEW_API_KEY"], 
            base_url=st.secrets["NEW_BASE_URL"]
        )
        comp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0, # 降低随机性，提升生成速度
            timeout=6.0
        )
        return json.loads(comp.choices[0].message.content)
    except Exception as e:
        return None

# --- 2. 界面极致压缩布局设计 ---
st.set_page_config(page_title="FUSION Pro", layout="centered")

st.markdown("""<style>
    /* 标题栏紧凑化 */
    .header-box { border-bottom:2px solid #1E3A8A; padding:5px 0; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center; }
    
    /* 引导语样式 */
    .guide-box { font-size:0.9rem; font-weight:bold; color:#1E3A8A; margin:8px 0; border-left: 4px solid #3B82F6; padding-left:8px; }
    
    /* 核心优化：主方块高度大幅压缩 */
    .word-box { background:white; padding:10px 15px; border-radius:10px; box-shadow:0 2px 8px rgba(0,0,0,0.05); border:1px solid #E5E7EB; text-align:center; margin-bottom:8px; }
    
    /* 例句卡片紧凑化 */
    .card-item { border:1.5px solid #3B82F6; padding:10px; border-radius:8px; margin-bottom:6px; background:#F8FAFC; border-left: 5px solid #1E3A8A; }
    
    /* 数字图标微调 */
    .idx { background:#1E3A8A; color:white; width:18px; height:18px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; font-weight:bold; margin-right:6px; font-size:10px; }
    
    /* 隐藏默认音频控件 */
    .stAudio { display:none; }
    
    /* 按钮样式微调 */
    .stButton>button { padding: 2px 10px; font-size: 0.85rem; height: auto; }
</style>""", unsafe_allow_html=True)

if "audio_text" not in st.session_state: st.session_state.audio_text = None
if "res_cache" not in st.session_state: st.session_state.res_cache = None

# 顶栏
st.markdown('<div class="header-box"><span style="color:#1E3A8A;font-size:1.2rem;font-weight:bold;">FUSION 智能化日语助手 Pro</span><span>👘</span></div>', unsafe_allow_html=True)

# 输入框
u_in = st.text_input("", placeholder="输入词汇，开启专业日语学习...", label_visibility="collapsed")

# 初始页面内容（解决打开页面空白的问题）
if not u_in and not st.session_state.res_cache:
    st.info("🌸 您好，我是 FUSION 智能助手。请输入中文词汇，我会为您提供 NHK 标准级的日语翻译与例句。")

# 触发查询
if u_in and (not st.session_state.res_cache or st.session_state.res_cache.get('q') != u_in):
    with st.spinner('NHK 标准检索中...'):
        res = get_fusion_fast_pro(u_in)
        if res:
            res['q'] = u_in
            st.session_state.res_cache = res
            # 设置初始自动播报：引导语 + 单词
            st.session_state.audio_text = f"これについて、以下の日本語が考えられます。{res['word']}"

# 渲染查询结果
if st.session_state.res_cache and st.session_state.res_cache.get('q') == u_in:
    r = st.session_state.res_cache
    st.markdown(f'<div class="guide-box">💡 これについて、以下の日本語が考えられます。</div>', unsafe_allow_html=True)
    
    # 极致压缩后的主词条
    st.markdown(f"""
    <div class="word-box">
        <h3 style="margin:0;color:#1E3A8A;font-size:1.6rem;">{r.get('word')}</h3>
        <p style="margin:2px 0;color:#3B82F6;font-size:1.1rem;font-weight:bold;">【{r.get('reading')}】</p>
        <p style="color:#64748B;font-size:0.75rem;margin:0;">🏷️ {r.get('pos')} | {r.get('level')} | 声调:{r.get('pitch')}</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button(f"🔊 重新播放单词音", use_container_width=True):
        st.session_state.audio_text = f"これについて、以下の日本語が考えられます。{r['word']}"

    # 3个标准例句展示
    for i, s in enumerate(r.get('sentences', []), 1):
        st.markdown(f'<div class="card-item"><b><span class="idx">{i}</span>{s.get("jp")}</b><br><span style="color:#64748B;font-size:0.75rem;margin-left:24px;">{s.get("kana")}</span><br><span style="color:#059669;margin-left:24px;font-size:0.8rem;">🇨🇳 {s.get("cn")}</span></div>', unsafe_allow_html=True)
        ca, cb = st.columns(2)
        if ca.button(f"🟢 标准速 {i}", key=f"n_{i}", use_container_width=True): 
            st.session_state.audio_text = s.get("jp")
        if cb.button(f"🔴 慢速 {i}", key=f"s_{i}", use_container_width=True): 
            st.session_state.audio_text = s.get("jp")

# --- 极速发音核心逻辑 ---
if st.session_state.audio_text:
    try:
        # 强制 lang='ja' 确保东京标准音
        tts = gTTS(text=st.session_state.audio_text, lang='ja')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        st.audio(fp, format="audio/mp3", autoplay=True)
        # 播完重置状态
        st.session_state.audio_text = None
    except:
        pass
