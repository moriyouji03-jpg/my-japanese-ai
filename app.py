import streamlit as st
from openai import OpenAI
import json
from gtts import gTTS
import io

# --- 1. 核心翻译逻辑 (仅针对词汇专家强化) ---
def get_expert_translation(u_in):
    try:
        client = OpenAI(api_key=st.secrets["NEW_API_KEY"], base_url=st.secrets["NEW_BASE_URL"])
        prompt = f"Expert Japanese Translate '{u_in}'. Return JSON ONLY."
        comp = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "Return valid JSON: {\"word\":\"\",\"reading\":\"\",\"pos\":\"\",\"level\":\"\",\"pitch\":\"\",\"sentences\":[{\"jp\":\"\",\"kana\":\"\",\"cn\":\"\"}]}"}],
            response_format={"type": "json_object"},
            temperature=0
        )
        return json.loads(comp.choices[0].message.content)
    except: return None

def play_audio(text):
    try:
        tts = gTTS(text=text, lang='ja')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        st.audio(fp, format="audio/mp3", autoplay=True)
    except: pass

# --- 2. 界面设计 ---
st.set_page_config(page_title="FUSION Pro", layout="wide")

st.markdown("""<style>
    [data-testid="stSidebar"] { background-color: #0F172A; }
    [data-testid="stSidebar"] * { color: #F1F5F9 !important; }
    .stAudio { display:none !important; }
    .word-box { background:white; padding:20px; border-radius:12px; border:1px solid #E5E7EB; text-align:center; }
    .card-item { border:1.5px solid #3B82F6; padding:12px; border-radius:10px; margin-bottom:10px; background:#F8FAFC; border-left: 6px solid #1E3A8A; }
</style>""", unsafe_allow_html=True)

# 初始引导页面数据
WELCOME_DATA = {
    "word": "こんにちは", "reading": "こんにちは", "pos": "感嘆詞", "level": "N5", "pitch": "平板",
    "sentences": [
        {"jp": "こんにちは、今日もよろしくお願いします。", "kana": "こんにちは、きょうもよろしくおねがいします。", "cn": "你好，今天也请多多关照。"},
        {"jp": "FUSION Proへようこそ、一緒に勉強しましょう。", "kana": "フュージョンプロへようこそ、いっしょにべんきょうしましょう。", "cn": "欢迎来到FUSION Pro，让我们一起学习吧。"},
        {"jp": "日本語の美しさを感じてください。", "kana": "にほんごのうつくしさをかんじてください。", "cn": "请感受日语的美。"}
    ]
}

# --- 3. 页面路由 (严格遵守指令：只动词汇专家) ---
with st.sidebar:
    st.markdown("## FUSION Pro")
    menu = st.radio("功能切换", ["AI 词汇专家", "五十音实验室", "每周 7 句金句"])
    st.markdown("---")
    st.markdown("<p style='color:#3B82F6; text-align:center;'>🌸 今日も、一緒に頑張りましょう！</p>", unsafe_allow_html=True)

if menu == "AI 词汇专家":
    st.header("AI 词汇专家")
    st.markdown("<h4 style='text-align:center; color:#3B82F6;'>今日も、一緒に頑張りましょう！</h4>", unsafe_allow_html=True)
    
    # 词汇查询输入框
    u_in = st.text_input("请输入中文词汇 (回车提交)", key="word_search_box")
    
    # 【核心逻辑修复】：物理隔离，确保输入与显示绝对同步
    if u_in:
        # 只要当前缓存的单词与输入框不一致，立即重新加载
        if "sync_word" not in st.session_state or st.session_state.sync_word != u_in:
            with st.spinner("AI 专家正在校准翻译..."):
                res = get_expert_translation(u_in)
                if res:
                    st.session_state.expert_res = res
                    st.session_state.sync_word = u_in
                    play_audio(f"これについて、以下の日本語が考えられます。{res['word']}")
        
        # 提取渲染数据
        display_data = st.session_state.get('expert_res')
        
        # 二次强校验：如果数据所属单词与输入框不匹配，拒绝渲染（防止张冠李戴）
        if display_data and st.session_state.sync_word == u_in:
            st.markdown(f"""<div class="word-box">
                <h2 style="margin:0; color:#1E3A8A;">{display_data['word']}</h2>
                <p style="color:#3B82F6; font-size:1.2rem; font-weight:bold;">【{display_data['reading']}】</p>
                <p style="color:#64748B; font-size:0.8rem;">🏷️ {display_data.get('pos','')} | {display_data.get('level','')} | {display_data.get('pitch','')}</p>
            </div>""", unsafe_allow_html=True)
            for i, s in enumerate(display_data['sentences'], 1):
                st.markdown(f'<div class="card-item"><b>{i}. {s["jp"]}</b><br><small>{s["kana"]}</small><br><span style="color:#059669;">{s["cn"]}</span></div>', unsafe_allow_html=True)
                if st.button(f"🔊 播放例句 {i}", key=f"v_{i}"): play_audio(s["jp"])
    else:
        # 输入为空时，强制回归初始状态，清理所有历史残余
        st.session_state.sync_word = ""
        st.session_state.expert_res = None
        display_data = WELCOME_DATA
        st.markdown(f"""<div class="word-box">
            <h2 style="margin:0; color:#1E3A8A;">{display_data['word']}</h2>
            <p style="color:#3B82F6; font-size:1.2rem; font-weight:bold;">【{display_data['reading']}】</p>
        </div>""", unsafe_allow_html=True)
        for i, s in enumerate(display_data['sentences'], 1):
            st.markdown(f'<div class="card-item"><b>{i}. {s["jp"]}</b><br><small>{s["kana"]}</small><br><span style="color:#059669;">{s["cn"]}</span></div>', unsafe_allow_html=True)

# 遵守指示：以下模块保持原样，不做任何改动
elif menu == "五十音实验室":
    st.header("五十音实验室")
    st.info("模块运行中...")

elif menu == "每周 7 句金句":
    st.header("每周 7 句金句")
    st.info("内容同步中...")
