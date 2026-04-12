import streamlit as st
from openai import OpenAI
import json
from gtts import gTTS
import io

# --- 1. 核心数据库：全量 50 音体系 ---
KANA_CHART = {
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
        "あ段": [("あ","ア","a"), ("か","カ","ka"), ("さ","サ","sa"), ("た","タ","ta"), ("な","ナ","na"), ("は","ハ","ha"), ("ま","マ","ma"), ("や","ヤ","ya"), ("ら","ラ","ra"), ("わ","ワ","wa")],
        "い段": [("い","イ","i"), ("き","キ","ki"), ("し","シ","shi"), ("ち","チ","chi"), ("に","ニ","ni"), ("ひ","ヒ","hi"), ("み","ミ","mi"), ("り","リ","ri")],
        "う段": [("う","ウ","u"), ("く","ク","ku"), ("す","ス","su"), ("つ","ツ","tsu"), ("ぬ","ヌ","nu"), ("ふ","フ","fu"), ("む","ム","mu"), ("ゆ","ユ","yu"), ("る","ル","ru")],
        "え段": [("え","Ｅ","e"), ("け","ケ","ke"), ("せ","セ","se"), ("て","テ","te"), ("ね","ネ","ne"), ("へ","ヘ","he"), ("め","メ","me"), ("れ","レ","re")],
        "お段": [("お","オ","o"), ("こ","コ","ko"), ("そ","ソ","so"), ("と","ト","to"), ("の","ノ","no"), ("ほ","ホ","ho"), ("も","モ","mo"), ("よ","ヨ","yo"), ("ろ","ロ","ro"), ("を","ヲ","wo")]
    },
    "浊音/半浊音": {
        "が行": [("が","ガ","ga"), ("ぎ","ギ","gi"), ("ぐ","グ","gu"), ("げ","ゲ","ge"), ("ご","ゴ","go")],
        "ざ行": [("ざ","ザ","za"), ("じ","ジ","ji"), ("ず","ズ","zu"), ("ぜ","ゼ","ze"), ("ぞ","ゾ","zo")],
        "だ行": [("だ","ダ","da"), ("ぢ","ヂ","ji"), ("づ","ヅ","zu"), ("で","デ","de"), ("ど","ド","do")],
        "ば行": [("ば","バ","ba"), ("び","ビ","bi"), ("ぶ","ブ","bu"), ("べ","ベ","be"), ("ぼ","ボ","bo")],
        "ぱ行": [("ぱ","パ","pa"), ("ぴ","ピ","pi"), ("ぷ","普","pu"), ("ぺ","ペ","pe"), ("ぽ","ポ","po")]
    },
    "拗音": {
        "き/ぎ": [("きゃ","キャ","kya"), ("きゅ","キュ","kyu"), ("きょ","キョ","kyo"), ("ぎゃ","ギャ","gya"), ("ぎゅ","ギュ","gyu"), ("ぎょ","ギョ","gyo")],
        "し/じ": [("しゃ","シャ","sha"), ("しゅ","シュ","shu"), ("しょ","ショ","sho"), ("じゃ","ジャ","ja"), ("じゅ","ジュ","ju"), ("じょ","ジョ","jo")],
        "ち/に": [("ちゃ","チャ","cha"), ("ちゅ","チュ","chu"), ("ちょ","チョ","cho"), ("にゃ","ニャ","nya"), ("にゅ","ニュ","nyu"), ("にょ","ニョ","nyo")],
        "ひ/び/ぴ": [("ひゃ","ヒャ","hya"), ("ひゅ","ヒュ","hyu"), ("ひょ","ヒョ","hyo"), ("びゃ","ビャ","bya"), ("びゅ","ビュ","byu"), ("びょ","ビョ","byo"), ("ぴゃ","ピャ","pya"), ("ぴゅ","ピュ","pyu"), ("ぴょ","ピョ","pyo")],
        "み/り": [("みゃ","ミャ","mya"), ("みゅ","ミュ","myu"), ("みょ","ミョ","myo"), ("りゃ","リャ","rya"), ("りゅ","リュ","ryu"), ("りょ","リョ","ryo")]
    }
}

