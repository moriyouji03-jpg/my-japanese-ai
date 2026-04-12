import streamlit as st
from openai import OpenAI
import json
from gtts import gTTS
import io

# --- 1. 核心数据库 (严禁改动) ---
KANA_CHART = {
    "清音-行": {"あ行": [("あ","ア","a"), ("い","イ","i"), ("う","ウ","u"), ("え","エ","e"), ("お","オ","o")], "か行": [("か","カ","ka"), ("き","キ","ki"), ("く","ク","ku"), ("け","ケ","ke"), ("こ","コ","ko")], "さ行": [("さ","サ","sa"), ("し","シ","shi"), ("す","ス","su"), ("せ","セ","se"), ("そ","ソ","so")], "た行": [("た","タ","ta"), ("ち","チ","chi"), ("つ","ツ","tsu"), ("て","テ","te"), ("と","ト","to")], "な行": [("な","ナ","na"), ("に","ニ","ni"), ("ぬ","ヌ","nu"), ("ね","ネ","ne"), ("の","ノ","no")], "は行": [("は","ハ","ha"), ("ひ","ヒ","hi"), ("ふ","フ","fu"), ("へ","ヘ","he"), ("ほ","ホ","ho")], "ま行": [("ま","マ","ma"), ("み","ミ","mi"), ("む","ム","mu"), ("め","メ","me"), ("も","モ","mo")], "や行": [("や","ヤ","ya"), (None,None,None), ("ゆ","ユ","yu"), (None,None,None), ("よ","ヨ","yo")], "ら行": [("ら","ラ","ra"), ("り","リ","ri"), ("る","ル","ru"), ("れ","レ","re"), ("ろ","罗","ro")], "わ行": [("わ","ワ","wa"), (None,None,None), (None,None,None), (None,None,None), ("を","ヲ","wo")], "ん": [("ん","ン","n"), (None,None,None), (None,None,None), (None,None,None), (None,None,None)]},
    "清音-段": {"あ段": [("あ","ア","a"), ("か","カ","ka"), ("さ","サ","sa"), ("た","タ","ta"), ("な","ナ","na"), ("は","ハ","ha"), ("ま","マ","ma"), ("や","ヤ","ya"), ("ら","ラ","ra"), ("わ","ワ","wa")], "い段": [("い","イ","i"), ("き","キ","ki"), ("し","シ","shi"), ("ち","チ","chi"), ("に","ニ","ni"), ("ひ","ヒ","hi"), ("み","ミ","mi"), ("り","リ","ri")], "う段": [("う","ウ","u"), ("く","ク","ku"), ("す","ス","su"), ("つ","ツ","tsu"), ("ぬ","ヌ","nu"), ("ふ","フ","fu"), ("む","ム","mu"), ("ゆ","ユ","yu"), ("る","ル","ru")], "え段": [("え","エ","e"), ("け","ケ","ke"), ("せ","セ","se"), ("て","テ","te"), ("ね","ネ","ne"), ("へ","ヘ","he"), ("め","メ","me"), ("れ","レ","re")], "お段": [("お","オ","o"), ("こ","コ","ko"), ("そ","ソ","so"), ("と","ト","to"), ("の","ノ","no"), ("ほ","ホ","ho"), ("も","モ","mo"), ("よ","ヨ","yo"), ("ろ","ロ","ro"), ("を","ヲ","wo")]}
}

# --- 2. 专家级发音引擎 ---
def play_audio(text, is_kana=False):
    try:
        audio_text = {"は": "ハ", "へ": "ヘ"}.get(text, text) if is_kana else text
        tts = gTTS(text=audio_text, lang='ja')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        st.audio(fp, format="audio/mp3", autoplay=True)
    except: pass

def get_expert_translation(u_in):
    try:
        client = OpenAI(api_key=st.secrets["NEW_API_KEY"], base_url=st.secrets["NEW_BASE_URL"])
        prompt = f"Expert Japanese Translate '{u_in}'. Return JSON ONLY."
        comp = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "Return valid JSON: {\"word\":\"\",\"reading\":\"\",\"pos\":\"\",\"level\":\"\",\"pitch\":\"\",\"sentences\":[{\"jp\":\"\",\"kana\":\"\",\"cn\":\"\"}]}"}],
            response_format={"type": "json_object"}
        )
        return json.loads(comp.choices[0].message.content)
    except: return None

# --- 3. UI 界面 ---
st.set_page_config(page_title="FUSION Pro", layout="wide")

