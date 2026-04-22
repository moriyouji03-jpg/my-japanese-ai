import streamlit as st
from openai import OpenAI
import json
from gtts import gTTS
import io

# --- 1. 核心数据库：100% 纯净版 ---
KANA_DATA = {
    "清音": {
        "行模式": {
            "あ行": [("あ","ア","a"), ("い","イ","i"), ("う","ウ","u"), ("え","エ","e"), ("お","オ","o")],
            "か行": [("か","カ","ka"), ("き","キ","ki"), ("く","ク","ku"), ("け","ケ","ke"), ("こ","コ","ko")],
            "さ行": [("さ","サ","sa"), ("し","シ","shi"), ("す","ス","su"), ("せ","セ","se"), ("そ","ソ","so")],
            "た行": [("た","タ","ta"), ("ち","チ","chi"), ("つ","ツ","tsu"), ("て","テ","te"), ("と","ト","to")],
            "な行": [("な","ナ","na"), ("に","ニ","ni"), ("ぬ","ヌ","nu"), ("ね","ネ","ne"), ("の","ノ","no")],
            "は行": [("は","ハ","ha"), ("ひ","ヒ","hi"), ("ふ","フ","fu"), ("へ","ヘ","he"), ("ほ","ホ","ho")],
            "ま行": [("ま","マ","ma"), ("み","ミ","mi"), ("む","ム","mu"), ("め","メ","me"), ("も","莫","mo")],
            "や行": [("や","ヤ","ya"), (None,None,None), ("ゆ","由","yu"), (None,None,None), ("よ","由","yo")],
            "ら行": [("ら","拉","ra"), ("り","里","ri"), ("る","路","ru"), ("れ","雷","re"), ("ろ","罗","ro")],
            "わ行": [("わ","和","wa"), (None,None,None), (None,None,None), (None,None,None), ("を","ヲ","wo")],
            "ん": [("ん","ン","n"), (None,None,None), (None,None,None), (None,None,None), (None,None,None)]
        },
        "段模式": {
            "あ段": [("あ","ア","a"), ("か","カ","ka"), ("さ","サ","sa"), ("た","塔","ta"), ("な","纳","na"), ("は","哈","ha"), ("ま","马","ma"), ("压","亚","ya"), ("ら","拉","ra"), ("わ","和","wa")],
            "い段": [("い","イ","i"), ("き","基","ki"), ("し","希","shi"), ("ち","七","chi"), ("に","尼","ni"), ("ひ","希","hi"), ("み","米","mi"), ("り","里","ri")],
            "う段": [("う","乌","u"), ("く","苦","ku"), ("す","斯","su"), ("つ","促","tsu"), ("ぬ","努","nu"), ("ふ","夫","fu"), ("む","姆","mu"), ("ゆ","由","yu"), ("る","路","ru")],
            "え段": [("え","诶","e"), ("け","开","ke"), ("せ","塞","se"), ("て","特","te"), ("ね","内","ne"), ("へ","黑","he"), ("め","梅","me"), ("れ","雷","re")],
            "お段": [("お","哦","o"), ("こ","阔","ko"), ("そ","索","so"), ("と","托","to"), ("の","诺","no"), ("ほ","霍","ho"), ("も","莫","mo"), ("よ","由","yo"), ("ろ","罗","ro")]
        }
    },
    "浊音/半浊音": {
        "が行": [("加","ガ","ga"), ("ぎ","吉","gi"), ("ぐ","古","gu"), ("げ","格","ge"), ("ご","戈","go")],
        "ざ行": [("ざ","扎","za"), ("じ","吉","ji"), ("ず","兹","zu"), ("ぜ","则","ze"), ("ぞ","左","zo")],
        "だ行": [("だ","达","da"), ("ぢ","吉","ji"), ("づ","兹","zu"), ("で","德","de"), ("ど","多","do")],
        "ば行": [("ば","巴","ba"), ("び","毕","bi"), ("ぶ","布","bu"), ("べ","贝","be"), ("ぼ","波","bo")],
        "ぱ行": [("ぱ","帕","pa"), ("ぴ","皮","pi"), ("ぷ","普","pu"), ("ぺ","佩","pe"), ("ぽ","波","po")]
    }
}

WEEKLY_CONTENT = [
    {"jp": "私たちは昨日、図書館で本を読みました。", "cn": "我们昨天在图书馆读书了。"},
    {"jp": "私は毎日コーヒーを飲みます。", "cn": "我每天喝咖啡。"},
    {"jp": "これは日本語の本です。", "cn": "这是日语书。"},
    {"jp": "駅はあそこにあります。", "cn": "车站就在那儿。"},
    {"jp": "一緒に昼ご飯を食べませんか。", "cn": "要不要一起吃午饭？"},
    {"jp": "明日も会社に行きます。", "cn": "明天也去公司。"},
    {"jp": "このケーキはとても美味しいです。", "cn": "这个蛋糕非常好吃。"}
]

