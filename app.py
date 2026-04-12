import streamlit as st
from openai import OpenAI
import json
from gtts import gTTS
import io
import hashlib

# --- 1. 核心数据库：严禁改动 ---
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
    "清音-行": {"あ行": [("あ","ア","a"), ("い","イ","i"), ("う","ウ","u"), ("え","エ","e"), ("お","オ","o")], "か行": [("か","カ","ka"), ("き","キ","ki"), ("く","ク","ku"), ("け","ケ","ke"), ("こ","コ","ko")], "さ行": [("さ","サ","sa"), ("し","シ","shi"), ("す","ス","su"), ("せ","セ","se"), ("そ","ソ","so")], "た行": [("た","タ","ta"), ("ち","チ","chi"), ("つ","ツ","tsu"), ("て","テ","te"), ("と","ト","to")], "な行": [("な","ナ","na"), ("内","ニ","ni"), ("ぬ","ヌ","nu"), ("ね","ネ","ne"), ("の","ノ","no")], "は行": [("は","ハ","ha"), ("ひ","ヒ","hi"), ("ふ","フ","fu"), ("へ","ヘ","he"), ("ほ","ホ","ho")], "ま行": [("ま","マ","ma"), ("み","ミ","mi"), ("む","ム","mu"), ("め","メ","me"), ("も","モ","mo")], "や行": [("や","ヤ","ya"), (None,None,None), ("ゆ","ユ","yu"), (None,None,None), ("よ","ヨ","yo")], "ら行": [("ら","ラ","ra"), ("り","リ","ri"), ("る","ル","ru"), ("れ","レ","re"), ("ろ","ロ","ro")], "わ行": [("わ","ワ","wa"), (None,None,None), (None,None,None), (None,None,None), ("を","ヲ","wo")], "ん": [("ん","ン","n"), (None,None,None), (None,None,None), (None,None,None), (None,None,None)]},
    "清音-段": {"あ段": [("あ","ア","a"), ("か","カ","ka"), ("さ","サ","sa"), ("た","塔","ta"), ("な","ナ","na"), ("は","ハ","ha"), ("ま","マ","ma"), ("や","亚","ya"), ("ら","拉","ra"), ("わ","瓦","wa")], "い段": [("い","イ","i"), ("き","キ","ki"), ("し","シ","shi"), ("ち","チ","chi"), ("に","ニ","ni"), ("ひ","ヒ","hi"), ("み","ミ","mi"), ("り","里","ri")], "う段": [("う","ウ","u"), ("く","库","ku"), ("す","斯","su"), ("つ","促","tsu"), ("ぬ","怒","nu"), ("ふ","夫","fu"), ("む","姆","mu"), ("ゆ","优","yu"), ("る","路","ru")], "え段": [("え","艾","e"), ("け","开","ke"), ("せ","色","se"), ("て","特","te"), ("ね","内","ne"), ("へ","嘿","he"), ("め","梅","me"), ("れ","雷","re")], "お段": [("お","欧","o"), ("こ","阔","ko"), ("そ","索","so"), ("と","托","to"), ("の","诺","no"), ("ほ","霍","ho"), ("も","摩","mo"), ("よ","哟","yo"), ("ろ","罗","ro"), ("を","喔","wo")]},
    "浊音/半浊音": {"が行": [("が","ガ","ga"), ("ぎ","ギ","gi"), ("ぐ","グ","gu"), ("げ","ゲ","ge"), ("ご","ゴ","go")], "ざ行": [("ざ","ザ","za"), ("じ","ジ","ji"), ("ず","ズ","zu"), ("ぜ","ゼ","ze"), ("ぞ","ゾ","zo")], "だ行": [("だ","ダ","da"), ("ぢ","ヂ","ji"), ("づ","ヅ","zu"), ("で","デ","de"), ("ど","ド","do")], "ば行": [("ば","バ","ba"), ("び","ビ","bi"), ("ぶ","ブ","bu"), ("べ","ベ","be"), ("ぼ","ボ","bo")], "ぱ行": [("ぱ","パ","pa"), ("ぴ","ピ","pi"), ("ぷ","プ","pu"), ("ぺ","ペ","pe"), ("ぽ","ポ","po")]},
    "拗音": {"き/ぎ系": [("きゃ","キャ","kya"), ("きゅ","キュ","kyu"), ("きょ","キョ","kyo"), ("ぎゃ","ギャ","gya"), ("ぎゅ","ギュ","gyu"), ("ぎょ","ギョ","gyo")], "し/じ系": [("しゃ","シャ","sha"), ("しゅ","シュ","shu"), ("しょ","ショ","sho"), ("じゃ","ジャ","ja"), ("じゅ","ジュ","ju"), ("じょ","ジョ","jo")], "ち/に系": [("ちゃ","チャ","cha"), ("ちゅ","チュ","chu"), ("ちょ","チョ","cho"), ("にゃ","ニャ","nya"), ("にゅ","ニュ","nyu"), ("にょ","ニョ","nyo")], "ひ/び/ぴ系": [("ひゃ","ヒャ","hya"), ("ひゅ","ヒュ","hyu"), ("ひょ","ヒョ","hyo"), ("びゃ","ビャ","bya"), ("びゅ","ビュ","byu"), ("びょ","ビョ","byo"), ("ぴゃ","ピゃ","pya"), ("ぴゅ","ピュ","pyu"), ("ぴょ","ピョ","pyo")]}
}

