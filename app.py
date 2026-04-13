import streamlit as st
from openai import OpenAI
import json
from gtts import gTTS
import io
import time

# --- 1. 核心数据库：100% 纯净五十音与实战金句 ---
KANA_DATA = {
    "清音-行": {
        "あ行": [("あ","ア","a"), ("い","イ","i"), ("う","ウ","u"), ("え","エ","e"), ("お","オ","o")],
        "か行": [("か","カ","ka"), ("き","キ","ki"), ("く","ク","ku"), ("け","ケ","ke"), ("こ","コ","ko")],
        "さ行": [("さ","サ","sa"), ("し","シ","shi"), ("す","ス","su"), ("せ","セ","se"), ("そ","ソ","so")],
        "た行": [("た","タ","ta"), ("ち","チ","chi"), ("つ","ツ","tsu"), ("て","テ","te"), ("と","ト","to")],
        "な行": [("な","ナ","na"), ("に","ニ","ni"), ("ぬ","ヌ","nu"), ("ね","ネ","ne"), ("の","ノ","no")],
        "は行": [("は","ハ","ha"), ("ひ","ヒ","hi"), ("ふ","フ","fu"), ("へ","ヘ","he"), ("ほ","ホ","ho")],
        "ま行": [("ま","マ","ma"), ("み","ミ","mi"), ("む","ム","mu"), ("め","メ","me"), ("も","モ","mo")],
        "や行": [("や","ヤ","ya"), (None,None,None), ("ゆ","ユ","yu"), (None,None,None), ("よ","ヨ","yo")], # 已修复补齐
        "ら行": [("ら","ラ","ra"), ("り","リ","ri"), ("る","ル","ru"), ("れ","レ","re"), ("ろ","ロ","ro")],
        "わ行": [("わ","ワ","wa"), (None,None,None), (None,None,None), (None,None,None), ("を","ヲ","wo")],
        "ん": [("ん","ン","n"), (None,None,None), (None,None,None), (None,None,None), (None,None,None)]
    },
    "清音-段": {
        "あ段": [("あ","ア","a"), ("か","カ","ka"), ("さ","サ","sa"), ("た","タ","ta"), ("な","ナ","na"), ("は","ハ","ha"), ("ま","マ","ma"), ("や","ヤ","ya"), ("ら","ラ","ra"), ("わ","和","wa")],
        "い段": [("い","イ","i"), ("き","キ","ki"), ("し","シ","shi"), ("ち","チ","chi"), ("に","ニ","ni"), ("ひ","ヒ","hi"), ("み","ミ","mi"), ("り","リ","ri")],
        "う段": [("う","ウ","u"), ("く","ク","ku"), ("す","ス","su"), ("つ","ツ","tsu"), ("ぬ","ヌ","nu"), ("ふ","フ","fu"), ("む","ム","mu"), ("ゆ","ユ","yu"), ("る","ル","ru")],
        "え段": [("え","エ","e"), ("け","ケ","ke"), ("せ","セ","se"), ("て","テ","te"), ("ね","ネ","ne"), ("へ","ヘ","he"), ("め","メ","me"), ("れ","レ","re")],
        "お段": [("お","オ","o"), ("こ","コ","ko"), ("そ","ソ","so"), ("と","ト","to"), ("の","ノ","no"), ("ほ","ホ","ho"), ("も","モ","mo"), ("よ","ヨ","yo"), ("ろ","ロ","ro"), ("を","ヲ","wo")]
    },
    "浊音/半浊音": {
        "が行": [("が","ガ","ga"), ("ぎ","ギ","gi"), ("ぐ","グ","gu"), ("げ","ゲ","ge"), ("ご","ゴ","go")],
        "ざ行": [("ざ","ザ","za"), ("じ","ジ","ji"), ("ず","ズ","zu"), ("ぜ","ゼ","ze"), ("ぞ","ゾ","zo")],
        "だ行": [("だ","ダ","da"), ("ぢ","ヂ","ji"), ("づ","ヅ","zu"), ("で","デ","de"), ("ど","ド","do")],
        "ば行": [("ば","バ","ba"), ("び","ビ","bi"), ("ぶ","ブ","bu"), ("べ","ベ","be"), ("ぼ","ボ","bo")],
        "ぱ行": [("ぱ","パ","pa"), ("ぴ","ピ","pi"), ("ぷ","プ","pu"), ("ぺ","ぺ","pe"), ("ぽ","ポ","po")]
    }
}

