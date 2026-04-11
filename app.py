import streamlit as st
from openai import OpenAI
import json
from gtts import gTTS
import io

# --- 1. 顶流语言专家：地道语义重构引擎 ---
def get_fusion_expert_ultimate(user_input):
    # 强制指令：严禁直译汉字词，必须使用日语母语者公认的单词
    prompt = f"""
    Role: Senior Japanese Editor (NHK Standard).
    Task: Translate MEANING of Chinese '{user_input}' to NATIVE Japanese.
    
    CRITICAL RULES:
    1. WORD: Use ONLY verified Japanese dictionary words. NEVER invent kanji words based on Chinese input.
    2. EXAMPLES: '号召' -> '呼びかける', '名落孙山' -> '落第/不合格', '工作' -> '仕事'.
    3. QUANTITY: Exactly 3 high-quality sentences.
    
    JSON format:
    {{
      "word": "地道日语词汇",
      "reading": "平假名",
      "pos": "词性",
      "level": "N4/N5",
      "pitch": "声调类型",
      "sentences": [
        {{"jp": "标准句子", "kana": "全假名", "cn": "中文翻译"}}
      ]
    }}
    """
    try:
        client = OpenAI(api_key=st.secrets["NEW_API_KEY"], base_url=st.secrets["NEW_BASE_URL"])
        comp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are a professional Japanese linguist. Accuracy is everything."},
                      {"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0, timeout=8.0
        )
        res = json.loads(comp.choices[0].message.content)
        
        # --- 物理拦截逻辑：修正 AI 幻觉 ---
        bad_words = ["号召", "名落", "深山", "工作"]
        if any(bw in res['word'] for bw in bad_words):
             if "号召" in user_input:
                 res['word'], res['reading'], res['pos'] = "呼びかける", "よびかける", "動詞"
             elif "名落" in user_input or "深山" in user_input:
                 res['word'], res['reading'] = "落第", "らくだい"
             elif "工作" in user_input:
                 res['word'], res['reading'] = "仕事", "しごと"
        
        # 强制 3 例句对齐
        while len(res['sentences']) < 3:
            res['sentences'].append({"jp": "例文を準備中です。", "kana": "れいぶんをじゅんびちゅうです。", "cn": "例句准备中。"})
        return res
    except: return None

# --- 2. 界面极致紧凑布局 ---
st.set_page_config(page_title="FUSION Pro", layout="centered", page_icon="👘")

st.markdown("""<style>
    .header-box { border-bottom:2px solid #1E3A8A; padding:5px 0; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center; }
    .guide-box { font-size:0.9rem; font-weight:bold; color:#1E3A8A; margin:8px 0; border-left: 4px solid #3B82F6; padding-left:8px; }
    .word-box { background:white; padding:10px 15px; border-radius:10px; box-shadow:0 2px 8px rgba(0,0,0,0.05); border:1px solid #E5E7EB; text-align:center; margin-bottom:8px; }
    .card-item { border:1.5px solid #3B82F6; padding:8px 10px; border-radius:8px; margin-bottom:5px; background:#F8FAFC; border-left: 5px solid #1E3A8A; }
    .idx { background:#1E3A8A; color:white; width:18px; height:18px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; font-weight:bold; margin-right:6px; font-size:10px; }
    .stAudio { display:none; }
    .stButton>button { padding: 2px 10px; font-size: 0.85rem; height: auto; }
</style>""", unsafe_allow_html=True)

# 种子欢迎数据
WELCOME_DATA = {
    "word": "こんにちは", "reading": "こんにちは", "pos": "感嘆詞", "level": "N5", "pitch": "平板",
    "sentences": [
        {"jp": "皆さん、こんにちは。お会いできて嬉しいです。", "kana": "みなさん、こんにちは。おあいできてうれしいです。", "cn": "大家好，很高兴见到大家。"},
        {"jp": "日本語の学習を一緒に楽しみましょう。", "kana": "にほんごのがくしゅうをいっしょにたのしみましょう。", "cn": "让我们一起享受日语学习的乐趣吧。"},
        {"jp": "何か質問があれば、いつでも聞いてください。", "kana": "なにかしつもんがあれば、いつでもきいてください。", "cn": "如果有任何问题，请随时提问。"}
    ]
}

# 极速发音函数
def play_audio(text, slow=False):
    try:
        tts = gTTS(text=text, lang='ja', slow=slow)
        fp = io.BytesIO(); tts.write_to_fp(fp); fp.seek(0)
        st.audio(fp, format="audio/mp3", autoplay=True)
    except: pass

if "res_cache" not in st.session_state: st.session_state.res_cache = None
if "last_query" not in st.session_state: st.session_state.last_query = ""

st.markdown('<div class="header-box"><span style="color:#1E3A8A;font-size:1.2rem;font-weight:bold;">FUSION 智能化日语助手 Pro</span><span>👘</span></div>', unsafe_allow_html=True)

u_in = st.text_input("", placeholder="输入词汇 (按回车直接查询并播报)...", label_visibility="collapsed")

if u_in:
    if u_in != st.session_state.last_query:
        with st.spinner('FUSION 专家正在进行深度转译...'):
            res = get_fusion_expert_ultimate(u_in)
            if res:
                st.session_state.res_cache = res
                st.session_state.last_query = u_in
                # --- 回车即读 ---
                play_audio(f"これについて、以下の日本語が考えられます。{res['word']}")
    display_data = st.session_state.res_cache
else:
    display_data = WELCOME_DATA

if display_data:
    st.markdown(f'<div class="guide-box">💡 これについて、以下の日本語が考えられます。</div>', unsafe_allow_html=True)
    st.markdown(f"""<div class="word-box">
        <h3 style="margin:0;color:#1E3A8A;font-size:1.4rem;">{display_data.get('word')}</h3>
        <p style="margin:2px 0;color:#3B82F6;font-size:1.1rem;font-weight:bold;">【{display_data.get('reading')}】</p>
        <p style="color:#64748B;font-size:0.75rem;margin:0;">🏷️ {display_data.get('pos')} | {display_data.get('level')} | 声调:{display_data.get('pitch')}</p>
    </div>""", unsafe_allow_html=True)

    for i, s in enumerate(display_data.get('sentences', []), 1):
        st.markdown(f'<div class="card-item"><b><span class="idx">{i}</span>{s.get("jp")}</b><br><span style="color:#64748B;font-size:0.75rem;margin-left:24px;">{s.get("kana")}</span><br><span style="color:#059669;margin-left:24px;font-size:0.8rem;">🇨🇳 {s.get("cn")}</span></div>', unsafe_allow_html=True)
        ca, cb = st.columns(2)
        if ca.button(f"🟢 标准速 {i}", key=f"n_{i}", use_container_width=True): 
            play_audio(s.get("jp"), slow=False)
        if cb.button(f"🔴 慢速 {i}", key=f"s_{i}", use_container_width=True): 
            play_audio(s.get("jp"), slow=True)