# --- 2. 核心播报：参考 B 站标准的教学级发音 ---
def play_audio(text, is_kana=False):
    try:
        # 发音策略加固：对基础假名添加特定后缀，强制 TTS 放弃语义理解，回归纯音节
        if is_kana:
            audio_map = {"は": "ハッ", "へ": "ヘッ", "を": "オ"}
            audio_text = audio_map.get(text, text)
        else:
            audio_text = text
            
        tts = gTTS(text=audio_text, lang='ja')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        st.audio(fp, format="audio/mp3", autoplay=True)
    except: pass

def get_expert_translation(u_in):
    try:
        client = OpenAI(api_key=st.secrets["NEW_API_KEY"], base_url=st.secrets["NEW_BASE_URL"])
        prompt = f"NHK Level Translate '{u_in}'. Return JSON ONLY."
        comp = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "Professional Japanese Linguist. Return JSON: {\"word\":\"\",\"reading\":\"\",\"pos\":\"\",\"level\":\"\",\"pitch\":\"\",\"sentences\":[{\"jp\":\"\",\"kana\":\"\",\"cn\":\"\"}]}"}],
            response_format={"type": "json_object"}
        )
        return json.loads(comp.choices[0].message.content)
    except: return None

# --- 3. UI 布局 ---
st.set_page_config(page_title="FUSION Pro", layout="wide")

st.markdown("""<style>
    [data-testid="stSidebar"] { background-color: #0F172A; }
    [data-testid="stSidebar"] * { color: #F1F5F9 !important; }
    .stAudio { display:none !important; }
    .word-box { background:white; padding:20px; border-radius:12px; border:1px solid #E5E7EB; text-align:center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .card-item { border:1px solid #3B82F6; padding:12px; border-radius:10px; margin-bottom:10px; background:#F8FAFC; border-left: 6px solid #1E3A8A; }
    .kana-card { display: flex; flex-direction: column; align-items: center; background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px; }
</style>""", unsafe_allow_html=True)

WELCOME_DATA = {
    "word": "こんにちは", "reading": "こんにちは", "pos": "感嘆詞", "level": "N5", "pitch": "平板",
    "sentences": [
        {"jp": "こんにちは、今日もよろしくお願いします。", "kana": "こんにちは、きょうもよろしくおねがいします。", "cn": "你好，今天也请多多关照。"},
        {"jp": "日本語の美しさを感じてください。", "kana": "にほんごのうつくしさをかんじてください。", "cn": "请感受日语的美。"}
    ]
}

