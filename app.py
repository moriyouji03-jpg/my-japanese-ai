import streamlit as st
from openai import OpenAI
import json
from gtts import gTTS
import io

# --- 1. 核心数据库：NHK 标准语料与 50 音体系 ---
WEEKLY_CONTENT = [
    {"jp": "お疲れ様です。お先に失礼します。", "cn": "辛苦了，我先走一步。"},
    {"jp": "お忙しいところ恐縮ですが、ご確認いただけますか。", "cn": "百忙之中给您添麻烦了，能请您确认一下吗？"},
    {"jp": "承知いたしました。早速取り掛かります。", "cn": "明白了。我马上着手处理。"},
    {"jp": "ご意見を伺えますでしょうか。", "cn": "可以请教一下您的意见吗？"},
    {"jp": "何卒よろしくお願い申し上げます。", "cn": "请多多关照。"},
    {"jp": "検討させていただきます。", "cn": "我们会慎重考虑。"},
    {"jp": "お会いできて光栄です。", "cn": "能见到您深感荣幸。"}
]

KANA_CHART = {
    "清音-行": {
        "あ行": [("あ","ア","a"), ("い","イ","i"), ("う","ウ","u"), ("え","Ｅ","e"), ("お","オ","o")],
        "か行": [("か","カ","ka"), ("き","キ","ki"), ("く","ク","ku"), ("け","ケ","ke"), ("こ","コ","ko")],
        "さ行": [("さ","サ","sa"), ("し","シ","shi"), ("す","ス","su"), ("せ","セ","se"), ("そ","ソ","so")],
        "た行": [("た","タ","ta"), ("ち","チ","chi"), ("つ","ツ","tsu"), ("て","テ","te"), ("と","ト","to")],
        "な行": [("な","ナ","na"), ("に","ニ","ni"), ("ぬ","ヌ","nu"), ("ね","ネ","ne"), ("の","ノ","no")],
        "は行": [("は","ハ","ha"), ("ひ","ヒ","hi"), ("ふ","フ","fu"), ("へ","ヘ","he"), ("ほ","ホ","ho")],
        "ま行": [("ま","马","ma"), ("み","ミ","mi"), ("む","ム","mu"), ("め","メ","me"), ("も","モ","mo")],
        "や行": [("や","ヤ","ya"), (None,None,None), ("ゆ","ユ","yu"), (None,None,None), ("よ","ヨ","yo")],
        "ら行": [("ら","ラ","ra"), ("り","リ","ri"), ("る","ル","ru"), ("れ","レ","re"), ("ろ","ロ","ro")],
        "わ行": [("わ","ワ","wa"), (None,None,None), (None,None,None), (None,None,None), ("を","ヲ","wo")],
        "ん": [("ん","ン","n"), (None,None,None), (None,None,None), (None,None,None), (None,None,None)]
    },
    "清音-段": {
        "あ段": [("あ","ア","a"), ("か","カ","ka"), ("さ","サ","sa"), ("た","タ","ta"), ("な","ナ","na"), ("は","ハ","ha"), ("ま","マ","ma"), ("や","ヤ","ya"), ("ら","ラ","ra"), ("わ","ワ","wa")],
        "い段": [("い","イ","i"), ("き","キ","ki"), ("し","シ","shi"), ("ち","チ","chi"), ("に","ニ","ni"), ("ひ","ヒ","hi"), ("み","ミ","mi"), ("り","リ","ri")],
        "う段": [("う","ウ","u"), ("く","ク","ku"), ("す","ス","su"), ("つ","ツ","tsu"), ("ぬ","ヌ","nu"), ("ふ","フ","fu"), ("む","ム","mu"), ("ゆ","ユ","yu"), ("る","ル","ru")],
        "え段": [("え","Ｅ","e"), ("け","ケ","ke"), ("せ","セ","se"), ("て","テ","te"), ("ね","ネ","ne"), ("へ","ヘ","he"), ("め","メ","me"), ("れ","レ","re")],
        "お段": [("お","オ","o"), ("こ","コ","ko"), ("そ","苏","so"), ("と","ト","to"), ("の","诺","no"), ("ほ","ホ","ho"), ("も","モ","mo"), ("よ","ヨ","yo"), ("ろ","罗","ro"), ("を","ヲ","wo")]
    },
    "浊音/半浊音": {
        "が行": [("が","ガ","ga"), ("ぎ","ギ","gi"), ("ぐ","グ","gu"), ("格","ゲ","ge"), ("ご","ゴ","go")],
        "ざ行": [("ざ","扎","za"), ("じ","ジ","ji"), ("ず","ズ","zu"), ("ぜ","ゼ","ze"), ("ぞ","佐","zo")],
        "だ行": [("だ","达","da"), ("ぢ","ヂ","ji"), ("づ","ヅ","zu"), ("で","德","de"), ("ど","多","do")],
        "ば行": [("ば","巴","ba"), ("び","毕","bi"), ("ぶ","布","bu"), ("べ","贝","be"), ("ぼ","波","bo")],
        "ぱ行": [("ぱ","帕","pa"), ("ぴ","皮","pi"), ("ぷ","普","pu"), ("ぺ","佩","pe"), ("ぽ","波","po")]
    },
    "拗音": {
        "き/ぎ": [("きゃ","キャ","kya"), ("きゅ","キュ","kyu"), ("きょ","キョ","kyo"), ("ぎゃ","ギャ","gya"), ("ぎゅ","ギュ","gyu"), ("ぎょ","ギョ","gyo")],
        "し/じ": [("しゃ","シャ","sha"), ("しゅ","シュ","shu"), ("しょ","ショ","sho"), ("じゃ","ジャ","ja"), ("じゅ","ジュ","ju"), ("じょ","ジョ","jo")],
        "ち/に": [("ちゃ","チャ","cha"), ("ちゅ","チュ","chu"), ("ちょ","チョ","cho"), ("にゃ","ニャ","nya"), ("にゅ","ニュ","nyu"), ("にょ","ニョ","nyo")],
        "ひ/び/ぴ": [("ひゃ","ヒャ","hya"), ("ひゅ","ヒュ","hyu"), ("ひょ","ヒョ","hyo"), ("びゃ","ビャ","bya"), ("びゅ","ビュ","byu"), ("びょ","ビョ","byo"), ("ぴゃ","ピャ","pya"), ("ぴゅ","ピュ","pyu"), ("ぴょ","ピョ","pyo")]
    }
}

