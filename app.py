import streamlit as st
from openai import OpenAI
import json
from gtts import gTTS
import io

# --- 1. 核心数据库 (保持稳定，严禁修改) ---
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
    "清音-行": {"あ行": [("あ","ア","a"), ("い","イ","i"), ("う","ウ","u"), ("え","エ","e"), ("お","オ","o")], "か行": [("か","カ","ka"), ("き","キ","ki"), ("く","ク","ku"), ("け","ケ","ke"), ("こ","コ","ko")], "さ行": [("さ","サ","sa"), ("し","シ","shi"), ("す","ス","su"), ("せ","セ","se"), ("そ","ソ","so")], "た行": [("た","タ","ta"), ("ち","チ","chi"), ("つ","ツ","tsu"), ("て","テ","te"), ("と","ト","to")], "な行": [("な","ナ","na"), ("に","ニ","ni"), ("ぬ","ヌ","nu"), ("ね","ネ","ne"), ("の","ノ","no")], "は行": [("は","ハ","ha"), ("ひ","ヒ","hi"), ("ふ","フ","fu"), ("へ","ヘ","he"), ("ほ","ホ","ho")], "ま行": [("ま","マ","ma"), ("み","ミ","mi"), ("む","ム","mu"), ("め","メ","me"), ("も","モ","mo")], "や行": [("や","ヤ","ya"), (None,None,None), ("ゆ","ユ","yu"), (None,None,None), ("よ","ヨ","yo")], "ら行": [("ら","ラ","ra"), ("り","リ","ri"), ("る","ル","ru"), ("れ","レ","re"), ("ろ","ロ","ro")], "わ行": [("わ","ワ","wa"), (None,None,None), (None,None,None), (None,None,None), ("を","ヲ","wo")], "ん": [("ん","ン","n"), (None,None,None), (None,None,None), (None,None,None), (None,None,None)]},
    "清音-段": {"あ段": [("あ","ア","a"), ("か","カ","ka"), ("さ","サ","sa"), ("た","タ","ta"), ("な","ナ","na"), ("は","ハ","ha"), ("马","マ","ma"), ("や","ヤ","ya"), ("ら","ラ","ra"), ("わ","ワ","wa")], "い段": [("い","イ","i"), ("き","キ","ki"), ("し","シ","shi"), ("ち","チ","chi"), ("に","ニ","ni"), ("ひ","ヒ","hi"), ("み","ミ","mi"), ("り","リ","ri")], "う段": [("う","ウ","u"), ("く","ク","ku"), ("す","ス","su"), ("つ","ツ","tsu"), ("ぬ","ヌ","nu"), ("ふ","フ","fu"), ("む","ム","mu"), ("ゆ","ユ","yu"), ("る","ル","ru")], "え段": [("え","エ","e"), ("け","ケ","ke"), ("せ","セ","se"), ("て","テ","te"), ("ね","ネ","ne"), ("へ","ヘ","he"), ("め","メ","me"), ("れ","レ","re")], "お段": [("お","オ","o"), ("こ","コ","ko"), ("そ","ソ","so"), ("と","ト","to"), ("の","ノ","no"), ("ほ","ホ","ho"), ("も","モ","mo"), ("よ","ヨ","yo"), ("ろ","ロ","ro"), ("を","ヲ","wo")]},
    "浊音/半浊音": {"が行": [("が","ガ","ga"), ("ぎ","ギ","gi"), ("ぐ","グ","gu"), ("げ","ゲ","ge"), ("ご","ゴ","go")], "ざ行": [("ざ","ザ","za"), ("じ","ジ","ji"), ("ず","ズ","zu"), ("ぜ","ゼ","ze"), ("ぞ","ゾ","zo")], "だ行": [("だ","ダ","da"), ("ぢ","ヂ","ji"), ("づ","ヅ","zu"), ("で","デ","de"), ("ど","ド","do")], "ば行": [("ば","バ","ba"), ("び","ビ","bi"), ("补","ブ","bu"), ("べ","ベ","be"), ("ぼ","ボ","bo")], "ぱ行": [("ぱ","パ","pa"), ("ぴ","ピ","pi"), ("ぷ","プ","pu"), ("ぺ","ペ","pe"), ("ぽ","ポ","po")]},
    "拗音": {"き/ぎ系": [("きゃ","キャ","kya"), ("きゅ","キュ","kyu"), ("きょ","キョ","kyo"), ("ぎゃ","ギャ","gya"), ("ぎゅ","ギュ","gyu"), ("ぎょ","ギョ","gyo")], "し/じ系": [("しゃ","シャ","sha"), ("しゅ","シュ","shu"), ("しょ","ショ","sho"), ("じゃ","ジャ","ja"), ("じゅ","ジュ","ju"), ("じょ","ジョ","jo")], "ち/内系": [("ちゃ","チャ","cha"), ("ちゅ","チュ","chu"), ("ちょ","チョ","cho"), ("にゃ","ニャ","nya"), ("にゅ","ニュ","nyu"), ("にょ","ニョ","nyo")], "ひ/び/ぴ系": [("ひゃ","ヒャ","hya"), ("ひゅ","ヒュ","hyu"), ("ひょ","ヒョ","hyo"), ("びゃ","ビャ","bya"), ("びゅ","ビュ","byu"), ("びょ","ビョ","byo"), ("ぴゃ","ピゃ","pya"), ("ぴゅ","ピュ","pyu"), ("ぴょ","ピョ","pyo")]}
}

