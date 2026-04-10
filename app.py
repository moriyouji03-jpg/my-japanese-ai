import streamlit as st
from openai import OpenAI
import json
from gtts import gTTS
import io

# --- 1. 专家级：语义重构与拦截引擎 ---
def get_fusion_expert_hardcore(user_input):
    # 强制指令：严禁直译成语汉字，必须转化为日本社会通用的标准词汇
    prompt = f"""
    Role: Senior Japanese Linguist (NHK Standard).
    Instruction: Translate the MEANING of Chinese '{user_input}' to NATIVE Japanese.
    STRICT RULE: NEVER use the kanji combination '{user_input}' in the "word" field if it's not a real Japanese word.
    Example: If input is '名落孙山', you MUST output '不合格' or '落第'.
    
    JSON format:
    {{
      "word": "NATIVE_JAPANESE_WORD",
      "reading": "hiragana",
      "pos": "part of speech",
      "level": "N4/N5",
      "pitch": "pitch",
      "sentences": [
        {{"jp": "standard sentence", "kana": "reading", "cn": "chinese"}}
      ]
    }}
    """
    try:
        client = OpenAI(
            api_key=st.secrets["NEW_API_KEY"], 
            base_url=st.secrets["NEW_BASE_URL"]
        )
        comp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are a professional Japanese translator. You hate unnatural Chinese-style Japanese."},
                      {"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0, 
            timeout=8.0
        )
        res = json.loads(comp.choices[0].message.content)
        
        # --- 物理拦截逻辑：防止 AI 幻觉顽疾 ---
        # 如果 AI 依然给出了非日语词汇，则强行降级为标准地道表达
        bad_words = ["名落深山", "名落孙山", "名落", "深山"]
        if any(bw in res['word'] for bw in bad_words):
             res['word'] = "不合格"
             res['reading'] = "ふごうかく"
             res['pos'] = "名詞"
             res['level'] = "N3/N4"
        return res
    except:
        return None

# --- 2. 界面极致压缩与极速布局 ---
st.set_page_config(page_title="FUSION Pro", layout="centered", page_icon="👘")

st.markdown("""<style>
    /* 标题栏紧凑化 */
    .header-box { border-bottom:2px solid #1E3A8A; padding:5px 0; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center; }
    
    /* 引导语样式 */
    .guide-box { font-size:0.9rem; font-weight:bold; color:#1E3A8A; margin:8px 0; border-left: 4px solid #3B82F6; padding-left:8px; }
    
    /* 极致压缩主方块高度 */
    .word-box { background:white; padding:10px 15px; border-radius:10px; box-shadow:0 2px 8px rgba(0,0,0,0.05); border:1px solid #E5E7EB; text-align:center; margin-bottom:8px; }
    
    /* 例句卡片紧凑设计 */
    .card-item { border:1.5px solid #3B82F6; padding:8px 10px; border-radius:8px; margin-bottom:5px; background:#F8FAFC; border-left: 5px solid #1E3A8A; }
    
    /* 数字图标微调 */
    .idx { background:#1E3A8A; color:white; width:18px; height:18px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; font-weight:bold; margin-right:6px; font-size:10px; }
    
    /* 隐藏默认控件 */
    .stAudio { display:none; }
    .stButton>button { padding: 2px 10px; font-size: 0.8rem; height: auto; }
</style>""", unsafe_allow_html=True)

# 初始种子数据：首屏仪式感
WELCOME_DATA = {
    "word": "こんにちは",
    "reading": "こんにちは",
    "pos": "感嘆詞",
    "level": "N5",
    "pitch": "平板",
    "sentences": [
        {"jp": "皆さん、こんにちは。お会いできて嬉しいです。", "kana": "みなさん、こんにちは。おあいできてうれしいです。", "cn": "大家好，很高兴见到大家。"},
        {"jp": "日本語の学習を一緒に楽しみましょう。", "kana": "にほんごのがくしゅうをいっしょにたのしみましょう。", "cn": "让我们一起享受日语学习的乐趣吧。"},
        {"jp": "何か質問があれば、いつでも聞いてください。", "kana": "なにかしつもんがあれば、いつでもきいてください。", "cn": "如果有任何问题，请随时提问。"}
    ]
}

if "audio_text" not in st.session_state: st.session_state.audio_text = None
if "res_cache" not in st.session_state: st.session_state.res_cache = None

st.markdown('<div class="header-box"><span style="color:#1E3A8A;font-size:1.2rem;font-weight:bold;">FUSION 智能化日语助手 Pro</span><span>👘</span></div>', unsafe_allow_html=True)

# 输入框锁定
u_in = st.text_input("", placeholder="输入中文词汇...", label_visibility="collapsed")

# 核心业务处理
if u_in:
    if not st.session_state.res_cache or st.session_state.res_cache.get('q') != u_in:
        with st.spinner('FUSION 专家引擎加速响应中...'):
            res = get_fusion_expert_hardcore(u_in)
            if res:
                res['q'] = u_in
                st.session_state.res_cache = res
                # --- 关键：回车后直接触发自动播报状态 ---
                st.session_state.audio_text = f"これについて、以下の日本語が考えられます。{res['word']}"
    display_data = st.session_state.res_cache
else:
    display_data = WELCOME_DATA

# 渲染全屏内容
if display_data:
    st.markdown(f'<div class="guide-box">💡 これについて、以下の日本語が考えられます。</div>', unsafe_allow_html=True)
    
    # 极致压缩主词条
    st.markdown(f"""
    <div class="word-box">
        <h3 style="margin:0;color:#1E3A8A;font-size:1.4rem;">{display_data.get('word')}</h3>
        <p style="margin:2px 0;color:#3B82F6;font-size:1.1rem;font-weight:bold;">【{display_data.get('reading')}】</p>
        <p style="color:#64748B;font-size:0.75rem;margin:0;">🏷️ {display_data.get('pos')} | {display_data.get('level')} | 声调:{display_data.get('pitch')}</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button(f"🔊 重新播放单词音频", use_container_width=True):
        st.session_state.audio_text = f"这について、以下の日本語が考えられます。{display_data['word']}"

    # 三条例句始终填充展示
    for i, s in enumerate(display_data.get('sentences', []), 1):
        st.markdown(f'<div class="card-item"><b><span class="idx">{i}</span>{s.get("jp")}</b><br><span style="color:#64748B;font-size:0.75rem;margin-left:24px;">{s.get("kana")}</span><br><span style="color:#059669;margin-left:24px;font-size:0.8rem;">🇨🇳 {s.get("cn")}</span></div>', unsafe_allow_html=True)
        ca, cb = st.columns(2)
        if ca.button(f"🟢 标准速 {i}", key=f"n_{i}", use_container_width=True): 
            st.session_state.audio_text = s.get("jp")
        if cb.button(f"🔴 慢速 {i}", key=f"s_{i}", use_container_width=True): 
            st.session_state.audio_text = s.get("jp")

# --- 极速音频播报 (回车即响) ---
if st.session_state.audio_text:
    try:
        # 强制 lang='ja' 确保东京标准音
        tts = gTTS(text=st.session_state.audio_text, lang='ja')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        st.audio(fp, format="audio/mp3", autoplay=True)
        st.session_state.audio_text = None # 播完重置
    except:
        pass