WEEKLY_CONTENT = [
    {"jp": "私は昨日、図書館で本を読みました。", "cn": "我昨天在图书馆读书了。"},
    {"jp": "私は毎日コーヒーを飲みます。", "cn": "我每天喝咖啡。"},
    {"jp": "これは日本語の本です。", "cn": "这是日语书。"},
    {"jp": "駅はあそこにあります。", "cn": "车站就在那儿。"},
    {"jp": "一緒に昼ご飯を食べませんか。", "cn": "要不要一起吃午饭？"},
    {"jp": "明日も会社に行きます。", "cn": "明天也去公司。"},
    {"jp": "このケーキはとても美味しいです。", "cn": "这个蛋糕非常好吃。"}
]

# --- 2. 核心引擎 (发音及专家翻译) ---
def play_audio(text_input):
    try:
        def calibrate(t):
            # 针对助词锁定片假名原音发音逻辑
            if t == "は": return "ハ。" 
            if t == "へ": return "ヘ。"
            return t

        if isinstance(text_input, list):
            processed_text = " 、 ".join([calibrate(t) for t in text_input if t])
        else:
            processed_text = calibrate(text_input)

        tts = gTTS(text=processed_text, lang='ja', slow=False)
        fp = io.BytesIO(); tts.write_to_fp(fp); fp.seek(0)
        st.audio(fp, format="audio/mp3", autoplay=True)
    except: pass