# --- 2. 响应优化引擎 ---
def play_audio(text, slow=False, is_kana=False):
    try:
        if is_kana:
            # 解决发音乱/慢：针对50音图采用极简文本发送，防止语义分析延迟
            audio_text = {"は": "はあ", "へ": "へえ"}.get(text, text)
        else:
            audio_text = text
        tts = gTTS(text=audio_text, lang='ja', slow=slow)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        st.audio(fp, format="audio/mp3", autoplay=True)
    except: pass

@st.cache_data(ttl=3600) # 加入缓存提升响应速度
def get_expert_translation(u_in):
    try:
        client = OpenAI(api_key=st.secrets["NEW_API_KEY"], base_url=st.secrets["NEW_BASE_URL"])
        prompt = f"NHK Style Translate '{u_in}'. Return JSON ONLY."
        comp = client.chat.completions.create(
            model="gpt-4o-mini", # 使用mini提升极速反馈，或改回gpt-4o确保严谨
            messages=[{"role": "system", "content": "Expert Japanese Editor. Return JSON: {\"word\":\"\",\"reading\":\"\",\"pos\":\"\",\"level\":\"\",\"pitch\":\"\",\"sentences\":[{\"jp\":\"\",\"kana\":\"\",\"cn\":\"\"}]}"}],
            response_format={"type": "json_object"}
        )
        return json.loads(comp.choices[0].message.content)
    except: return None

# --- 3. UI 布局 ---
st.set_page_config(page_title="FUSION Pro v2.0", layout="wide")
st.markdown("""<style>
    [data-testid="stSidebar"] { background-color: #0F172A; }
    [data-testid="stSidebar"] * { color: #F1F5F9 !important; }
    .stAudio { display:none !important; }
    .word-box { background:white; padding:15px; border-radius:10px; border:1px solid #E5E7EB; text-align:center; }
    .card-item { border:1.5px solid #3B82F6; padding:10px; border-radius:8px; margin-bottom:8px; background:#F8FAFC; border-left: 5px solid #1E3A8A; }
</style>""", unsafe_allow_html=True)

WELCOME_DATA = {
    "word": "こんにちは", "reading": "こんにちは", "pos": "感嘆詞", "level": "N5", "pitch": "平板",
    "sentences": [
        {"jp": "こんにちは、今日もよろしくお願いします。", "kana": "こんにちは、きょうもよろしくおねがいします。", "cn": "你好，今天也请多多关照。"},
        {"jp": "FUSION Proへようこそ、一緒に勉強しましょう。", "kana": "フュージョンプロへようこそ、いっしょにべんきょうしましょう。", "cn": "欢迎来到FUSION Pro，让我们一起学习吧。"},
        {"jp": "日本語の美しさを感じてください。", "kana": "にほんごのうつくしさをかんじてください。", "cn": "请感受日语的美。"}
    ]
}

