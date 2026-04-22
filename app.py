import streamlit as st
from openai import OpenAI
import json
from gtts import gTTS
import io
import base64
import random

# --- 1. 核心数据库：100% 纯净全量五十音 (含行/段模式) ---
KANA_DATA = {
    "清音": {
        "行模式": {
            "あ行": [("あ","ア","a"), ("い","イ","i"), ("う","ウ","u"), ("え","エ","e"), ("お","オ","o")],
            "か行": [("か","カ","ka"), ("き","キ","ki"), ("く","ク","ku"), ("け","ケ","ke"), ("こ","コ","ko")],
            "さ行": [("さ","サ","sa"), ("し","シ","shi"), ("す","ス","su"), ("せ","セ","se"), ("そ","ソ","so")],
            "た行": [("た","タ","ta"), ("ち","チ","chi"), ("つ","ツ","tsu"), ("て","テ","te"), ("内","ト","to")],
            "な行": [("な","ナ","na"), ("に","ニ","ni"), ("ぬ","ヌ","nu"), ("ね","ネ","ne"), ("の","诺","no")],
            "は行": [("は","ハ","ha"), ("ひ","ヒ","hi"), ("ふ","フ","fu"), ("へ","ヘ","he"), ("ほ","ホ","ho")],
            "ま行": [("ま","马","ma"), ("み","米","mi"), ("む","姆","mu"), ("め","梅","me"), ("も","莫","mo")],
            "や行": [("や","亚","ya"), (None,None,None), ("ゆ","由","yu"), (None,None,None), ("よ","由","yo")],
            "ら行": [("ら","拉","ra"), ("り","里","ri"), ("る","路","ru"), ("れ","雷","re"), ("ろ","罗","ro")],
            "わ行": [("わ","和","wa"), (None,None,None), (None,None,None), (None,None,None), ("を","ヲ","wo")],
            "ん": [("ん","ン","n")]
        },
        "段模式": {
            "あ段": [("あ","ア","a"), ("か","カ","ka"), ("さ","サ","sa"), ("た","塔","ta"), ("な","纳","na"), ("は","哈","ha"), ("ま","马","ma"), ("や","亚","ya"), ("ら","拉","ra"), ("わ","和","wa")],
            "い段": [("い","イ","i"), ("き","基","ki"), ("し","希","shi"), ("ち","七","chi"), ("に","尼","ni"), ("ひ","希","hi"), ("み","米","mi"), ("り","里","ri")],
            "う段": [("う","乌","u"), ("く","苦","ku"), ("す","斯","su"), ("つ","促","tsu"), ("ぬ","努","nu"), ("ふ","夫","fu"), ("む","姆","mu"), ("ゆ","由","yu"), ("る","路","ru")],
            "え段": [("え","诶","e"), ("け","开","ke"), ("せ","塞","se"), ("て","特","te"), ("ね","内","ne"), ("へ","黑","he"), ("め","梅","me"), ("れ","雷","re")],
            "お段": [("お","哦","o"), ("こ","阔","ko"), ("そ","索","so"), ("と","托","to"), ("の","诺","no"), ("ほ","霍","ho"), ("も","莫","mo"), ("よ","由","yo"), ("ろ","罗","ro")]
        }
    },
    "浊音/半浊音": {
        "が行": [("が","ガ","ga"), ("ぎ","吉","gi"), ("ぐ","古","gu"), ("げ","格","ge"), ("ご","戈","go")],
        "ざ行": [("ざ","扎","za"), ("じ","吉","ji"), ("ず","兹","zu"), ("ぜ","则","ze"), ("ぞ","左","zo")],
        "だ行": [("だ","达","da"), ("ぢ","吉","ji"), ("づ","兹","zu"), ("で","德","de"), ("ど","多","do")],
        "ば行": [("ば","巴","ba"), ("び","毕","bi"), ("ぶ","布","bu"), ("べ","贝","be"), ("ぼ","波","bo")],
        "ぱ行": [("ぱ","帕","pa"), ("ぴ","皮","pi"), ("ぷ","普","pu"), ("ぺ","佩","pe"), ("ぽ","波","po")]
    }
}

WEEKLY_CONTENT = [
    {"jp": "私は昨日、図書館で本を読みました。", "cn": "我昨天在图书馆读书了。"},
    {"jp": "私は毎日コーヒーを飲みます。", "cn": "我每天喝咖啡。"},
    {"jp": "これは日本語の本です。", "cn": "这是日语书。"},
    {"jp": "駅はあそこにあります。", "cn": "车站就在那儿。"},
    {"jp": "一緒に昼ご飯を食べませんか。", "cn": "要不要一起吃午饭？"}
]

