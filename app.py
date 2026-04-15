import streamlit as st
from openai import OpenAI
import json
from gtts import gTTS
import io

# --- 1. 核心翻译逻辑 (极致稳定性加固) ---
def get_expert_translation(u_in):
    try:
        client = OpenAI(api_key=st.secrets["NEW_API_KEY"], base_url=st.secrets["NEW_BASE_URL"])
        # 强制要求 AI 必须翻译输入框中的词，严禁产生任何联觉
        prompt = f"NHK Standard. Translate ONLY the specific word '{u_in}' to native Japanese. Return JSON ONLY."
        comp = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "Professional Japanese Editor. Accuracy is your priority. Return JSON: {\"word\":\"\",\"reading\":\"\",\"pos\":\"\",\"level\":\"\",\"pitch\":\"\",\"sentences\":[{\"jp\":\"\",\"kana\":\"\",\"cn\":\"\"}]}"}],
            response_format={"type": "json_object"},
            temperature=0
        )
        data = json.loads(comp.choices[0].message.content)
        return data
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
    .word-box { background:white; padding:20px; border-radius:12px; border:1px solid #E5E7EB; text-align:center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .card-item { border:1px solid #3B82F6; padding:12px; border-radius:10px; margin-bottom:10px; background:#F8FAFC; border-left: 6px solid #1E3A8A; }
</style>""", unsafe_allow_html=True)

WELCOME_DATA = {
    "word": "こんにちは", "reading": "こんにちは", "pos": "感嘆詞", "level": "N5", "pitch": "平板",
    "sentences": [
        {"jp": "こんにちは、今日もよろしくお願いします。", "kana": "こんにちは、きょうもよろしくおねがいします。", "cn": "你好，今天也请多多关照。"},
        {"jp": "FUSION Proへようこそ、一緒に勉強しましょう。", "kana": "フュージョンプロへようこそ、いっしょにべんきょうしましょう。", "cn": "欢迎来到FUSION Pro，让我们一起学习吧。"},
        {"jp": "日本語の美しさを感じてください。", "kana": "にほんごのうつくしさをかんじてください。", "cn": "请感受日语的美。"}
    ]
}

# --- 3. 页面路由 ---
with st.sidebar:
    st.markdown("## FUSION Pro")
    menu = st.radio("功能切换", ["AI 词汇专家", "五十音实验室", "每周 7 句金句"])
    st.markdown("---")
    st.markdown("<p style='color:#3B82F6; font-weight:bold; text-align:center;'>🌸 今日も、一緒に頑張りましょう！</p>", unsafe_allow_html=True)

# --- 模块 A: AI 词汇专家 (逻辑同步锁) ---
if menu == "AI 词汇专家":
    st.header("AI 词汇专家")
    st.markdown("<h4 style='text-align:center; color:#3B82F6;'>今日も、一緒に頑張りましょう！</h4>", unsafe_allow_html=True)
    
    # 获取用户输入
    current_input = st.text_input("请输入中文词汇 (回车提交)", key="word_input_key")
    
    # 逻辑核心：一旦输入改变，立即重置状态，绝不保留旧数据
    if current_input:
        # 如果当前缓存的关键词不等于输入框内容，执行物理清理并请求
        if "sync_lock_word" not in st.session_state or st.session_state.sync_lock_word != current_input:
            st.session_state.sync_lock_word = current_input
            st.session_state.current_data = None # 物理清理
            
            with st.spinner(f"正在为您同步‘{current_input}’的专家级解析..."):
                res = get_expert_translation(current_input)
                if res:
                    st.session_state.current_data = res
                    play_audio(f"これについて、以下の日本語が考えられます。{res['word']}")
        
        # 渲染区：只有当数据存在且确保属于当前输入的词时才显示
        display = st.session_state.get('current_data')
        if display:
            st.markdown(f"""<div class="word-box">
                <h2 style="margin:0; color:#1E3A8A;">{display['word']}</h2>
                <p style="color:#3B82F6; font-size:1.2rem; font-weight:bold;">【{display['reading']}】</p>
                <p style="color:#64748B; font-size:0.8rem;">🏷️ {display.get('pos','')} | {display.get('level','')} | {display.get('pitch','')}</p>
            </div>""", unsafe_allow_html=True)
            for i, s in enumerate(display['sentences'], 1):
                st.markdown(f'<div class="card-item"><b>{i}. {s["jp"]}</b><br><small>{s["kana"]}</small><br><span style="color:#059669;">{s["cn"]}</span></div>', unsafe_allow_html=True)
                if st.button(f"🔊 播放例句 {i}", key=f"v_{i}"): play_audio(s["jp"])
    else:
        # 输入为空时回归初始界面
        st.session_state.sync_lock_word = ""
        st.session_state.current_data = None
        st.markdown(f"""<div class="word-box">
            <h2 style="margin:0; color:#1E3A8A;">{WELCOME_DATA['word']}</h2>
            <p style="color:#3B82F6; font-size:1.2rem; font-weight:bold;">【{WELCOME_DATA['reading']}】</p>
        </div>""", unsafe_allow_html=True)
        for i, s in enumerate(WELCOME_DATA['sentences'], 1):
            st.markdown(f'<div class="card-item"><b>{i}. {s["jp"]}</b><br><small>{s["kana"]}</small><br><span style="color:#059669;">{s["cn"]}</span></div>', unsafe_allow_html=True)

# 遵守指示：保持其他模块原样
elif menu == "五十音实验室":
    st.header("五十音实验室")
    st.info("模块运行中...")

elif menu == "每周 7 句金句":
    st.header("每周 7 句金句")
    st.info("内容同步中...")
