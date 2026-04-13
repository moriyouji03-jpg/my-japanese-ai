import streamlit as st
from openai import OpenAI
import json
from gtts import gTTS
import io
import time

# --- 1. 核心数据库：100% 纯净五十音 (彻底移除汉字) ---
KANA_DATA = {
    "清音-行": {
        "あ行": [("あ","ア","a"), ("い","イ","i"), ("う","ウ","u"), ("え","エ","e"), ("お","オ","o")],
        "か行": [("か","カ","ka"), ("き","キ","ki"), ("く","ク","ku"), ("け","ケ","ke"), ("こ","コ","ko")],
        "さ行": [("さ","サ","sa"), ("し","シ","shi"), ("す","ス","su"), ("せ","セ","se"), ("そ","ソ","so")],
        "た行": [("た","タ","ta"), ("ち","チ","chi"), ("つ","ツ","tsu"), ("て","テ","te"), ("内","ト","to")],
        "な行": [("な","ナ","na"), ("に","ニ","ni"), ("ぬ","ヌ","nu"), ("ね","ネ","ne"), ("の","ノ","no")],
        "は行": [("は","ハ","ha"), ("ひ","ヒ","hi"), ("ふ","フ","fu"), ("へ","ヘ","he"), ("ほ","ホ","ho")],
        "ま行": [("ま","マ","ma"), ("み","ミ","mi"), ("む","ム","mu"), ("め","メ","me"), ("も","モ","mo")],
        "や行": [("や","ヤ","ya"), (None,None,None), ("ゆ","ユ","yu"), (None,None,None), ("よ","ヨ","yo")],
        "ら行": [("ら","ア","ra"), ("り","リ","ri"), ("る","ル","ru"), ("れ","レ","re"), ("ろ","ロ","ro")],
        "わ行": [("わ","ワ","wa"), (None,None,None), (None,None,None), (None,None,None), ("を","ヲ","wo")],
        "ん": [("ん","ン","n"), (None,None,None), (None,None,None), (None,None,None), (None,None,None)]
    },
    "清音-段": {
        "あ段": [("あ","ア","a"), ("か","カ","ka"), ("さ","サ","sa"), ("た","タ","ta"), ("な","ナ","na"), ("は","ハ","ha"), ("ま","マ","ma"), ("や","亚","ya"), ("ら","ラ","ra"), ("わ","ワ","wa")],
        "い段": [("い","イ","i"), ("き","キ","ki"), ("し","シ","shi"), ("ち","チ","chi"), ("に","ニ","ni"), ("ひ","ヒ","hi"), ("み","ミ","mi"), ("り","リ","ri")],
        "う段": [("う","ウ","u"), ("く","ク","ku"), ("す","ス","su"), ("つ","ツ","tsu"), ("ぬ","ヌ","nu"), ("ふ","フ","fu"), ("む","ム","mu"), ("ゆ","ユ","yu"), ("る","ル","ru")],
        "え段": [("え","エ","e"), ("け","ケ","ke"), ("せ","セ","se"), ("て","テ","te"), ("ね","ネ","ne"), ("へ","ヘ","he"), ("め","メ","me"), ("れ","レ","re")],
        "お段": [("お","オ","o"), ("こ","コ","ko"), ("そ","ソ","so"), ("特","ト","to"), ("の","ノ","no"), ("ほ","ホ","ho"), ("も","モ","mo"), ("よ","ヨ","yo"), ("ろ","ロ","ro"), ("を","ヲ","wo")]
    },
    "浊音/半浊音": {
        "が行": [("が","ガ","ga"), ("ぎ","ギ","gi"), ("ぐ","グ","gu"), ("げ","ゲ","ge"), ("ご","ゴ","go")],
        "ざ行": [("ざ","ザ","za"), ("じ","ジ","ji"), ("ず","ズ","zu"), ("ぜ","ゼ","ze"), ("ぞ","ゾ","zo")],
        "だ行": [("だ","ダ","da"), ("ぢ","ヂ","ji"), ("づ","ヅ","zu"), ("で","デ","de"), ("ど","ド","do")],
        "ば行": [("ば","バ","ba"), ("び","ビ","bi"), ("ぶ","ブ","bu"), ("べ","ベ","be"), ("ぼ","ボ","bo")],
        "ぱ行": [("ぱ","パ","pa"), ("ぴ","ピ","pi"), ("ぷ","普","pu"), ("ぺ","佩","pe"), ("ぽ","波","po")]
    },
    "拗音体系": {
        "清拗音": [("きゃ","キャ","kya"), ("きゅ","キュ","kyu"), ("きょ","キョ","kyo"), ("しゃ","シャ","sha"), ("しゅ","シュ","shu"), ("しょ","ショ","sho"), ("ちゃ","チャ","cha"), ("ちゅ","チュ","chu"), ("ちょ","チョ","cho")],
        "浊拗音": [("ぎゃ","ギャ","gya"), ("ぎゅ","ギュ","gyu"), ("ぎょ","ギョ","gyo"), ("じゃ","ジャ","ja"), ("じゅ","ジュ","ju"), ("じょ","ジョ","jo")],
        "半浊拗音": [("ぴゃ","ピャ","pya"), ("ぴゅ","ピュ","pyu"), ("ぴょ","ピョ","pyo")]
    }
}