def get_expert_translation(u_in):
    try:
        client = OpenAI(api_key=st.secrets["NEW_API_KEY"], base_url=st.secrets["NEW_BASE_URL"])
        prompt = f"专家翻译'{u_in}'。JSON格式：word, reading, pos, level, pitch, sentences(3句含jp, kana, cn)。"
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "顶尖中日翻译专家。只输出纯JSON。"}, {"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except: return None

# --- 3. UI 布局与样式 ---
st.set_page_config(page_title="FUSION Pro v4.2", layout="wide")

st.markdown("""<style>
    [data-testid="stSidebar"] { background-color: #0F172A !important; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label { 
        color: #FFFFFF !important; font-weight: 500 !important; 
    }
    audio { display:none !important; }
    .kana-card { background: white; border: 1px solid #E2E8F0; border-radius: 12px; padding: 10px 0; text-align: center; }
    .hiragana { font-size: 2rem; font-weight: bold; color: #1E3A8A; line-height: 1.1; }
    .romaji { font-size: 0.85rem; color: #3B82F6; font-weight: 600; text-transform: uppercase; }
    .word-box { background:white; padding:15px; border-radius:12px; box-shadow:0 8px 20px rgba(0,0,0,0.05); border:1px solid #E5E7EB; text-align:center; }
    .card-item { border:1.5px solid #E2E8F0; padding:12px; border-radius:10px; margin-bottom:10px; background:#F8FAFC; border-left: 6px solid #1E3A8A; }
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.title("FUSION Pro")
    menu = st.radio("功能模块切换", ["AI 词汇专家", "五十音实验室", "每周 7 句"], index=0)

# --- 模块 A: AI 词汇专家 ---
if menu == "AI 词汇专家":
    st.header("AI 词汇专家")
    u_in = st.text_input("请输入中文词汇 (按回车查询)", placeholder="落实、号召")
    current_word = u_in.strip() if u_in else "你好"
    
    if current_word:
        if "last_query" not in st.session_state or st.session_state.last_query != current_word:
            res = get_expert_translation(current_word)
            if res:
                st.session_state.res_cache = res
                st.session_state.last_query = current_word
                play_audio("これについて、以下の日本語が考えられます")

        display = st.session_state.get('res_cache')
        if display:
            st.markdown(f"""<div class="word-box" style="max-width:650px; margin:auto;">
                <h1 style="color:#1E3A8A; margin:0;">{display.get('word','')}</h1>
                <p style="color:#3B82F6; font-size:1.2rem; font-weight:bold; margin:5px 0;">【{display.get('reading','')}】</p>
                <div style="font-size:0.8rem; color:#64748B;">🏷️ {display.get('pos','')} | 🏆 {display.get('level','')} | 📈 {display.get('pitch','')}型</div>
            </div>""", unsafe_allow_html=True)
            
            _, cm, _ = st.columns([1,1,1])
            if cm.button("🔊 播放单词正音", use_container_width=True, key=f"main_p_{time.time()}"):
                play_audio(display.get('word',''))

            st.markdown("---")
            st.subheader("📖 专业场景例句")
            for i, s in enumerate(display.get('sentences', []), 1):
                with st.container():
                    st.markdown(f"""<div class="card-item">
                        <strong>{i}. {s.get('jp', '')}</strong><br>
                        <small style="color:#64748B;">{s.get('kana', '')}</small><br>
                        <span style="color:#059669; font-weight:500;">{s.get('cn', '')}</span>
                    </div>""", unsafe_allow_html=True)
                    col1, col2, _ = st.columns([1, 1, 3])
                    if col1.button(f"▶️ 标准速 {i}", key=f"std_{i}_{time.time()}"): play_audio(s.get('jp',''))
                    if col2.button(f"🐢 慢速 {i}", key=f"slo_{i}_{time.time()}"): play_audio(s.get('jp',''))

# --- 模块 B: 五十音实验室 ---
elif menu == "五十音实验室":
    st.header("五十音实验室")
    selected_tab = st.segmented_control("音系选择", list(KANA_DATA.keys()), default="清音-行")
    
    if selected_tab in KANA_DATA:
        sub_cat = st.selectbox("分类选择", list(KANA_DATA[selected_tab].keys()))
        current_list = KANA_DATA[selected_tab][sub_cat]
        
        if st.button(f"🔊 节奏连读：{sub_cat}", use_container_width=True, key=f"run_{sub_cat}"):
            play_audio([item[0] for item in current_list if item[0]])
                
        st.markdown("---")
        num_cols = 5 if "行" in sub_cat or "浊" in sub_cat else 3
        cols = st.columns(num_cols)
        for idx, item in enumerate(current_list):
            if item[0]:
                with cols[idx % num_cols]:
                    st.markdown(f"""<div class="kana-card">
                        <div class="hiragana">{item[0]}</div>
                        <div style="color:#64748B; font-size:0.9rem;">{item[1]}</div>
                        <div class="romaji">{item[2]}</div>
                    </div>""", unsafe_allow_html=True)
                    if st.button("🔊", key=f"v_{sub_cat}_{idx}_{time.time()}", use_container_width=True):
                        play_audio(item[0])

# --- 模块 C: 每周 7 句实战金句 ---
elif menu == "每周 7 句":
    st.header("每周 7 句实战金句")
    for i, item in enumerate(WEEKLY_CONTENT, 1):
        with st.expander(f"第 {i} 句：{item['jp']}"):
            st.write(f"🇨🇳 中文翻译：{item['cn']}")
            # 补齐朗读功能
            if st.button(f"🔊 播放标准朗读", key=f"wk_play_{i}_{time.time()}"):
                play_audio(item['jp'])
            st.audio_input(f"录音跟读练习", key=f"wk_input_{i}")