# --- 2. 核心逻辑：翻译引擎与发音 ---
def get_expert_translation(u_in):
    try:
        client = OpenAI(api_key=st.secrets["NEW_API_KEY"], base_url=st.secrets["NEW_BASE_URL"])
        prompt = f"NHK Level Translate '{u_in}' to JP. JSON only: {{\"word\":\"\",\"reading\":\"\",\"pos\":\"\",\"level\":\"N4-N5\",\"pitch\":\"\",\"sentences\":[{{\"jp\":\"\",\"kana\":\"\",\"cn\":\"\"}}]}}"
        comp = client.chat.completions.create(
            model="gpt-4o", # 强制使用高级模型
            messages=[{"role": "system", "content": "Professional Japanese Editor. NEVER use fake kanji like '号召' (ごうしょう). Use '呼びかける' instead."},
                      {"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0
        )
        res = json.loads(comp.choices[0].message.content)
        while len(res['sentences']) < 3:
            res['sentences'].append({"jp": "例文を準備中です。", "kana": "れいぶんをじゅんびちゅうです。", "cn": "例句准备中。"})
        return res
    except: return None

def play_audio(text, slow=False):
    try:
        tts = gTTS(text=text, lang='ja', slow=slow)
        fp = io.BytesIO(); tts.write_to_fp(fp); fp.seek(0)
        st.audio(fp, format="audio/mp3", autoplay=True)
    except: pass

# --- 3. UI 样式美化 ---
st.set_page_config(page_title="FUSION Pro v2.0", layout="wide")

st.markdown("""<style>
    /* 侧边栏菜单颜色与设计感优化 */
    [data-testid="stSidebar"] { background-color: #0F172A; border-right: 1px solid #1E293B; }
    [data-testid="stSidebar"] * { color: #F1F5F9 !important; font-weight: 500; }
    .st-emotion-cache-17l78vu { background: rgba(59, 130, 246, 0.2); border-left: 4px solid #3B82F6; } /* 激活项样式 */
    
    /* 50音压缩版卡片 */
    .kana-card { background: white; border: 1px solid #E2E8F0; border-radius: 6px; padding: 6px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    .kana-hira { font-size: 1.2rem; font-weight: 800; color: #1E3A8A; line-height: 1.2; }
    .kana-sub { font-size: 0.7rem; color: #64748B; margin-top: 2px; }
    
    /* 词汇专家样式 */
    .word-box { background:white; padding:15px; border-radius:10px; box-shadow:0 4px 12px rgba(0,0,0,0.05); border:1px solid #E5E7EB; text-align:center; }
    .card-item { border:1px solid #3B82F6; padding:10px; border-radius:8px; margin-bottom:8px; background:#F8FAFC; border-left: 5px solid #1E3A8A; }
</style>""", unsafe_allow_html=True)

# 初始引导数据
WELCOME_DATA = {
    "word": "こんにちは", "reading": "こんにちは", "pos": "感嘆詞", "level": "N5", "pitch": "平板",
    "sentences": [
        {"jp": "皆さん、こんにちは。FUSION Proへようこそ。", "kana": "みなさん、こんにちは。フュージョン プロへようこそ。", "cn": "大家好，欢迎来到 FUSION Pro。"},
        {"jp": "日本語の学習を一緒に楽しみましょう。", "kana": "にほんごのがくしゅうをいっしょにたのしみましょう。", "cn": "让我们一起享受日语学习的乐趣吧。"},
        {"jp": "今日は、一緒に頑張りましょう！", "kana": "きょうは、いっしょにがんばりましょう！", "cn": "今天也请一起加油吧！"}
    ]
}

# --- 4. 路由与模块 ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center; margin-bottom:20px;'>FUSION Pro</h2>", unsafe_allow_html=True)
    menu = st.radio("功能模块切换", ["AI 词汇专家", "发音实验室 (五十音图)", "JLPT 考级强化"], index=0)
    st.markdown("---")
    st.markdown("<p style='text-align:center; color:#3B82F6;'>🌸 今日も、一緒に頑張りましょう！</p>", unsafe_allow_html=True)

# --- 模块 A: 词汇专家 ---
if menu == "AI 词汇专家":
    st.header("AI 词汇专家")
    u_in = st.text_input("请输入中文词汇 (按回车查询)", placeholder="例如：努力、号召")
    
    if u_in:
        res = get_expert_translation(u_in)
        if res:
            st.session_state.res_cache = res
    else:
        st.session_state.res_cache = WELCOME_DATA

    display = st.session_state.get('res_cache')
    if display:
        st.markdown(f"""<div class="word-box">
            <h2 style="margin:0;color:#1E3A8A;">{display['word']}</h2>
            <p style="color:#3B82F6;font-size:1.1rem;font-weight:bold;">【{display['reading']}】</p>
            <p style="color:#64748B;font-size:0.8rem;">🏷️ {display['pos']} | {display['level']} | {display['pitch']}</p>
        </div>""", unsafe_allow_html=True)
        
        if st.button("🔊 播放单词音"): play_audio(display['word'])
        
        for i, s in enumerate(display['sentences'], 1):
            st.markdown(f'<div class="card-item"><b>{i}. {s["jp"]}</b><br><small>{s["kana"]}</small><br><span style="color:#059669;">{s["cn"]}</span></div>', unsafe_allow_html=True)
            if st.button(f"🔊 播放例句 {i}"): play_audio(s["jp"])

# --- 模块 B: 发音实验室 ---
elif menu == "发音实验室 (五十音图)":
    st.header("发音实验室 (五十音図)")
    
    # 全量体系选择
    category = st.selectbox("选择分类", list(KANA_CHART.keys()))
    sub_key = st.selectbox(f"选择具体【{category}】", list(KANA_CHART[category].keys()))
    
    current_list = KANA_CHART[category][sub_key]
    
    if st.button(f"🔊 连续朗读整个【{sub_key}】"):
        audio_str = "".join([item[0] for item in current_list if item[0]])
        play_audio(audio_str)

    # 压缩版网格展示
    cols = st.columns(min(len(current_list), 10))
    for idx, item in enumerate(current_list):
        if item[0]:
            with cols[idx % 10]:
                st.markdown(f"""<div class="kana-card">
                    <div class="kana-hira">{item[0]}</div>
                    <div class="kana-sub">{item[1]}</div>
                    <div class="kana-sub">[{item[2]}]</div>
                </div>""", unsafe_allow_html=True)
                if st.button("🔊", key=f"k_{sub_key}_{idx}"):
                    play_audio(item[0])

    st.markdown("---")
    st.write("🎙️ 请点击下方麦克风录音，进行 AI 发音纠错分析：")
    st.audio_input("录入您的发音", key="voice_lab_input")

# --- 模块 C: 考级强化 ---
elif menu == "JLPT 考级强化":
    st.header("JLPT 考级强化")
    # 修复截图4中的 TypeError：将 slider 改为 selectbox 确保稳定性
    n_lv = st.selectbox("选择目标等级", ["N5", "N4", "N3", "N2", "N1"], index=3)
    st.success(f"已锁定 {n_lv} 级核心题库。正在充实该等级的听力与语法精练模块...")
    st.progress(0.2, text="当前学习进度")
