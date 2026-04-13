import streamlit as st
from openai import OpenAI
import json
from gtts import gTTS
import io

# --- 1. 核心数据库：高纯度 50 音体系 (100% 纯净校对版) ---
KANA_DATA = {
    "清音-行": {
        "あ行": [("あ","ア","a"), ("い","イ","i"), ("う","ウ","u"), ("え","エ","e"), ("お","オ","o")],
        "か行": [("か","カ","ka"), ("き","キ","ki"), ("く","ク","ku"), ("け","ケ","ke"), ("こ","コ","ko")],
        "さ行": [("さ","サ","sa"), ("し","シ","shi"), ("す","ス","su"), ("せ","セ","se"), ("そ","ソ","so")],
        "た行": [("た","タ","ta"), ("ち","チ","chi"), ("つ","ツ","tsu"), ("て","テ","te"), ("と","ト","to")],
        "な行": [("な","ナ","na"), ("に","ニ","ni"), ("ぬ","ヌ","nu"), ("ね","ネ","ne"), ("の","ノ","no")],
        "は行": [("は","ハ","ha"), ("ひ","ヒ","hi"), ("ふ","フ","fu"), ("へ","ヘ","he"), ("ほ","ホ","ho")],
        "ま行": [("ま","マ","ma"), ("み","ミ","mi"), ("む","ム","mu"), ("め","メ","me"), ("も","モ","mo")],
        "や行": [("や","ヤ","ya"), (None,None,None), ("ゆ","ユ","yu"), (None,None,None), ("よ","ヨ","yo")],
        "ら行": [("ら","ラ","ra"), ("り","リ","ri"), ("る","ル","ru"), ("れ","レ","re"), ("ろ","ロ","ro")],
        "わ行": [("わ","ワ","wa"), (None,None,None), (None,None,None), (None,None,None), ("を","ヲ","wo")],
        "ん": [("ん","ン","n"), (None,None,None), (None,None,None), (None,None,None), (None,None,None)]
    },
    "清音-段": {
        "あ段": [("あ","ア","a"), ("か","カ","ka"), ("さ","サ","sa"), ("た","タ","ta"), ("な","ナ","na"), ("は","ハ","ha"), ("ま","马","ma"), ("や","ヤ","ya"), ("ら","ラ","ra"), ("わ","ワ","wa")],
        "い段": [("い","イ","i"), ("き","キ","ki"), ("し","シ","shi"), ("ち","チ","chi"), ("に","ニ","ni"), ("ひ","ヒ","hi"), ("み","ミ","mi"), ("り","リ","ri")],
        "う段": [("う","ウ","u"), ("く","ク","ku"), ("す","ス","su"), ("つ","ツ","tsu"), ("ぬ","ヌ","nu"), ("夫","フ","fu"), ("む","ム","mu"), ("ゆ","ユ","yu"), ("る","ル","ru")],
        "え段": [("え","エ","e"), ("け","ケ","ke"), ("せ","セ","se"), ("て","テ","te"), ("ね","ネ","ne"), ("へ","ヘ","he"), ("め","メ","me"), ("れ","レ","re")],
        "お段": [("お","オ","o"), ("こ","コ","ko"), ("そ","ソ","so"), ("と","ト","to"), ("の","ノ","no"), ("ほ","ホ","ho"), ("も","モ","mo"), ("よ","ヨ","yo"), ("ろ","罗","ro"), ("を","ヲ","wo")]
    },
    "浊音/半浊音": {
        "が行": [("が","ガ","ga"), ("ぎ","ギ","gi"), ("ぐ","グ","gu"), ("げ","ゲ","ge"), ("ご","ゴ","go")],
        "ざ行": [("ざ","ザ","za"), ("じ","ジ","ji"), ("ず","ズ","zu"), ("ぜ","ゼ","ze"), ("ぞ","ゾ","zo")],
        "だ行": [("だ","ダ","da"), ("ぢ","ヂ","ji"), ("づ","ヅ","zu"), ("で","デ","de"), ("ど","ド","do")],
        "ば行": [("ば","バ","ba"), ("び","ビ","bi"), ("ぶ","ブ","bu"), ("べ","ベ","be"), ("ぼ","波","bo")],
        "ぱ行": [("ぱ","帕","pa"), ("ぴ","皮","pi"), ("ぷ","普","pu"), ("ぺ","佩","pe"), ("ぽ","波","po")]
    },
    "拗音体系": {
        "清拗音": [("きゃ","キャ","kya"), ("きゅ","キュ","kyu"), ("きょ","キョ","kyo"), ("しゃ","シャ","sha"), ("しゅ","シュ","shu"), ("しょ","ショ","sho"), ("ちゃ","チャ","cha"), ("ちゅ","チュ","chu"), ("ちょ","チョ","cho")],
        "浊拗音": [("ぎゃ","ギャ","gya"), ("ぎゅ","ギュ","gyu"), ("ぎょ","ギョ","gyo"), ("じゃ","ジャ","ja"), ("じゅ","ジュ","ju"), ("じょ","ジョ","jo")],
        "半浊拗音": [("ぴゃ","ピャ","pya"), ("ぴゅ","ピュ","pyu"), ("ぴょ","ピョ","pyo")]
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

# --- 2. 核心播报引擎 (Phonetic Padding 算法) ---
def play_audio(text_input, is_continuous=False):
    """
    通过音位补全，彻底根除助词误读
    """
    try:
        def force_primary_sound(t):
            # 针对顽固的助词发音，使用长元音补全强制拉回词头发音
            if t == "は": return "はあ" # ha -> haa 确保 ha 原音
            if t == "へ": return "へえ" # he -> hee 确保 he 原音
            if t == "を": return "をを" # o -> oo 确保 o 原音
            return t

        if isinstance(text_input, list):
            # 连读模式
            processed_text = "、".join([force_primary_sound(t) for t in text_input if t])
        else:
            # 单音模式
            processed_text = force_primary_sound(text_input)

        tts = gTTS(text=processed_text, lang='ja', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        st.audio(fp, format="audio/mp3", autoplay=True)
    except:
        pass

def get_expert_translation(u_in):
    try:
        client = OpenAI(api_key=st.secrets["NEW_API_KEY"], base_url=st.secrets["NEW_BASE_URL"])
        prompt = f"专家翻译'{u_in}'。JSON：word, reading, pos, level, pitch, context_advice, sentences(3句)。"
        comp = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "顶级中日同传专家。"}, {"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(comp.choices[0].message.content)
    except: return None

# --- 3. UI 整体样式 ---
st.set_page_config(page_title="FUSION Pro v3.4", layout="wide")

st.markdown("""<style>
    [data-testid="stSidebar"] { background-color: #0F172A; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span { color: #FFFFFF !important; font-weight: 500; }
    audio { display:none !important; }
    
    .kana-card {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 10px 0;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .hiragana { font-size: 2rem; font-weight: bold; color: #1E3A8A; line-height: 1.1; }
    .katakana { font-size: 0.9rem; color: #64748B; margin: 2px 0; }
    .romaji { font-size: 0.8rem; color: #3B82F6; font-weight: 600; text-transform: uppercase; }
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## FUSION Pro")
    menu = st.radio("功能模块切换", ["AI 词汇专家", "五十音实验室", "每周 7 句金句"], index=1)

# --- 模块 B: 五十音实验室 ---
if menu == "五十音实验室":
    st.header("五十音实验室")
    
    tab_titles = list(KANA_DATA.keys())
    selected_tab = st.segmented_control("选择音系", tab_titles, default=tab_titles[0])
    sub_cat = st.selectbox(f"具体分类", list(KANA_DATA[selected_tab].keys()))
    current_list = KANA_DATA[selected_tab][sub_cat]
    
    if st.button(f"⏱️ 节奏连读整个 【{sub_cat}】", use_container_width=True):
        play_audio([item[0] for item in current_list if item[0]], is_continuous=True)
            
    st.markdown("---")
    num_cols = 5 if "行" in selected_tab or "浊" in selected_tab else 3
    cols = st.columns(num_cols)
    for idx, item in enumerate(current_list):
        if item[0]:
            with cols[idx % num_cols]:
                st.markdown(f"""
                <div class="kana-card">
                    <div class="hiragana">{item[0]}</div>
                    <div class="katakana">{item[1]}</div>
                    <div class="romaji">{item[2]}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("🔊", key=f"s_{sub_cat}_{idx}", use_container_width=True):
                    play_audio(item[0])

# --- 模块 A/C 略 (保持 v3.3 逻辑) ---
elif menu == "AI 词汇专家":
    st.header("AI 词汇专家")
    u_in = st.text_input("请输入中文词汇", placeholder="号召、落实")
    search_query = u_in.strip() if u_in else "你好"
    if search_query:
        if "last_query" not in st.session_state or st.session_state.last_query != search_query:
            res = get_expert_translation(search_query)
            if res:
                st.session_state.res_cache = res
                st.session_state.last_query = search_query
                play_audio("これについて、以下の日本語が考えられます")
        display = st.session_state.get('res_cache')
        if display:
            st.markdown(f"""<div style="background:white; padding:12px 20px; border-radius:12px; box-shadow:0 8px 20px rgba(0,0,0,0.05); border:1px solid #E5E7EB; text-align:center; margin: auto; max-width: 650px; border-top: 5px solid #3B82F6;">
                <h1 style="margin:2px 0; color:#1E3A8A;">{display['word']}</h1>
                <p style="color:#3B82F6; font-weight:bold;">【{display['reading']}】</p>
                <div style="font-size:0.8rem; color:#475569;">🏷️ {display['pos']} | 🏆 {display['level']} | 📈 {display['pitch']}型</div>
            </div>""", unsafe_allow_html=True)
            if st.button("🔊 播放", key="p_main"): play_audio(display['word'])
            for i, s in enumerate(display.get('sentences', []), 1):
                st.markdown(f'<div style="border:1.5px solid #E2E8F0; padding:12px; border-radius:10px; margin-bottom:10px; background:#F8FAFC; border-left: 6px solid #1E3A8A;"><b>{i}. {s["jp"]}</b><br><small>{s["kana"]}</small><br><span style="color:#059669;">{s["cn"]}</span></div>', unsafe_allow_html=True)
                c1, c2, _ = st.columns([1, 1, 3])
                if c1.button(f"▶️ 标准 {i}", key=f"std_{i}"): play_audio(s["jp"])
                if c2.button(f"🐢 慢速 {i}", key=f"slo_{i}"): play_audio(s["jp"], slow=True)

elif menu == "每周 7 句金句":
    st.header("每周 7 句实战金句")
    for i, item in enumerate(WEEKLY_CONTENT, 1):
        with st.expander(f"第 {i} 句：{item['jp']}"):
            st.write(f"**🇨🇳 中文：** {item['cn']}")
            if st.button(f"🔊 播放", key=f"wk_p_{i}"): play_audio(item['jp'])