with st.sidebar:
    st.markdown("## FUSION Pro")
    menu = st.radio("功能模块切换", ["AI 词汇专家", "五十音实验室", "每周 7 句金句"], index=0)
    st.markdown("---")
    st.markdown("<p style='color:#3B82F6; font-weight:bold; text-align:center;'>🌸 今日も、一緒に頑張りましょう！</p>", unsafe_allow_html=True)

# --- 模块 A: AI 词汇专家 (逻辑物理隔离，根治张冠李戴) ---
if menu == "AI 词汇专家":
    st.header("AI 词汇专家")
    st.markdown("<h4 style='text-align:center; color:#3B82F6;'>今日も、一緒に頑張りましょう！</h4>", unsafe_allow_html=True)
    
    u_in = st.text_input("请输入中文词汇 (按回车查询)", key="search_bar")
    
    # 物理清除逻辑：计算当前输入的哈希值，与缓存对比
    if u_in:
        current_hash = hashlib.md5(u_in.encode()).hexdigest()
        if "last_hash" not in st.session_state or st.session_state.last_hash != current_hash:
            with st.spinner("专家引擎正在深度校准翻译..."):
                res = get_expert_translation(u_in)
                if res:
                    st.session_state.expert_data = res
                    st.session_state.last_hash = current_hash
                    play_audio(f"これについて、以下の日本語が考えられます。{res['word']}")
        display_data = st.session_state.get('expert_data')
    else:
        display_data = WELCOME_DATA

    if display_data:
        st.markdown(f"""<div class="word-box">
            <h2 style="margin:0; color:#1E3A8A;">{display_data['word']}</h2>
            <p style="color:#3B82F6; font-size:1.2rem; font-weight:bold;">【{display_data['reading']}】</p>
            <p style="color:#64748B; font-size:0.8rem;">🏷️ {display_data.get('pos','')} | {display_data.get('level','')} | {display_data.get('pitch','')}</p>
        </div>""", unsafe_allow_html=True)
        st.write("")
        for i, s in enumerate(display_data['sentences'], 1):
            st.markdown(f'<div class="card-item"><b>{i}. {s["jp"]}</b><br><small>{s["kana"]}</small><br><span style="color:#059669;">{s["cn"]}</span></div>', unsafe_allow_html=True)
            if st.button(f"🔊 播放例句 {i}", key=f"voice_{i}"): play_audio(s["jp"])

# --- 模块 B: 五十音实验室 (音系回归与发音加固) ---
elif menu == "五十音实验室":
    st.header("五十音实验室 (教学级发音)")
    st.info("提示：发音已参照 NHK 标准校准，克服助词读法。")
    
    cat = st.selectbox("分类选择", list(KANA_CHART.keys()))
    sub = st.selectbox(f"具体内容", list(KANA_CHART[cat].keys()))
    current_list = KANA_CHART[cat][sub]
    
    if st.button(f"🔊 连续朗读整个【{sub}】", use_container_width=True):
        audio_text = " 、 ".join([item[0] for item in current_list if item[0]])
        play_audio(audio_text, is_kana=True)

    st.write("")
    cols = st.columns(len(current_list))
    for idx, item in enumerate(current_list):
        if item[0]:
            with cols[idx]:
                st.markdown(f"""<div class="kana-card">
                    <div style="font-size:1.6rem; font-weight:bold; color:#1E3A8A;">{item[0]}</div>
                    <div style="font-size:0.8rem; color:#64748B;">{item[1]}</div>
                    <div style="font-size:0.7rem; color:#64748B;">[{item[2]}]</div>
                </div>""", unsafe_allow_html=True)
                if st.button("🔊", key=f"k_{sub}_{idx}"): play_audio(item[0], is_kana=True)

# --- 模块 C: 每周 7 句 (实战加固) ---
elif menu == "每周 7 句金句":
    st.header("每周 7 句实战金句")
    for i, item in enumerate(WEEKLY_CONTENT, 1):
        with st.expander(f"第 {i} 句：{item['jp']}"):
            st.write(f"🇨🇳 中文解释：{item['cn']}")
            if st.button(f"🔊 播放标准音", key=f"p_{i}"): play_audio(item['jp'])
            st.audio_input(f"录音跟读练习", key=f"r_{i}")