# --- 2. 核心播报与分析引擎 ---
def play_audio(text, slow=False):
    try:
        tts = gTTS(text=text, lang='ja', slow=slow)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        st.audio(fp, format="audio/mp3", autoplay=True)
    except Exception:
        pass

def get_expert_translation(u_in):
    try:
        client = OpenAI(api_key=st.secrets["NEW_API_KEY"], base_url=st.secrets["NEW_BASE_URL"])
        prompt = f"NHK Style Translate '{u_in}'. JSON only: {{\"word\":\"\",\"reading\":\"\",\"pos\":\"\",\"level\":\"N4\",\"pitch\":\"\",\"sentences\":[{{\"jp\":\"\",\"kana\":\"\",\"cn\":\"\"}},{{\"jp\":\"\",\"kana\":\"\",\"cn\":\"\"}},{{\"jp\":\"\",\"kana\":\"\",\"cn\":\"\"}}]}}"
        comp = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "Professional Japanese Linguist. Focused on precision."},
                      {"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(comp.choices[0].message.content)
    except Exception:
        return None

# --- 3. UI 布局 ---
st.set_page_config(page_title="FUSION Pro v2.0", layout="wide")

st.markdown("""<style>
    [data-testid="stSidebar"] { background-color: #0F172A; }
    [data-testid="stSidebar"] * { color: #F1F5F9 !important; }
    .word-box { background:white; padding:25px; border-radius:15px; box-shadow:0 10px 25px rgba(0,0,0,0.05); border:1px solid #E5E7EB; text-align:center; }
    .card-item { border:1.5px solid #3B82F6; padding:15px; border-radius:10px; margin-bottom:12px; background:#F8FAFC; border-left: 6px solid #1E3A8A; }
    .kana-card { background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 6px; text-align: center; }
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## FUSION Pro")
    menu = st.radio("功能模块切换", ["AI 词汇专家", "五十音实验室", "每周 7 句金句"], index=0)
    st.markdown("---")
    st.markdown("<p style='color:#3B82F6; font-weight:bold; text-align:center;'>🌸 今日も、一緒に頑張りましょう！</p>", unsafe_allow_html=True)

# --- 模块 A: AI 词汇专家 ---
if menu == "AI 词汇专家":
    st.header("AI 词汇专家")
    
    # 修改点 1：欢迎语只显示，不朗读
    st.markdown("<h4 style='color:#1E3A8A; text-align:center; margin-bottom:20px;'>🌸 今日も、一緒に頑張りましょう！</h4>", unsafe_allow_html=True)
    
    u_in = st.text_input("请输入中文词汇 (按回车查询)", placeholder="例如：努力、号召")
    
    # 初始默认显示“你好”
    current_query = u_in.strip() if u_in else "你好"
    
    if current_query:
        if "last_query" not in st.session_state or st.session_state.last_query != current_query:
            with st.spinner(f'解析中...'):
                res = get_expert_translation(current_query)
                if res:
                    st.session_state.res_cache = res
                    st.session_state.last_query = current_query
                    # 修改点 2：固定语音播报句子，不拼接单词
                    play_audio("これについて、以下の日本語が考えられます")
        
        display = st.session_state.get('res_cache')
        if display:
            st.markdown(f"""
                <div style="display: flex; justify-content: center; margin-bottom: 25px;">
                    <div class="word-box" style="width: 100%; max-width: 650px; border-top: 6px solid #3B82F6;">
                        <h1 style="margin:5px 0; color:#1E3A8A; font-size: 3.5rem;">{display['word']}</h1>
                        <p style="color:#3B82F6; font-size:1.4rem; font-weight:bold; margin-bottom:10px;">【{display['reading']}】</p>
                        <div style="display: flex; justify-content: center; gap: 20px;">
                            <span style="background:#F1F5F9; padding:4px 12px; border-radius:20px; color:#475569; font-size:0.9rem;">🏷️ {display['pos']}</span>
                            <span style="background:#F1F5F9; padding:4px 12px; border-radius:20px; color:#475569; font-size:0.9rem;">🏆 {display['level']}</span>
                            <span style="background:#F1F5F9; padding:4px 12px; border-radius:20px; color:#475569; font-size:0.9rem;">📈 {display['pitch']}</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns([1, 1, 1])
            with c2:
                if st.button("🔊 播放单词标准音", use_container_width=True): 
                    play_audio(display['word'])
            
            st.markdown("---")
            st.subheader("📖 专业场景例句")
            for i, s in enumerate(display['sentences'], 1):
                st.markdown(f'<div class="card-item"><b>{i}. {s["jp"]}</b><br><small>{s["kana"]}</small><br><span style="color:#059669;">{s["cn"]}</span></div>', unsafe_allow_html=True)
                col1, col2, _ = st.columns([1, 1, 3])
                if col1.button(f"▶️ 标准速 {i}"): play_audio(s["jp"])
                if col2.button(f"🐢 慢速 {i}"): play_audio(s["jp"], slow=True)

# --- 模块 B: 五十音实验室 ---
elif menu == "五十音实验室":
    st.header("五十音实验室")
    cat = st.selectbox("选择分类", list(KANA_CHART.keys()))
    sub = st.selectbox(f"选择具体【{cat}】", list(KANA_CHART[cat].keys()))
    
    current_list = KANA_CHART[cat][sub]
    if st.button(f"🔊 连续朗读整个【{sub}】", use_container_width=True):
        play_audio("".join([item[0] for item in current_list if item[0]]))

    cols = st.columns(len(current_list))
    for idx, item in enumerate(current_list):
        if item[0]:
            with cols[idx]:
                st.markdown(f'<div class="kana-card"><b>{item[0]}</b><br><small>{item[1]}</small></div>', unsafe_allow_html=True)
                if st.button("🔊", key=f"k_{sub}_{idx}"): play_audio(item[0])

# --- 模块 C: 每周 7 句 ---
elif menu == "每周 7 句金句":
    st.header("每周 7 句实战金句")
    for i, item in enumerate(WEEKLY_CONTENT, 1):
        with st.expander(f"第 {i} 句：{item['jp']}"):
            st.write(f"🇨🇳 中文：{item['cn']}")
            if st.button(f"🔊 播放第 {i} 句"): play_audio(item['jp'])
            st.audio_input(f"练习第 {i} 句", key=f"wk_{i}")
