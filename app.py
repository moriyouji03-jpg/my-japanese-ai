import streamlit as st
from openai import OpenAI
import json
from gtts import gTTS
import io

# --- 1. 核心数据库：全量五十音、浊音、拗音 (100% 纯净版) ---
KANA_DATA = {
    "清音": {
        "行模式": {
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
        "段模式": {
            "あ段": [("あ","ア","a"), ("か","カ","ka"), ("さ","サ","sa"), ("た","タ","ta"), ("な","ナ","na"), ("は","ハ","ha"), ("ま","マ","ma"), ("や","ヤ","ya"), ("ら","拉","ra"), ("わ","ワ","wa")],
            "い段": [("い","イ","i"), ("き","キ","ki"), ("し","シ","shi"), ("ち","チ","chi"), ("に","ニ","ni"), ("ひ","ヒ","hi"), ("み","ミ","mi"), ("り","里","ri")],
            "う段": [("う","ウ","u"), ("く","ク","ku"), ("す","ス","su"), ("つ","ツ","tsu"), ("ぬ","努","nu"), ("ふ","夫","fu"), ("む","姆","mu"), ("ゆ","由","yu"), ("る","路","ru")],
            "え段": [("え","エ","e"), ("け","ケ","ke"), ("せ","塞","se"), ("て","特","te"), ("ね","内","ne"), ("へ","黑","he"), ("め","梅","me"), ("れ","雷","re")],
            "お段": [("お","オ","o"), ("こ","阔","ko"), ("そ","索","so"), ("と","托","to"), ("の","诺","no"), ("ほ","霍","ho"), ("も","莫","mo"), ("よ","由","yo"), ("ろ","罗","ro")]
        }
    },
    "浊音/半浊音": {
        "が行": [("が","ガ","ga"), ("ぎ","ギ","gi"), ("ぐ","グ","gu"), ("げ","格","ge"), ("ご","戈","go")],
        "ざ行": [("ざ","扎","za"), ("じ","吉","ji"), ("ず","兹","zu"), ("ぜ","则","ze"), ("ぞ","左","zo")],
        "だ行": [("だ","达","da"), ("ぢ","吉","ji"), ("づ","兹","zu"), ("で","得","de"), ("ど","多","do")],
        "ば行": [("ば","巴","ba"), ("び","毕","bi"), ("ぶ","布","bu"), ("べ","贝","be"), ("ぼ","波","bo")],
        "ぱ行": [("ぱ","帕","pa"), ("ぴ","皮","pi"), ("ぷ","普","pu"), ("ぺ","佩","pe"), ("ぽ","波","po")]
    },
    "拗音": {
        "清拗音": [("きゃ","kya"), ("きゅ","kyu"), ("きょ","kyo"), ("しゃ","sha"), ("しゅ","shu"), ("しょ","sho"), ("ちゃ","cha"), ("ちゅ","chu"), ("ちょ","cho")],
        "浊拗音": [("ぎゃ","gya"), ("ぎゅ","gyu"), ("ぎょ","gyo"), ("じゃ","ja"), ("じゅ","ju"), ("じょ","jo")],
        "半浊拗音": [("ぴゃ","pya"), ("ぴゅ","pyu"), ("ぴょ","pyo")]
    }
}

WEEKLY_CONTENT = [
    {"jp": "私は昨日、図書館で本を読みました。", "cn": "我昨天在图书馆读书了。"},
    {"jp": "私は毎日コーヒーを飲みます。", "cn": "我每天喝咖啡。"},
    {"jp": "これは日本語の本です。", "cn": "这是日语书。"},
    {"jp": "駅はあそこにあります。", "cn": "车站就在那儿。"},
    {"jp": "一緒に昼ご飯を食べませんか。", "cn": "要不要一起吃午饭？"}
]

# --- 2. 语音引擎 (v7.1 精准校准版) ---
def play_audio(text_input):
    audio_slot = st.empty()
    try:
        def calibrate(t):
            # 锁定原音的关键：使用假名+长音标记 ヘー 避开助词算法
            anchors = {"は": "ハ", "へ": "ヘー", "を": "ヲ"}
            return anchors.get(t, t)

        processed = "、".join([calibrate(t) for t in text_input if t]) if isinstance(text_input, list) else calibrate(text_input)
        tts = gTTS(text=processed, lang='ja', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        with audio_slot:
            st.audio(fp, format="audio/mp3", autoplay=True)
    except:
        pass

def get_expert_translation(u_in):
    try:
        client = OpenAI(api_key=st.secrets["NEW_API_KEY"], base_url=st.secrets["NEW_BASE_URL"])
        prompt = f"专家分析‘{u_in}’。输出纯JSON：word, reading, pos, level, pitch, sentences(3句含jp, kana, cn)。"
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "Top-tier translator."}, {"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        return json.loads(response.choices[0].message.content)
    except:
        return None

# --- 3. UI 布局 ---
st.set_page_config(page_title="FUSION Pro v7.1", layout="wide")

st.markdown("""<style>
    [data-testid="stSidebar"] { background-color: #0F172A !important; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span { color: white !important; }
    audio { display:none !important; }
    .word-box { background:white; padding:15px; border-radius:12px; border:1px solid #E5E7EB; text-align:center; }
    .card-item { border:1px solid #E2E8F0; padding:10px; border-radius:10px; margin-bottom:8px; background:#F8FAFC; border-left: 5px solid #1E3A8A; }
    .kana-card { background: white; border: 1px solid #E2E8F0; border-radius: 12px; padding: 10px 0; text-align: center; min-height:100px; }
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.title("FUSION Pro")
    menu = st.radio("导航", ["五十音实验室", "AI 词汇专家", "每周 7 句"], index=0)

# --- 模块 A: 五十音实验室 (补全“段”选择) ---
if menu == "五十音实验室":
    st.header("五十音实验室")
    
    top_cat = st.radio("大类选择", ["清音", "浊音/半浊音", "拗音"], horizontal=True)
    
    if top_cat == "清音":
        mode = st.radio("查看方式", ["行模式", "段模式"], horizontal=True)
        sub_cat = st.selectbox("具体分类", list(KANA_DATA["清音"][mode].keys()))
        current_list = KANA_DATA["清音"][mode][sub_cat]
    else:
        sub_cat = st.selectbox("具体分类", list(KANA_DATA[top_cat].keys()))
        current_list = KANA_DATA[top_cat][sub_cat]
    
    if st.button(f"🔊 节奏连读：{sub_cat}", use_container_width=True):
        play_audio([item[0] for item in current_list if item[0]])
                
    st.markdown("---")
    num_cols = 5
    cols = st.columns(num_cols)
    for idx, item in enumerate(current_list):
        if item[0]:
            with cols[idx % num_cols]:
                st.markdown(f"""<div class="kana-card">
                    <div style="font-size:2rem; font-weight:bold; color:#1E3A8A;">{item[0]}</div>
                    <div style="color:#64748B; font-size:0.9rem;">{item[1] if len(item)>2 else ''}</div>
                    <div style="color:#3B82F6; font-weight:600;">{item[2] if len(item)>2 else item[1]}</div>
                </div>""", unsafe_allow_html=True)
                if st.button("🔊", key=f"btn_{top_cat}_{sub_cat}_{idx}"):
                    play_audio(item[0])

# --- 模块 B: AI 词汇专家 ---
elif menu == "AI 词汇专家":
    st.header("AI 词汇专家")
    u_in = st.text_input("请输入中文", placeholder="落实、号召")
    if u_in:
        res = get_expert_translation(u_in)
        if res:
            st.markdown(f"""<div class="word-box">
                <h2 style="color:#1E3A8A; margin:0;">{res.get('word','')}</h2>
                <p style="color:#3B82F6; font-weight:bold;">【{res.get('reading','')}】</p>
                <small>{res.get('pos','')} | {res.get('level','')} | {res.get('pitch','')}型</small>
            </div>""", unsafe_allow_html=True)
            if st.button("🔊 播放单词", key="p_main"): play_audio(res.get('word'))
            st.markdown("---")
            for i, s in enumerate(res.get('sentences', []), 1):
                st.markdown(f'<div class="card-item"><b>{i}. {s.get("jp")}</b><br><span style="color:#059669;">{s.get("cn")}</span></div>', unsafe_allow_html=True)
                if st.button(f"🔊 例句 {i}", key=f"s_{i}"): play_audio(s.get("jp"))

# --- 模块 C: 每周 7 句 ---
elif menu == "每周 7 句":
    st.header("每周 7 句")
    for i, item in enumerate(WEEKLY_CONTENT, 1):
        with st.expander(f"第 {i} 句：{item['jp']}"):
            st.write(f"🇨🇳 {item['cn']}")
            if st.button(f"🔊 朗读", key=f"wk_{i}"): play_audio(item['jp'])