# --- 2. 语音引擎 ---
def play_audio(text_input):
    audio_placeholder = st.empty()
    try:
        def calibrate(t):
            anchors = {"は": "ハ", "へ": "ヘ。", "を": "ヲ"}
            return anchors.get(t, t)
        processed = "、".join([calibrate(t) for t in text_input if t]) if isinstance(text_input, list) else calibrate(text_input)
        tts = gTTS(text=processed, lang='ja', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        with audio_placeholder:
            st.audio(fp, format="audio/mp3", autoplay=True)
    except:
        pass

def get_expert_translation(u_in):
    try:
        client = OpenAI(api_key=st.secrets["NEW_API_KEY"], base_url=st.secrets["NEW_BASE_URL"])
        # 优化后的深度角色提示词
        prompt = f"""你是一名拥有20年经验的中日同声传译专家。
请翻译词汇：'{u_in}'。
注意：如果是“大家”、“号召”等具有公文色彩的词，请翻译为地道的日企公文表达（如将“大家”处理为“我々”或“皆様”，将“号召”处理为“呼びかける”或“勧誘”）。
输出纯JSON格式：word, reading, pos, level, pitch, sentences(3句含jp, kana, cn)。"""
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "You are a top-tier Japanese translator specialist."}, {"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        return json.loads(response.choices[0].message.content)
    except:
        return None

# --- 3. UI 布局 ---
st.set_page_config(page_title="FUSION Pro v7.7", layout="wide")

st.markdown("""<style>
    [data-testid="stSidebar"] { background-color: #0F172A !important; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label { color: white !important; font-weight: 500 !important; }
    audio { display:none !important; }
    .word-box { background:white; padding:15px; border-radius:12px; border:1px solid #E5E7EB; text-align:center; }
    .card-item { border:1px solid #E2E8F0; padding:10px; border-radius:10px; margin-bottom:8px; background:#F8FAFC; border-left: 5px solid #1E3A8A; }
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.title("FUSION Pro")
    menu = st.radio("功能模块", ["AI 词汇专家", "五十音实验室", "每周 7 句"], index=0)

if menu == "AI 词汇专家":
    st.header("AI 词汇专家 (专业校准版)")
    u_in = st.text_input("请输入中文词汇 (回车查询)", placeholder="大家、号召、椅子")
    
    if u_in:
        if "last_query" not in st.session_state or st.session_state.last_query != u_in:
            res = get_expert_translation(u_in)
            if res:
                st.session_state.res_cache = res
                st.session_state.last_query = u_in
                play_audio("翻訳結果を確認してください")

        display = st.session_state.get('res_cache')
        if display:
            st.markdown(f"""<div class="word-box">
                <h2 style="color:#1E3A8A; margin:0;">{display.get('word','')}</h2>
                <p style="color:#3B82F6; font-weight:bold;">【{display.get('reading','')}】</p>
                <small>{display.get('pos','')} | {display.get('level','')} | {display.get('pitch','')}型</small>
            </div>""", unsafe_allow_html=True)
            if st.button("🔊 播放单词结果", key="p_main"):
                play_audio(display.get('word',''))
            
            st.markdown("---")
            for i, s in enumerate(display.get('sentences', []), 1):
                st.markdown(f'<div class="card-item"><b>{i}. {s.get("jp")}</b><br><small>{s.get("kana")}</small><br><span style="color:#059669;">{s.get("cn")}</span></div>', unsafe_allow_html=True)
                if st.button(f"🔊 播放例句 {i}", key=f"s_{i}"):
                    play_audio(s.get("jp"))

elif menu == "五十音实验室":
    st.header("五十音实验室")
    top_cat = st.radio("分类", ["清音", "浊音/半浊音"], horizontal=True)
    if top_cat == "清音":
        mode = st.radio("模式", ["行模式", "段模式"], horizontal=True)
        sub_cat = st.selectbox("选择", list(KANA_DATA["清音"][mode].keys()))
        current_list = KANA_DATA["清音"][mode][sub_cat]
    else:
        sub_cat = st.selectbox("选择", list(KANA_DATA[top_cat].keys()))
        current_list = KANA_DATA[top_cat][sub_cat]
    
    if st.button(f"🔊 节奏连读：{sub_cat}", use_container_width=True):
        play_audio([item[0] for item in current_list if item[0]])
                
    st.markdown("---")
    cols = st.columns(5)
    for idx, item in enumerate(current_list):
        if item[0]:
            with cols[idx % 5]:
                st.markdown(f'<div style="text-align:center; padding:10px; border:1px solid #eee; border-radius:8px;"><b>{item[0]}</b><br><small>{item[1]}</small></div>', unsafe_allow_html=True)
                if st.button("🔊", key=f"b_{idx}"): play_audio(item[0])

elif menu == "每周 7 句":
    st.header("每周 7 句")
    for i, item in enumerate(WEEKLY_CONTENT, 1):
        with st.expander(f"第 {i} 句：{item['jp']}"):
            st.write(f"🇨🇳 {item['cn']}")
            if st.button(f"🔊 播放", key=f"wk_{i}"): play_audio(item['jp'])