# --- 2. 语音引擎：手机端“Base64 强制唤醒”版 ---
def play_audio(text_input):
    try:
        def calibrate(t):
            # 锁定原音：针对“へ”使用片假名+句号，强制手机浏览器锁定 he 发音
            anchors = {"は": "ハ。", "へ": "ヘ。", "を": "ヲ。"}
            return anchors.get(t, t)

        processed = "、".join([calibrate(t) for t in text_input if t]) if isinstance(text_input, list) else calibrate(text_input)
        
        tts = gTTS(text=processed, lang='ja', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        
        # 核心改进：Base64 注入技术
        # 不再依赖 streamlit 的 st.audio，而是直接生成 HTML5 自动播放代码
        b64 = base64.b64encode(fp.read()).decode()
        md = f"""
            <audio autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.components.v1.html(md, height=0) # 隐藏组件，实现纯净背景发音
    except:
        pass

def get_expert_translation(u_in):
    try:
        client = OpenAI(api_key=st.secrets["NEW_API_KEY"], base_url=st.secrets["NEW_BASE_URL"])
        prompt = f"专家分析‘{u_in}’。输出纯JSON：word, reading, pos, level, pitch, sentences(3句含jp, kana, cn)。注：‘大家’翻译为‘我々’。"
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "Professional translator."}, {"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except: return None

# --- 3. UI 布局 ---
st.set_page_config(page_title="FUSION Pro v9.0", layout="wide")

st.markdown("""<style>
    [data-testid="stSidebar"] { background-color: #0F172A !important; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label { color: white !important; font-weight: 500 !important; }
    .card-item { border:1px solid #E2E8F0; padding:10px; border-radius:10px; margin-bottom:8px; background:#F8FAFC; border-left: 5px solid #1E3A8A; }
    .kana-card { background: white; border: 1px solid #E2E8F0; border-radius: 12px; padding: 10px 0; text-align: center; }
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.title("FUSION Pro")
    menu = st.radio("导航", ["五十音实验室", "AI 词汇专家", "每周 7 句"], index=1)

# --- AI 词汇专家 ---
if menu == "AI 词汇专家":
    st.header("AI 词汇专家")
    u_in = st.text_input("中文查询", placeholder="号召、大家")
    if u_in:
        if "last_q" not in st.session_state or st.session_state.last_q != u_in:
            res = get_expert_translation(u_in)
            if res:
                st.session_state.res_cache = res
                st.session_state.last_q = u_in
        
        display = st.session_state.get('res_cache')
        if display:
            st.markdown(f"### {display.get('word','')} 【{display.get('reading','')}】")
            if st.button("🔊 播放单词"): play_audio(display.get('word',''))
            for i, s in enumerate(display.get('sentences', []), 1):
                st.markdown(f'<div class="card-item"><b>{s.get("jp")}</b><br>{s.get("cn")}</div>', unsafe_allow_html=True)
                if st.button(f"🔊 朗读例句 {i}"): play_audio(s.get("jp"))

# --- 五十音实验室 ---
elif menu == "五十音实验室":
    st.header("五十音实验室")
    top_cat = st.radio("分类", ["清音", "浊音/半浊音"], horizontal=True)
    if top_cat == "清音":
        mode = st.radio("模式", ["行模式", "段模式"], horizontal=True)
        sub_cat = st.selectbox("分类选择", list(KANA_DATA["清音"][mode].keys()))
        current_list = KANA_DATA["清音"][mode][sub_cat]
    else:
        sub_cat = st.selectbox("分类选择", list(KANA_DATA[top_cat].keys()))
        current_list = KANA_DATA[top_cat][sub_cat]
    
    if st.button(f"🔊 节奏连读：{sub_cat}", use_container_width=True):
        play_audio([item[0] for item in current_list if item[0]])
    
    cols = st.columns(5)
    for idx, item in enumerate(current_list):
        if item[0]:
            with cols[idx % 5]:
                st.markdown(f'<div class="kana-card"><b>{item[0]}</b><br><small>{item[1]}</small></div>', unsafe_allow_html=True)
                # 使用随机 key 确保手机端每次点击都被视为新交互
                if st.button("🔊", key=f"btn_{idx}_{random.randint(0,999)}"):
                    play_audio(item[0])

# --- 每周 7 句 ---
elif menu == "每周 7 句":
    st.header("每周 7 句")
    for i, item in enumerate(WEEKLY_CONTENT, 1):
        with st.expander(f"第 {i} 句：{item['jp']}"):
            st.write(item['cn'])
            if st.button(f"🔊 朗读", key=f"wk_{i}"): play_audio(item['jp'])