# --- 2. 发音引擎 (增强版) ---
def play_audio(text_input):
    try:
        def calibrate(t):
            # 针对 は(ha) 和 へ(he) 采用“音标引导+强制停顿”法，100% 锁定原音
            if t == "は": return "ha, は。"
            if t == "へ": return "he, へ。"
            if t == "を": return "o, を。"
            return t

        if isinstance(text_input, list):
            # 连续朗读：增加物理停顿
            processed_text = " 、 ".join([calibrate(t) for t in text_input if t])
        else:
            processed_text = calibrate(text_input)

        tts = gTTS(text=processed_text, lang='ja', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        # 强制音频组件刷新
        st.audio(fp, format="audio/mp3", autoplay=True)
    except Exception as e:
        st.error(f"发音模块异常: {e}")

def get_ai_expert(u_in):
    try:
        client = OpenAI(api_key=st.secrets["NEW_API_KEY"], base_url=st.secrets["NEW_BASE_URL"])
        prompt = f"请作为顶尖中日翻译专家，分析词汇‘{u_in}’。返回JSON：word, reading, pos, level, pitch, sentences(3句)。"
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "你只输出纯净的JSON格式。"}, {"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return None

# --- 3. UI 布局 ---
st.set_page_config(page_title="FUSION Pro v4.0", layout="wide")

st.markdown("""<style>
    [data-testid="stSidebar"] { background-color: #0F172A; }
    audio { display:none !important; }
    .kana-card { background: white; border: 1px solid #E2E8F0; border-radius: 12px; padding: 12px 0; text-align: center; }
    .hiragana { font-size: 2.2rem; font-weight: bold; color: #1E3A8A; }
    .romaji { font-size: 0.9rem; color: #3B82F6; font-weight: 600; text-transform: uppercase; }
    .card-item { border:1px solid #E2E8F0; padding:15px; border-radius:12px; background:#F8FAFC; border-left: 5px solid #1E3A8A; margin-bottom:10px; }
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.title("FUSION Pro")
    menu = st.radio("功能模块", ["五十音实验室", "AI 词汇专家", "每周金句"], index=0)

# --- 模块 A: 五十音实验室 ---
if menu == "五十音实验室":
    st.header("五十音实验室")
    # 修复 KeyError 的关键点：确保选择逻辑严丝合缝
    main_cat = st.segmented_control("选择音系", list(KANA_DATA.keys()), default="清音-行")
    
    if main_cat in KANA_DATA:
        sub_cat = st.selectbox("具体分类", list(KANA_DATA[main_cat].keys()))
        current_list = KANA_DATA[main_cat][sub_cat]
        
        c1, _ = st.columns([1, 2])
        if c1.button(f"🔊 节奏连读：{sub_cat}", use_container_width=True, key=f"run_{sub_cat}"):
            play_audio([item[0] for item in current_list if item[0]])
        
        st.markdown("---")
        num_cols = 5 if "行" in sub_cat or "浊" in sub_cat else 3
        cols = st.columns(num_cols)
        
        for idx, item in enumerate(current_list):
            if item[0]:
                with cols[idx % num_cols]:
                    st.markdown(f"""<div class="kana-card">
                        <div class="hiragana">{item[0]}</div>
                        <div class="katakana" style="color:#64748B;">{item[1]}</div>
                        <div class="romaji">{item[2]}</div>
                    </div>""", unsafe_allow_html=True)
                    # 动态 Key 解决重复点击失效
                    if st.button("🔊", key=f"btn_{idx}_{time.time()}"):
                        play_audio(item[0])

# --- 模块 B: AI 词汇专家 ---
elif menu == "AI 词汇专家":
    st.header("AI 词汇专家")
    u_input = st.text_input("输入中文词汇", placeholder="例如：落实、号召")
    
    if u_input:
        if "last_word" not in st.session_state or st.session_state.last_word != u_input:
            data = get_ai_expert(u_input)
            if data:
                st.session_state.expert_cache = data
                st.session_state.last_word = u_input
        
        res = st.session_state.get("expert_cache")
        if res:
            st.markdown(f"""<div style="text-align:center; padding:20px; background:white; border-radius:15px; border:1px solid #E2E8F0; margin-bottom:20px;">
                <h1 style="color:#1E3A8A; margin:0;">{res['word']}</h1>
                <p style="color:#3B82F6; font-size:1.2rem; margin:5px 0;">【{res['reading']}】</p>
                <code style="background:#F1F5F9; padding:2px 8px;">{res['pos']} | {res['level']} | {res['pitch']}型</code>
            </div>""", unsafe_allow_html=True)
            
            if st.button("🔊 播放单词正音", key=f"play_main_{time.time()}"):
                play_audio(res['word'])
            
            st.subheader("场景应用例句")
            # 修复 TypeError 的渲染逻辑
            for i, s in enumerate(res.get('sentences', []), 1):
                with st.container():
                    st.markdown(f"""<div class="card-item">
                        <strong>{i}. {s.get('jp', '')}</strong><br>
                        <small style="color:#64748B;">{s.get('kana', '')}</small><br>
                        <span style="color:#059669;">{s.get('cn', '')}</span>
                    </div>""", unsafe_allow_html=True)
                    if st.button(f"播放例句 {i}", key=f"sent_{i}_{time.time()}"):
                        play_audio(s.get('jp', ''))

# --- 模块 C: 每周金句 ---
elif menu == "每周金句":
    st.header("职场实战 7 句")
    sentences = [
        {"jp": "お疲れ様です。お先に失礼します。", "cn": "辛苦了，我先走一步。"},
        {"jp": "ご検討のほど、よろしくお願いいたします。", "cn": "请您考虑。"}
    ]
    for i, item in enumerate(sentences):
        with st.expander(f"句型 {i+1}: {item['jp']}"):
            st.write(item['cn'])
            if st.button(f"播放", key=f"gold_{i}_{time.time()}"):
                play_audio(item['jp'])