# CSS 深度美化与对齐
st.markdown("""<style>
    [data-testid="stSidebar"] { background-color: #0F172A; }
    [data-testid="stSidebar"] * { color: #F1F5F9 !important; }
    .stAudio { display:none !important; }
    .word-box { background:white; padding:20px; border-radius:12px; border:1px solid #E5E7EB; text-align:center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
    .card-item { border:1px solid #3B82F6; padding:12px; border-radius:10px; margin-bottom:10px; background:#F8FAFC; border-left: 6px solid #1E3A8A; }
    .kana-card-container { display: flex; flex-direction: column; align-items: center; justify-content: center; background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px; min-width: 80px; }
    .kana-main { font-size: 1.8rem; font-weight: bold; color: #1E3A8A; margin-bottom: 2px; }
    .kana-sub { font-size: 0.8rem; color: #64748B; }
</style>""", unsafe_allow_html=True)

WELCOME_DATA = {
    "word": "こんにちは", "reading": "こんにちは", "pos": "感嘆詞", "level": "N5", "pitch": "平板",
    "sentences": [
        {"jp": "こんにちは、今日もよろしくお願いします。", "kana": "こんにちは、きょうもよろしくおねがいします。", "cn": "你好，今天也请多多关照。"},
        {"jp": "FUSION Proへようこそ、一緒に勉強しましょう。", "kana": "フュージョンプロへようこそ、いっしょにべんきょうしましょう。", "cn": "欢迎来到FUSION Pro，让我们一起学习吧。"},
        {"jp": "日本語の美しさを感じてください。", "kana": "にほんごのうつくしさをかんじてください。", "cn": "请感受日语的美。"}
    ]
}

with st.sidebar:
    st.markdown("## FUSION Pro")
    menu = st.radio("功能切换", ["AI 词汇专家", "五十音实验室", "每周 7 句金句"])
    st.markdown("---")
    st.markdown("<p style='color:#3B82F6; text-align:center;'>🌸 今日も、一緒に頑張りましょう！</p>", unsafe_allow_html=True)

# --- 模块 A: AI 词汇专家 ---
if menu == "AI 词汇专家":
    st.header("AI 词汇专家")
    st.markdown("<h4 style='text-align:center; color:#3B82F6;'>今日も、一緒に頑張りましょう！</h4>", unsafe_allow_html=True)
    
    u_in = st.text_input("请输入中文词汇 (回车提交)", key="input_field")
    
    # 逻辑：判定输入
    if u_in:
        if "last" not in st.session_state or st.session_state.last != u_in:
            res = get_expert_translation(u_in)
            if res:
                st.session_state.data = res
                st.session_state.last = u_in
                play_audio(f"これについて、以下の日本語が考えられます。{res['word']}")
        display_data = st.session_state.get('data')
    else:
        display_data = WELCOME_DATA
        if "played_welcome" not in st.session_state:
            play_audio("こんにちは、今日もよろしくお願いします。")
            st.session_state.played_welcome = True

    if display_data:
        st.markdown(f"""<div class="word-box">
            <h2 style="margin:0; color:#1E3A8A;">{display_data['word']}</h2>
            <p style="color:#3B82F6; font-size:1.2rem; font-weight:bold;">【{display_data['reading']}】</p>
            <p style="color:#64748B; font-size:0.8rem;">🏷️ {display_data.get('pos','')} | {display_data.get('level','')} | {display_data.get('pitch','')}</p>
        </div>""", unsafe_allow_html=True)
        st.write("")
        for i, s in enumerate(display_data['sentences'], 1):
            st.markdown(f'<div class="card-item"><b>{i}. {s["jp"]}</b><br><small>{s["kana"]}</small><br><span style="color:#059669;">{s["cn"]}</span></div>', unsafe_allow_html=True)
            if st.button(f"🔊 播放例句 {i}", key=f"btn_{i}"): play_audio(s["jp"])

# --- 模块 B: 五十音实验室 (视觉对齐版) ---
elif menu == "五十音实验室":
    st.header("五十音实验室")
    cat = st.selectbox("分类", list(KANA_CHART.keys()))
    sub = st.selectbox(f"具体【{cat}】", list(KANA_CHART[cat].keys()))
    current_list = KANA_CHART[cat][sub]
    
    if st.button(f"🔊 连读整个【{sub}】", use_container_width=True):
        audio_t = " 、 ".join([item[0] for item in current_list if item[0]])
        play_audio(audio_t, is_kana=True)

    st.write("")
    # 栅格系统对齐
    cols = st.columns(len(current_list))
    for idx, item in enumerate(current_list):
        if item[0]:
            with cols[idx]:
                st.markdown(f"""<div class="kana-card-container">
                    <div class="kana-main">{item[0]}</div>
                    <div class="kana-sub">{item[1]}</div>
                    <div class="kana-sub">[{item[2]}]</div>
                </div>""", unsafe_allow_html=True)
                if st.button("🔊", key=f"k_{sub}_{idx}"): play_audio(item[0], is_kana=True)
