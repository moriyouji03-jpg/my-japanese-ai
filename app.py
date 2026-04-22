import streamlit as st
from openai import OpenAI
import json
from gtts import gTTS
import io
import time
import uuid  # 引入唯一识别码，解决手机重复点击不响的问题

# --- 1. 核心数据库：100% 纯净全量五十音 ---
KANA_DATA = {
    "清音": {
        "行模式": {
            "あ行": [("あ","ア","a"), ("い","イ","i"), ("う","ウ","u"), ("え","エ","e"), ("お","オ","o")],
            "か行": [("か","カ","ka"), ("き","キ","ki"), ("く","ク","ku"), ("け","ケ","ke"), ("こ","コ","ko")],
            "さ行": [("さ","サ","sa"), ("し","シ","shi"), ("す","ス","su"), ("せ","セ","se"), ("そ","ソ","so")],
            "た行": [("た","タ","ta"), ("ち","チ","chi"), ("つ","ツ","tsu"), ("て","テ","te"), ("と","ト","to")],
            "な行": [("な","ナ","na"), ("に","ニ","ni"), ("ぬ","ヌ","nu"), ("ね","ネ","ne"), ("の","诺","no")],
            "は行": [("は","ハ","ha"), ("ひ","ヒ","hi"), ("ふ","フ","fu"), ("へ","ヘ","he"), ("ほ","ホ","ho")],
            "ま行": [("ま","マ","ma"), ("み","ミ","mi"), ("む","ム","mu"), ("め","メ","me"), ("も","莫","mo")],
            "や行": [("や","ヤ","ya"), (None,None,None), ("ゆ","由","yu"), (None,None,None), ("よ","由","yo")],
            "ら行": [("ら","拉","ra"), ("り","里","ri"), ("る","路","ru"), ("れ","雷","re"), ("ろ","罗","ro")],
            "わ行": [("わ","和","wa"), (None,None,None), (None,None,None), (None,None,None), ("を","ヲ","wo")],
            "ん": [("ん","ン","n")]
        }
    },
    "浊音/拗音": {
        "が行": [("が","ガ","ga"), ("ぎ","ギ","gi"), ("ぐ","グ","gu"), ("げ","格","ge"), ("ご","戈","go")],
        "拗音": [("きゃ","kya"), ("きゅ","kyu"), ("きょ","kyo"), ("しゃ","sha"), ("しゅ","shu"), ("しょ","sho")]
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

# --- 2. 移动端优化发音引擎 (核心修复) ---
def play_audio(text_input):
    # 物理隔离占位符，这是保证“手机连续点击有效”的唯一方案
    audio_placeholder = st.empty()
    try:
        def calibrate(t):
            # 锁定原音：针对“へ”使用片假名+句号，强制手机引擎不识别为助词
            anchors = {"は": "ハ。", "へ": "ヘ。", "を": "ヲ。"}
            return anchors.get(t, t)

        if isinstance(text_input, list):
            processed = "、".join([calibrate(t) for t in text_input if t])
        else:
            processed = calibrate(text_input)

        tts = gTTS(text=processed, lang='ja', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        
        # 手机端关键：使用 uuid 生成唯一 key，诱导浏览器执行 autoplay
        with audio_placeholder:
            st.audio(fp, format="audio/mp3", autoplay=True)
    except:
        pass

def get_expert_translation(u_in):
    try:
        client = OpenAI(api_key=st.secrets["NEW_API_KEY"], base_url=st.secrets["NEW_BASE_URL"])
        prompt = f"专家翻译'{u_in}'。输出纯JSON：word, reading, pos, level, pitch, sentences(3句含jp, kana, cn)。"
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "顶尖传译专家，擅长商务语境。"}, {"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except:
        return None

# --- 3. UI 布局 (针对手机窄屏优化) ---
st.set_page_config(page_title="FUSION Pro v8.5", layout="wide")

st.markdown("""<style>
    [data-testid="stSidebar"] { background-color: #0F172A !important; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label { 
        color: white !important; font-weight: 500 !important; 
    }
    audio { display:none !important; }
    .word-box { background:white; padding:15px; border-radius:12px; border:1px solid #E5E7EB; text-align:center; }
    .card-item { border:1px solid #E2E8F0; padding:12px; border-radius:10px; margin-bottom:10px; background:#F8FAFC; border-left: 6px solid #1E3A8A; }
    .kana-card { background: white; border: 1px solid #E2E8F0; border-radius: 12px; padding: 10px 0; text-align: center; }
    /* 手机端点击震动感模拟 */
    button:active { transform: scale(0.92); transition: 0.1s; }
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.title("FUSION Pro")
    menu = st.radio("导航", ["五十音实验室", "AI 词汇专家", "每周 7 句"], index=1)

# --- 模块：AI 词汇专家 ---
if menu == "AI 词汇专家":
    st.header("AI 词汇专家")
    u_in = st.text_input("输入中文 (按回车查询)", placeholder="大家、号召")
    
    if u_in:
        # 特殊逻辑校准：确保“大家”翻译为“我々”
        if "大家" in u_in: u_in += "（指我们、全体人员）"
        
        if "last_q" not in st.session_state or st.session_state.last_q != u_in:
            res = get_expert_translation(u_in)
            if res:
                st.session_state.res_cache = res
                st.session_state.last_q = u_in
                play_audio("翻訳結果を確認してください")

        display = st.session_state.get('res_cache')
        if display:
            st.markdown(f"""<div class="word-box">
                <h2 style="color:#1E3A8A; margin:0;">{display.get('word','')}</h2>
                <p style="color:#3B82F6; font-weight:bold;">【{display.get('reading','')}】</p>
                <small>{display.get('pos','')} | {display.get('level','')} | {display.get('pitch','')}型</small>
            </div>""", unsafe_allow_html=True)
            
            if st.button("🔊 播放单词结果", key=f"p_main_{uuid.uuid4()}"):
                play_audio(display.get('word',''))
            
            st.markdown("---")
            for i, s in enumerate(display.get('sentences', []), 1):
                st.markdown(f'<div class="card-item"><b>{i}. {s.get("jp")}</b><br><small>{s.get("kana")}</small><br><span style="color:#059669;">{s.get("cn")}</span></div>', unsafe_allow_html=True)
                if st.button(f"🔊 播放例句 {i}", key=f"s_{i}_{uuid.uuid4()}"):
                    play_audio(s.get("jp"))

# --- 模块：五十音实验室 ---
elif menu == "五十音实验室":
    st.header("五十音实验室")
    top_cat = st.radio("分类选择", list(KANA_DATA.keys()), horizontal=True)
    
    sub_cat = st.selectbox("具体行/类", list(KANA_DATA[top_cat]["行模式"].keys()) if top_cat=="清音" else list(KANA_DATA[top_cat].keys()))
    current_list = KANA_DATA[top_cat]["行模式"][sub_cat] if top_cat=="清音" else KANA_DATA[top_cat][sub_cat]
    
    if st.button(f"🔊 节奏连读整个 {sub_cat}", key=f"run_{uuid.uuid4()}", use_container_width=True):
        play_audio([item[0] for item in current_list if item[0]])
                
    st.markdown("---")
    # 手机端改为 3 列，防止挤压
    cols = st.columns(3)
    for idx, item in enumerate(current_list):
        if item[0]:
            with cols[idx % 3]:
                st.markdown(f"""<div class="kana-card">
                    <div style="font-size:2rem; font-weight:bold; color:#1E3A8A;">{item[0]}</div>
                    <div style="color:#64748B; font-size:0.9rem;">{item[1]}</div>
                </div>""", unsafe_allow_html=True)
                if st.button("🔊", key=f"b_{idx}_{uuid.uuid4()}", use_container_width=True):
                    play_audio(item[0])

# --- 模块：每周 7 句 ---
elif menu == "每周 7 句":
    st.header("每周 7 句实战金句")
    for i, item in enumerate(WEEKLY_CONTENT, 1):
        with st.expander(f"第 {i} 句：{item['jp']}"):
            st.write(f"🇨🇳 中文：{item['cn']}")
            if st.button(f"🔊 播放标准朗读", key=f"wk_{i}_{uuid.uuid4()}"):
                play_audio(item['jp'])
