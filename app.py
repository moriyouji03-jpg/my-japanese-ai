import streamlit as st
from openai import OpenAI
import json
from gtts import gTTS
import io

# --- 1. 专家级：语义重构与 3 例句强约束引擎 ---
def get_fusion_expert_final_v2(user_input):
    prompt = f"""
    Role: Senior Japanese Linguist (NHK Standard).
    Task: Translate MEANING of Chinese '{user_input}' to NATIVE Japanese.
    
    STRICT RULES:
    1. WORD: Use ONLY native words (e.g. '不合格' for '名落孙山'). 
    2. ATTRIBUTES: Explicitly state if it's '他動詞' or '自動詞' if applicable.
    3. QUANTITY: Exactly 3 distinct high-quality sentences.
    
    JSON format:
    {{
      "word": "地道词汇",
      "reading": "平假名",
      "pos": "词性(含自/他动词标注)",
      "level": "N1-N5",
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
            messages=[{"role": "system", "content": "Professional Japanese Editor. You focus on accurate grammar (transitive/intransitive)."},
                      {"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0, timeout=8.0
        )
        res = json.loads(comp.choices[0].message.content)
        
        # 物理拦截逻辑
        bad_words = ["号召", "名落", "深山", "工作"]
        if any(bw in res['word'] for bw in bad_words):
             if "号召" in user_input: res['word'], res['reading'] = "呼びかける", "よびかける"
             elif "名落" in user_input: res['word'], res['reading'] = "落第", "らくだい"
             elif "工作" in user_input: res['word'], res['reading'] = "仕事", "しごと"
        
        while len(res['sentences']) < 3:
            res['sentences'].append({"jp": "例文を準備中です。", "kana": "れいぶんをじゅんびちゅうです。", "cn": "例句准备中。"})
        return res
    except: return None

# --- 2. 界面设计 ---
st.set_page_config(page_title="FUSION Pro", layout="centered", page_icon="👘")

st.markdown("""<style>
    .header-box { border-bottom:2px solid #1E3A8A; padding:5px 0; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center; }
    .guide-box { font-size:0.9rem; font-weight:bold; color:#1E3A8A; margin:8px 0; border-left: 4px solid #3B82F6; padding-left:8px; }
    .word-box { background:white; padding:10px 15px; border-radius:10px; box-shadow:0 2px 8px rgba(0,0,0,0.05); border:1px solid #E5E7EB; text-align:center; margin-bottom:8px; }
    .card-item { border:1.5px solid #3B82F6; padding:8px 10px; border-radius:8px; margin-bottom:5px; background:#F8FAFC; border-left: 5px solid #1E3A8A; }
    .idx { background:#1E3A8A; color:white; width:18px; height:18px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; font-weight:bold; margin-right:6px; font-size:10px; }
    .stAudio { display:none; }
    .stButton>button { padding: 2px 10px; font-size: 0.85rem; height: auto; border-radius: 20px; }
</style>""", unsafe_allow_html=True)

WELCOME_DATA = {
    "word": "こんにちは", "reading": "こんにちは", "pos": "感嘆詞", "level": "N5", "pitch": "平板",
    "sentences": [
        {"jp": "🌸 FUSION Pro：传递最地道的日本之声。", "kana": "フュージョン プロ：もっともじもとのにほんのこえをつたえます。", "cn": "FUSION Pro：传递最地道的日本之声。"},
        {"jp": "日本語の学習を一緒に楽しみましょう。", "kana": "にほんごのがくしゅうをいっしょにたのしみましょう。", "cn": "让我们一起享受日语学习的乐趣吧。"},
        {"jp": "何か質問があれば、いつでも聞いてください。", "kana": "なにかしつもんがあれば、いつでもきいてください。", "cn": "如果有任何问题，请随时提问。"}
    ]
}

def play_audio(text, slow=False):
    try:
        tts = gTTS(text=text, lang='ja', slow=slow)
        fp = io.BytesIO(); tts.write_to_fp(fp); fp.seek(0)
        st.audio(fp, format="audio/mp3", autoplay=True)
    except: pass

if "res_cache" not in st.session_state: st.session_state.res_cache = None
if "last_query" not in st.session_state: st.session_state.last_query = ""

st.markdown('<div class="header-box"><span style="color:#1E3A8A;font-size:1.2rem;font-weight:bold;">FUSION 智能化日语助手 Pro</span><span>👘</span></div>', unsafe_allow_html=True)

# 快速建议标签
c1, c2, c3, c4 = st.columns(4)
q_tags = ["努力", "号召", "工作", "出差"]
btn_val = None
if c1.button("🔥 努力"): btn_val = "努力"
if c2.button("🚀 号召"): btn_val = "号召"
if c3.button("💼 工作"): btn_val = "工作"
if c4.button("🚄 出差"): btn_val = "出差"

u_in_raw = st.text_input("", placeholder="输入词汇 (按回车直接查询播报)...", label_visibility="collapsed")
u_in = btn_val if btn_val else u_in_raw

if u_in:
    if u_in != st.session_state.last_query:
        with st.spinner('专家引擎校准中...'):
            res = get_fusion_expert_final_v2(u_in)
            if res:
                st.session_state.res_cache = res
                st.session_state.last_query = u_in
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