with st.sidebar:
    st.markdown("## FUSION Pro")
    menu = st.radio("功能模块切换", ["AI 词汇专家", "五十音实验室", "每周 7 句金句"], index=0)
    st.markdown("---")
    st.markdown("<p style='color:#3B82F6; font-weight:bold; text-align:center;'>🌸 今日も、一緒に頑張りましょう！</p>", unsafe_allow_html=True)

# --- 模块 A: 词汇专家 (即时响应加固) ---
if menu == "AI 词汇专家":
    st.header("AI 词汇专家")
    st.markdown("<h5 style='text-align:center; color:#3B82F6;'>今日も、一緒に頑張りましょう！</h5>", unsafe_allow_html=True)
    
    # 使用 form 结构强制回车提交，解决无反应问题
    with st.form(key="search_form", clear_on_submit=False):
        u_in = st.text_input("请输入中文词汇 (输入后按回车提交)", key="user_query")
        submit_button = st.form_submit_button(label="立即检索")

    if u_in:
        res = get_expert_translation(u_in)
        if res:
            play_audio(f"これについて、以下の日本語が考えられます。{res['word']}")
            st.markdown(f"""<div class="word-box">
                <h2 style="margin:0;color:#1E3A8A;">{res['word']}</h2>
                <p style="color:#3B82F6;font-size:1.1rem;font-weight:bold;">【{res['reading']}】</p>
                <p style="color:#64748B;font-size:0.8rem;">🏷️ {res['pos']} | {res['level']} | {res['pitch']}</p>
            </div>""", unsafe_allow_html=True)
            for i, s in enumerate(res['sentences'], 1):
                st.markdown(f'<div class="card-item"><b>{i}. {s["jp"]}</b><br><small>{s["kana"]}</small><br><span style="color:#059669;">{s["cn"]}</span></div>', unsafe_allow_html=True)
                if st.button(f"🔊 播放例句 {i}", key=f"s_{i}"): play_audio(s["jp"])
    else:
        # 显示初始页面
        st.markdown(f"""<div class="word-box">
            <h2 style="margin:0;color:#1E3A8A;">{WELCOME_DATA['word']}</h2>
            <p style="color:#3B82F6;font-size:1.1rem;font-weight:bold;">【{WELCOME_DATA['reading']}】</p>
        </div>""", unsafe_allow_html=True)
        for i, s in enumerate(WELCOME_DATA['sentences'], 1):
            st.markdown(f'<div class="card-item"><b>{i}. {s["jp"]}</b><br><small>{s["kana"]}</small><br><span style="color:#059669;">{s["cn"]}</span></div>', unsafe_allow_html=True)

# --- 模块 B: 五十音实验室 (发音加速) ---
elif menu == "五十音实验室":
    st.header("五十音实验室 (发音纠错)")
    cat = st.selectbox("选择分类", list(KANA_CHART.keys()))
    sub = st.selectbox(f"选择具体【{cat}】", list(KANA_CHART[cat].keys()))
    current_list = KANA_CHART[cat][sub]
    
    # 极简连读逻辑，杜绝卡顿
    if st.button(f"🔊 连续朗读整个【{sub}】"):
        audio_text = " 、 ".join([item[0] for item in current_list if item[0]])
        play_audio(audio_text, is_kana=True)

    cols = st.columns(len(current_list))
    for idx, item in enumerate(current_list):
        if item[0]:
            with cols[idx]:
                st.markdown(f"<div style='text-align:center; font-size:1.5rem; font-weight:bold; color:#1E3A8A;'>{item[0]}</div>", unsafe_allow_html=True)
                if st.button("🔊", key=f"btn_{sub}_{idx}"): 
                    play_audio(item[0], is_kana=True)

# --- 模块 C: 每周 7 句 ---
elif menu == "每周 7 句金句":
    st.header("每周 7 句实战金句")
    for i, item in enumerate(WEEKLY_CONTENT, 1):
        with st.expander(f"第 {i} 句：{item['jp']}"):
            st.write(f"🇨🇳 中文意思：{item['cn']}")
            if st.button(f"🔊 播放标准音", key=f"week_{i}"): play_audio(item['jp'])
            st.audio_input(f"跟读练习", key=f"rec_{i}")
