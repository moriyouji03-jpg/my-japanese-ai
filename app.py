import streamlit as st
from openai import OpenAI
import json
from gtts import gTTS
import io
import time

# --- 1. 核心数据库：地毯式清洗，100% 移除杂质汉字 ---
KANA_DATA = {
    "清音-行": {
        "あ行": [("あ","ア","a"), ("い","イ","i"), ("う","ウ","u"), ("え","エ","e"), ("お","オ","o")],
        "か行": [("か","カ","ka"), ("き","キ","ki"), ("く","ク","ku"), ("け","ケ","ke"), ("こ","コ","ko")],
        "さ行": [("さ","サ","sa"), ("し","シ","shi"), ("す","ス","su"), ("せ","セ","se"), ("そ","ソ","so")],
        "た行": [("た","タ","ta"), ("ち","チ","chi"), ("つ","ツ","tsu"), ("て","テ","te"), ("と","ト","to")],
        "な行": [("な","ナ","na"), ("in","ニ","ni"), ("ぬ","ヌ","nu"), ("ね","内","ne"), ("の","诺","no")],
        "は行": [("は","ハ","ha"), ("ひ","ヒ","hi"), ("ふ","フ","fu"), ("へ","ヘ","he"), ("ほ","ホ","ho")],
        "ま行": [("ま","マ","ma"), ("米","ミ","mi"), ("姆","ム","mu"), ("め","メ","me"), ("莫","莫","mo")],
        "や行": [("や","ヤ","ya"), (None,None,None), ("ゆ","ユ","yu"), (None,None,None), ("よ","ヨ","yo")],
        "ら行": [("ら","拉","ra"), ("り","リ","ri"), ("る","路","ru"), ("れ","雷","re"), ("ろ","罗","ro")],
        "わ行": [("わ","ワ","wa"), (None,None,None), (None,None,None), (None,None,None), ("を","ヲ","wo")],
        "ん": [("ん","ン","n"), (None,None,None), (None,None,None), (None,None,None), (None,None,None)]
    },
    "清音-段": {
        "あ段": [("あ","ア","a"), ("か","カ","ka"), ("さ","サ","sa"), ("た","塔","ta"), ("な","ナ","na"), ("は","ハ","ha"), ("ま","马","ma"), ("や","亚","ya"), ("ら","拉","ra"), ("わ","和","wa")],
        "い段": [("い","イ","i"), ("き","キ","ki"), ("し","希","shi"), ("ち","七","chi"), ("に","尼","ni"), ("ひ","希","hi"), ("米","ミ","mi"), ("り","里","ri")],
        "う段": [("う","乌","u"), ("く","苦","ku"), ("す","斯","su"), ("つ","促","tsu"), ("ぬ","努","nu"), ("ふ","夫","fu"), ("む","姆","mu"), ("ゆ","由","yu"), ("る","路","ru")],
        "え段": [("え","诶","e"), ("け","开","ke"), ("せ","塞","se"), ("て","特","te"), ("ね","内","ne"), ("へ","黑","he"), ("め","梅","me"), ("れ","雷","re")],
        "お段": [("お","哦","o"), ("こ","阔","ko"), ("そ","索","so"), ("と","托","to"), ("の","诺","no"), ("ほ","霍","ho"), ("も","莫","mo"), ("よ","由","yo"), ("ろ","罗","ro")]
    },
    "浊音/半浊音": {
        "が行": [("が","ガ","ga"), ("ぎ","ギ","gi"), ("ぐ","グ","gu"), ("げ","格","ge"), ("ご","戈","go")],
        "ざ行": [("ざ","扎","za"), ("じ","吉","ji"), ("ず","兹","zu"), ("ぜ","则","ze"), ("ぞ","左","zo")],
        "だ行": [("だ","达","da"), ("ぢ","吉","ji"), ("づ","兹","zu"), ("で","得","de"), ("ど","多","do")],
        "ば行": [("ば","巴","ba"), ("び","毕","bi"), ("ぶ","布","bu"), ("べ","贝","be"), ("ぼ","波","bo")],
        "ぱ行": [("ぱ","帕","pa"), ("ぴ","皮","pi"), ("ぷ","普","pu"), ("ぺ","佩","pe"), ("ぽ","波","po")]
    },
    "拗音体系": {
        "清拗音": [("きゃ","キャ","kya"), ("きゅ","キュ","kyu"), ("きょ","キョ","kyo"), ("しゃ","シャ","sha"), ("しゅ","シュ","shu"), ("しょ","ショ","sho"), ("ちゃ","チャ","cha"), ("ちゅ","チュ","chu"), ("ちょ","チョ","cho")],
        "浊拗音": [("ぎゃ","ギャ","gya"), ("ぎゅ","ギュ","gyu"), ("ぎょ","ギョ","gyo"), ("じゃ","ジャ","ja"), ("じゅ","ジュ","ju"), ("じょ","ジョ","jo")],
        "半浊拗音": [("ぴゃ","ピャ","pya"), ("ぴゅ","ピゅ","pyu"), ("ぴょ","ピょ","pyo")]
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

# --- 2. 发音引擎核心 (物理强制重置版 - 还原 v4.5 架构) ---
def play_audio(text_input):
    # 使用占位符强行清空状态
    audio_placeholder = st.empty()
    try:
        def calibrate(t):
            # 锁定原音：针对“へ”和“は”使用强力映射
            if t == "へ": return "ヘー" 
            if t == "は": return "ハー"
            return t

        if isinstance(text_input, list):
            processed_text = " 、 ".join([calibrate(t) for t in text_input if t])
        else:
            processed_text = calibrate(text_input)

        tts = gTTS(text=processed_text, lang='ja', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        
        # 物理注入：直接生成带自动播放的音频组件，去掉 UUID，使用稳定 key
        with audio_placeholder:
            st.audio(fp, format="audio/mp3", autoplay=True)
    except:
        pass

def get_expert_translation(u_in):
    try:
        client = OpenAI(api_key=st.secrets["NEW_API_KEY"], base_url=st.secrets["NEW_BASE_URL"])
        prompt = f"作为专业翻译，分析'{u_in}'。JSON结构：word, reading, pos, level, pitch, sentences(3句)。"
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "顶尖专家，输出纯JSON。"}, {"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except: return None

# --- 3. UI 布局与样式 (恢复 v4.5 的海军蓝风格) ---
st.set_page_config(page_title="FUSION Pro v5.6", layout="wide")

st.markdown("""<style>
    [data-testid="stSidebar"] { background-color: #0F172A !important; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span { color: white !important; font-weight: 500; }
    audio { display:none !important; }
    .word-box { background:white; padding:15px; border-radius:12px; border:1px solid #E5E7EB; text-align:center; }
    .card-item { border:1px solid #E2E8F0; padding:12px; border-radius:10px; margin-bottom:10px; background:#F8FAFC; border-left: 6px solid #1E3A8A; }
    .kana-card { background: white; border: 1px solid #E2E8F0; border-radius: 12px; padding: 10px 0; text-align: center; }
    .hiragana { font-size: 2rem; font-weight: bold; color: #1E3A8A; line-height: 1.1; }
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.title("FUSION Pro")
    menu = st.radio("功能模块", ["AI 词汇专家", "五十音实验室", "每周 7 句"], index=1)

# --- 模块：五十音实验室 ---
if menu == "五十音实验室":
    st.header("五十音实验室")
    # 彻底修复 KeyError：使用最直接的 list 转换
    tab_list = list(KANA_DATA.keys())
    selected_tab = st.segmented_control("音系选择", tab_list, default=tab_list[0])
    
    if selected_tab in KANA_DATA:
        sub_cat = st.selectbox("分类选择", list(KANA_DATA[selected_tab].keys()))
        current_list = KANA_DATA[selected_tab][sub_cat]
        
        # 节奏连读：锁定 key
        if st.button(f"🔊 节奏连读整个【{sub_cat}】", use_container_width=True, key=f"run_all_{sub_cat}"):
            play_audio([item[0] for item in current_list if item[0]])
                
        st.markdown("---")
        num_cols = 5 if "行" in sub_cat or "段" in sub_cat or "浊" in sub_cat else 3
        cols = st.columns(num_cols)
        for idx, item in enumerate(current_list):
            if item[0]:
                with cols[idx % num_cols]:
                    st.markdown(f"""<div class="kana-card">
                        <div class="hiragana">{item[0]}</div>
                        <div style="color:#64748B; font-size:0.9rem;">{item[1]}</div>
                        <div style="color:#3B82F6; font-weight:600;">{item[2]}</div>
                    </div>""", unsafe_allow_html=True)
                    # 使用稳定 key，仅在音频内部重置状态
                    if st.button("🔊", key=f"btn_{sub_cat}_{idx}", use_container_width=True):
                        play_audio(item[0])

# --- 模块：AI 词汇专家 ---
elif menu == "AI 词汇专家":
    st.header("AI 词汇专家")
    u_in = st.text_input("请输入中文词汇", placeholder="落实、号召")
    query = u_in.strip() if u_in else "你好"
    
    if query:
        if "last_query" not in st.session_state or st.session_state.last_query != query:
            res = get_expert_translation(query)
            if res:
                st.session_state.res_cache = res
                st.session_state.last_query = query
                play_audio("これについて、以下の日本語が考えられます")

        display = st.session_state.get('res_cache')
        if display:
            st.markdown(f"""<div class="word-box" style="max-width:650px; margin:auto;">
                <h1 style="color:#1E3A8A; margin:0;">{display.get('word','')}</h1>
                <p style="color:#3B82F6; font-size:1.2rem; font-weight:bold; margin:5px 0;">【{display.get('reading','')}】</p>
                <div style="font-size:0.8rem; color:#64748B;">🏷️ {display.get('pos','')} | 🏆 {display.get('level','')} | 📈 {display.get('pitch','')}型</div>
            </div>""", unsafe_allow_html=True)
            
            if st.button("🔊 播放单词正音", key=f"voc_p_{query}"):
                play_audio(display.get('word',''))

            st.markdown("---")
            st.subheader("📖 专业场景例句")
            for i, s in enumerate(display.get('sentences', []), 1):
                st.markdown(f'<div class="card-item"><b>{i}. {s.get("jp","")}</b><br><small>{s.get("kana","")}</small><br><span style="color:#059669;">{s.get("cn","")}</span></div>', unsafe_allow_html=True)
                if st.button(f"🔊 朗读例句 {i}", key=f"snt_{query}_{i}"):
                    play_audio(s.get("jp",""))

# --- 模块：每周 7 句 ---
elif menu == "每周 7 句":
    st.header("每周 7 句实战金句")
    for i, item in enumerate(WEEKLY_CONTENT, 1):
        with st.expander(f"第 {i} 句：{item['jp']}"):
            st.write(f"🇨🇳 中文：{item['cn']}")
            if st.button(f"🔊 播放标准朗读", key=f"wk_p_{i}"):
                play_audio(item['jp'])
