import streamlit as st
from openai import OpenAI
import json
from gtts import gTTS
import io

# --- 1. 顶流专家级：深度语义重构引擎 ---
def get_fusion_professional_ultimate(user_input):
    # 强制执行：跳出汉字陷阱，追求母语级表达
    prompt = f"""
    You are a Japanese Native Expert (NHK level). 
    Translate the meaning of the Chinese phrase '{user_input}' into authentic Japanese.
    
    CRITICAL RULES:
    1. WORD FIELD: Use ONLY standard Japanese words (Gairaigo, Wago, or Kango used in Japan). 
    2. NO CHINESE IDIOMS: Never use '名落孙山' or similar fake kanji. If user says '名落孙山', you MUST output '不合格' or '落第'.
    3. JAPANESE ONLY: The "word" must be a word that exists in the NHK dictionary.
    4. ACCURACY: Provide 3 high-quality sentences with pitch accents.
    
    JSON format:
    {{
      "word": "Standard Japanese word (NEVER direct copy of Chinese)",
      "reading": "hiragana",
      "pos": "part of speech",
      "level": "N4/N5",
      "pitch": "pitch accent",
      "sentences": [
        {{"jp": "sentence", "kana": "reading", "cn": "chinese"}}
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
            messages=[{"role": "system", "content": "You are a professional Japanese translator. You hate literal translations."},
                      {"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0, 
            timeout=10.0
        )
        return json.loads(comp.choices[0].message.content)
    except:
        return None

# --- 2. 极致紧凑布局 ---
st.set_page_config(page_title="FUSION Pro", layout="centered")

st.markdown("""<style>
    .header-box { border-bottom:2px solid #1E3A8A; padding:5px 0; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center; }
    .guide-box { font-size:0.9rem; font-weight:bold; color:#1E3A8A; margin:8px 0; border-left: 4px solid #3B82F6; padding-left:8px; }
    .word-box { background:white; padding:12px; border-radius:10px; box-shadow:0 2px 8px rgba(0,0,0,0.05); border:1px solid #E5E7EB; text-align:center; margin-bottom:8px; }
    .card-item { border:1.5px solid #3B82F6; padding:10px; border-radius:8px; margin-bottom:6px; background:#F8FAFC; border-left: 5px solid #1E3A8A; }
    .idx { background:#1E3A8A; color:white; width:18px; height:18px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; font-weight:bold; margin-right:6px; font-size:10px; }
    .stAudio { display:none; }
</style>""", unsafe_allow_html=True)

# 初始全页面种子数据
WELCOME_DATA = {
    "word": "こんにちは", "reading": "こんにちは", "pos": "感嘆詞", "level": "N5", "pitch": "平板",
    "sentences": [
        {"jp": "皆さん、こんにちは。お会いできて嬉しいです。", "kana": "みなさん、こんにちは。おあいできてうれしいです。", "cn": "大家好，很高兴见到大家。"},
        {"jp": "日本語の学習を一緒に楽しみましょう。", "kana": "にほんごのがくしゅうをいっしょにたのしみましょう。", "cn": "让我们一起享受日语学习的乐趣吧。"},
        {"jp": "何か質問があれば、いつでも聞いてください。", "kana": "なにかしつもんがあれば、いつでもきいてください。", "cn": "如果有任何问题，请随时提问。"}
    ]
}

if "audio_text" not in st.session_state: st.session_state.audio_text = None
if "res_cache" not in st.session_state: st.session_state.res_cache = None

st.markdown('<div class="header-box"><span style="color:#1E3A8A;font-size:1.2rem;font-weight:bold;">FUSION 智能化日语助手 Pro</span><span>👘</span></div>', unsafe_allow_html=True)

u_in = st.text_input("", placeholder="请输入词汇...", label_visibility="collapsed")

if u_in:
    if not st.session_state.res_cache or st.session_state.res_cache.get('q') != u_in:
        with st.spinner('FUSION 专家引擎正在进行深度语义重构...'):
            res = get_fusion_professional_ultimate(u_in)
            if res:
                res['q'] = u_in
                st.session_state.res_cache = res
                st.session_state.audio_text = f"これについて、以下の日本語が考えられます。{res['word']}"
    display_data = st.session_state.res_cache
else:
    display_data = WELCOME_DATA

if display_data:
    st.markdown(f'<div class="guide-box">💡 これについて、以下の日本語が考えられます。</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="word-box">
        <h3 style="margin:0;color:#1E3A8A;font-size:1.5rem;">{display_data.get('word')}</h3>
        <p style="margin:2px 0;color:#3B82F6;font-size:1.1rem;font-weight:bold;">【{display_data.get('reading')}】</p>
        <p style="color:#64748B;font-size:0.75rem;margin:0;">🏷️ {display_data.get('pos')} | {display_data.get('level')} | 声调:{display_data.get('pitch')}</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button(f"🔊 重新播放单词音频", use_container_width=True):
        st.session_state.audio_text = f"これについて、以下の日本語が考えられます。{display_data['word']}"

    for i, s in enumerate(display_data.get('sentences', []), 1):
        st.markdown(f'<div class="card-item"><b><span class="idx">{i}</span>{s.get("jp")}</b><br><span style="color:#64748B;font-size:0.75rem;margin-left:24px;">{s.get("kana")}</span><br><span style="color:#059669;margin-left:24px;font-size:0.8rem;">🇨🇳 {s.get("cn")}</span></div>', unsafe_allow_html=True)
        ca, cb = st.columns(2)
        if ca.button(f"🟢 标准速 {i}", key=f"n_{i}", use_container_width=True): 
            st.session_state.audio_text = s.get("jp")
        if cb.button(f"🔴 慢速 {i}", key=f"s_{i}", use_container_width=True): 
            st.session_state.audio_text = s.get("jp")

if st.session_state.audio_text:
    try:
        tts = gTTS(text=st.session_state.audio_text, lang='ja')
        fp = io.BytesIO(); tts.write_to_fp(fp); fp.seek(0)
        st.audio(fp, format="audio/mp3", autoplay=True)
        st.session_state.audio_text = None
    except: pass
