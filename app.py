import streamlit as st
from openai import OpenAI
import json
from gtts import gTTS
import io

# --- 1. 核心数据库与配置 ---
WEEKLY_CONTENT = [
    {"jp": "お疲れ様です。お先に失礼します。", "cn": "辛苦了，我先走一步。"},
    {"jp": "お忙しいところ恐縮ですが、ご確認いただけますか。", "cn": "百忙之中给您添麻烦了，能请您确认一下吗？"},
    {"jp": "承知いたしました。早速取り掛かります。", "cn": "明白了。我马上着手处理。"},
    {"jp": "ご意見を伺えますでしょうか。", "cn": "可以请教一下您的意见吗？"},
    {"jp": "何卒よろしくお願い申し上げます。", "cn": "请多多关照。"},
    {"jp": "検討させていただきます。", "cn": "我们会慎重考虑。"},
    {"jp": "お会いできて光栄です。", "cn": "能见到您深感荣幸。"}
]

# (五十音数据保持不变，此处略过以节省篇幅，实际应用请保留原数据)
KANA_CHART = { "清音-行": { "あ行": [("あ","ア","a"), ("い","イ","i"), ("う","ウ","u"), ("え","Ｅ","e"), ("お","オ","o")] } }

# --- 2. 核心播报引擎 (隐藏 UI 控制) ---
def play_audio(text, slow=False, silent=True):
    try:
        tts = gTTS(text=text, lang='ja', slow=slow)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        if silent:
            with st.container():
                st.audio(fp, format="audio/mp3", autoplay=True)
                # 隐藏播放器
                st.markdown("""<style>audio { display:none !important; }</style>""", unsafe_allow_html=True)
        else:
            st.audio(fp, format="audio/mp3", autoplay=True)
    except: pass

# --- 3. 专家级翻译逻辑 (深度优化 Prompt) ---
def get_expert_translation(u_in):
    try:
        client = OpenAI(api_key=st.secrets["NEW_API_KEY"], base_url=st.secrets["NEW_BASE_URL"])
        # 这里是核心改进：要求 AI 思考语境，拒绝“死翻”
        prompt = f"""
        作为一名资深中日翻译专家，请将中文词汇“{u_in}”翻译为最地道、最符合现代日本社会表达习惯的日语。
        
        【要求】：
        1. 拒绝机械翻译。如果该词在日语中有更自然的固有词表达（如：号召 -> 呼びかける），请优先使用。
        2. 返回 JSON 格式，必须包含：
           - word: 最地道的日语表达
           - reading: 汉字的假名标注
           - pos: 词性
           - level: JLPT等级(N1-N5)
           - pitch: 音调类型(如 0, 1, 2)
           - context_advice: 简短的语感说明（如：该词常用于商务、比汉字词更柔和等）
           - sentences: 3个极具实战意义的例句。
        
        JSON 结构：
        {{
          "word": "", "reading": "", "pos": "", "level": "", "pitch": "", "context_advice": "",
          "sentences": [
            {{"jp": "日语原句", "kana": "假名辅助", "cn": "地道中文翻译"}},
            ...
          ]
        }}
        """
        comp = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "你是一位拥有30年经验的同声传译专家，精通中日语言细微差异。"},
                      {"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(comp.choices[0].message.content)
    except: return None

# --- 4. UI 布局 ---
st.set_page_config(page_title="FUSION Pro v2.5", layout="wide")

st.markdown("""<style>
    [data-testid="stSidebar"] { background-color: #0F172A; }
    .word-box { background:white; padding:15px 20px; border-radius:12px; box-shadow:0 8px 20px rgba(0,0,0,0.06); border:1px solid #E5E7EB; text-align:center; }
    .card-item { border:1.5px solid #E2E8F0; padding:12px; border-radius:10px; margin-bottom:10px; background:#F8FAFC; border-left: 6px solid #1E3A8A; }
    .advice-box { background:#EFF6FF; border:1px dashed #3B82F6; padding:8px; border-radius:8px; margin-top:10px; font-size:0.85rem; color:#1E40AF; text-align:left; }
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## FUSION Pro")
    menu = st.radio("功能模块切换", ["AI 词汇专家", "五十音实验室", "每周 7 句金句"], index=0)

# --- 模块 A: AI 词汇专家 ---
if menu == "AI 词汇专家":
    st.header("AI 词汇专家")
    st.markdown("<h4 style='color:#1E3A8A; text-align:center; margin-bottom:15px;'>🌸 今日も、一緒に頑張りましょう！</h4>", unsafe_allow_html=True)
    
    u_in = st.text_input("请输入中文词汇 (按回车查询)", placeholder="例如：号召、落实、对接")
    
    search_query = u_in.strip() if u_in else "你好"
    
    if search_query:
        if "last_query" not in st.session_state or st.session_state.last_query != search_query:
            with st.spinner('专家正在斟酌最地道的表达...'):
                res = get_expert_translation(search_query)
                if res:
                    st.session_state.res_cache = res
                    st.session_state.last_query = search_query
                    # 修改点：回车即刻朗读固定开场白（静默模式）
                    play_audio("これについて、以下の日本語が考えられます", silent=True)
        
        display = st.session_state.get('res_cache')
        if display:
            st.markdown(f"""
                <div style="display: flex; justify-content: center; margin-bottom: 20px;">
                    <div class="word-box" style="width: 100%; max-width: 650px; border-top: 5px solid #3B82F6;">
                        <h1 style="margin:2px 0; color:#1E3A8A; font-size: 2.8rem;">{display['word']}</h1>
                        <p style="color:#3B82F6; font-size:1.1rem; font-weight:bold; margin-bottom:8px;">【{display['reading']}】</p>
                        <div style="display: flex; justify-content: center; gap: 15px;">
                            <span style="background:#F1F5F9; padding:2px 10px; border-radius:15px; color:#475569; font-size:0.8rem;">🏷️ {display['pos']}</span>
                            <span style="background:#F1F5F9; padding:2px 10px; border-radius:15px; color:#475569; font-size:0.8rem;">🏆 {display['level']}</span>
                            <span style="background:#F1F5F9; padding:2px 10px; border-radius:15px; color:#475569; font-size:0.8rem;">📈 {display['pitch']}型</span>
                        </div>
                        <div class="advice-box">💡 <b>专家建议：</b>{display.get('context_advice', '暂无建议')}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # 播放按钮
            c1, c2, c3 = st.columns([1, 1, 1])
            with c2:
                if st.button("🔊 播放单词标准音", use_container_width=True): 
                    play_audio(display['word'], silent=True)
            
            st.markdown("---")
            st.subheader("📖 专业场景例句")
            for i, s in enumerate(display['sentences'], 1):
                st.markdown(f"""
                    <div class="card-item">
                        <div style="font-size:1.1rem; color:#1E3A8A;"><b>{i}. {s["jp"]}</b></div>
                        <div style="margin-top:4px; color:#64748B; font-size:0.9rem;">{s["kana"]}</div>
                        <div style="margin-top:6px; color:#059669; font-weight:500;">{s["cn"]}</div>
                    </div>
                """, unsafe_allow_html=True)
                col1, col2, _ = st.columns([1, 1, 3])
                if col1.button(f"▶️ 标准速 {i}", key=f"std_{i}"): play_audio(s["jp"], silent=True)
                if col2.button(f"🐢 慢速 {i}", key=f"slo_{i}"): play_audio(s["jp"], slow=True, silent=True)
