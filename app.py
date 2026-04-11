import streamlit as st
from openai import OpenAI
import json
from gtts import gTTS
import io

# --- 1. 核心数据库与逻辑 ---
def get_fusion_expert_ultra_logic(u_in):
    # 强化 JSON Prompt，确保 GPT 严格遵守格式，防止 ValueError
    prompt = f"""
    Role: Expert Japanese Linguist. Output valid JSON only.
    Task: Translate '{u_in}' to native Japanese.
    JSON structure:
    {{
      "word": "string",
      "reading": "string",
      "pos": "string",
      "level": "string",
      "pitch": "string",
      "sentences": [
        {{"jp": "string", "kana": "string", "cn": "string"}},
        {{"jp": "string", "kana": "string", "cn": "string"}},
        {{"jp": "string", "kana": "string", "cn": "string"}}
      ]
    }}
    """
    try:
        client = OpenAI(api_key=st.secrets["NEW_API_KEY"], base_url=st.secrets["NEW_BASE_URL"])
        comp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are a professional JP-CN translator. Return JSON only. No text before or after."},
                      {"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0
        )
        return json.loads(comp.choices[0].message.content)
    except Exception as e:
        return None

# 五十音图数据映射 (平假名, 片假名, 罗马字)
KANA_CHART = {
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
    "ん": [("ん","ン","n"), (None,None,None), (None,None,None), (None,None,None), (None,None,None)],
    "が行": [("が","ガ","ga"), ("ぎ","ギ","gi"), ("ぐ","グ","gu"), ("げ","ゲ","ge"), ("ご","ゴ","go")],
    "ざ行": [("ざ","ザ","za"), ("じ","ジ","ji"), ("ず","ズ","zu"), ("ぜ","ゼ","ze"), ("ぞ","ゾ","zo")],
    "だ行": [("だ","ダ","da"), ("ぢ","ヂ","ji"), ("づ","ヅ","zu"), ("で","デ","de"), ("ど","ド","do")],
    "ば行": [("ば","バ","ba"), ("び","ビ","bi"), ("ぶ","ブ","bu"), ("べ","ベ","be"), ("ぼ","ボ","bo")],
    "ぱ行": [("ぱ","パ","pa"), ("ぴ","ピ","pi"), ("ぷ","プ","pu"), ("ぺ","ペ","pe"), ("ぽ","ポ","po")]
}

# --- 2. 界面设计 ---
st.set_page_config(page_title="FUSION Pro", layout="wide")

st.markdown("""<style>
    [data-testid="stSidebar"] { background-color: #1E3A8A; color: white; }
    .kana-card { background: white; border: 1px solid #E5E7EB; border-radius: 8px; padding: 10px; text-align: center; margin-bottom: 5px; }
    .kana-hira { font-size: 1.5rem; font-weight: bold; color: #1E3A8A; }
    .kana-sub { font-size: 0.8rem; color: #64748B; }
    .word-box { background:white; padding:15px; border-radius:10px; box-shadow:0 2px 8px rgba(0,0,0,0.05); border:1px solid #E5E7EB; text-align:center; }
    .card-item { border:1.5px solid #3B82F6; padding:10px; border-radius:8px; margin-bottom:8px; background:#F8FAFC; border-left: 5px solid #1E3A8A; }
</style>""", unsafe_allow_html=True)

def play_audio(text):
    try:
        tts = gTTS(text=text, lang='ja')
        fp = io.BytesIO(); tts.write_to_fp(fp); fp.seek(0)
        st.audio(fp, format="audio/mp3", autoplay=True)
    except: pass

with st.sidebar:
    st.title("FUSION Pro")
    menu = st.radio("功能模块切换", ["👘 AI 词汇专家", "🗣️ 发音实验室", "📝 JLPT 考级强化"])
    st.info("🌸 今日も、一緒に頑張りましょう！")

# --- 模块 A: AI 词汇专家 (修复 ValueError) ---
if menu == "👘 AI 词汇专家":
    st.header("AI 词汇专家")
    u_in = st.text_input("请输入中文词汇 (按回车查询)")
    if u_in:
        with st.spinner("专家引擎加载中..."):
            res = get_fusion_expert_ultra_logic(u_in)
            if res:
                st.markdown(f"""<div class="word-box">
                    <h2 style="margin:0;color:#1E3A8A;">{res['word']}</h2>
                    <p style="color:#3B82F6;font-size:1.1rem;font-weight:bold;">【{res['reading']}】</p>
                    <p style="color:#64748B;font-size:0.8rem;">🏷️ {res['pos']} | {res['level']} | {res['pitch']}</p>
                </div>""", unsafe_allow_html=True)
                if st.button("🔊 播放单词音"): play_audio(res['word'])
                for i, s in enumerate(res['sentences'], 1):
                    st.markdown(f'<div class="card-item"><b>{i}. {s["jp"]}</b><br><small>{s["kana"]}</small><br><span style="color:#059669;">{s["cn"]}</span></div>', unsafe_allow_html=True)
                    if st.button(f"🔊 播放例句 {i}"): play_audio(s["jp"])
            else:
                st.error("语义重组失败，请重试或检查 API 配置。")

# --- 模块 B: 发音实验室 (50 音图专家版) ---
elif menu == "🗣️ 发音实验室":
    st.header("发音实验室 (五十音図)")
    mode = st.radio("模式选择", ["按行选择 (纵向)", "按段选择 (横向)"], horizontal=True)
    
    # 构建段逻辑
    segments = ["あ段", "い段", "う段", "え段", "お段"]
    
    if mode == "按行选择 (纵向)":
        row_key = st.selectbox("选择行", list(KANA_CHART.keys()))
        current_list = KANA_CHART[row_key]
        label = row_key
    else:
        seg_idx = st.selectbox("选择段", [0,1,2,3,4], format_func=lambda x: segments[x])
        current_list = [KANA_CHART[k][seg_idx] for k in KANA_CHART.keys() if len(KANA_CHART[k]) > seg_idx]
        label = segments[seg_idx]

    # 显示并支持批量播放
    if st.button(f"🔊 连续朗读整个【{label}】"):
        audio_text = "".join([item[0] for item in current_list if item[0]])
        play_audio(audio_text)

    # 矩阵展示 (平/片/罗马字)
    cols = st.columns(len(current_list))
    for idx, (col, item) in enumerate(zip(cols, current_list)):
        if item[0]:
            with col:
                st.markdown(f"""<div class="kana-card">
                    <div class="kana-hira">{item[0]}</div>
                    <div class="kana-sub">{item[1]}</div>
                    <div class="kana-sub">[{item[2]}]</div>
                </div>""", unsafe_allow_html=True)
                if st.button("🔊", key=f"btn_{label}_{idx}"):
                    play_audio(item[0])

    st.markdown("---")
    st.write("🎙️ 请点击下方麦克风录音，进行 AI 发音纠错分析：")
    st.audio_input("录入您的发音", key="voice_lab")

# --- 模块 C: JLPT 考级强化 ---
elif menu == "📝 JLPT 考级强化":
    st.header("JLPT 考级强化")
    st.slider("选择等级", options=["N5","N4","N3","N2","N1"], value="N2")
    st.info("已锁定考级大纲。练习模块充实中...")
