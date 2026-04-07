import streamlit as st
from groq import Groq
import json
from gtts import gTTS
import io

# 1. 核心配置
API_KEY = "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"
client = Groq(api_key=API_KEY)

# 2. 注入 FUSION 1.0 专属顶级 UI 样式
st.markdown("""
    <style>
    .main { background-color: #f4f7fb; }
    .fusion-title { color: #1E3A8A; font-family: 'Inter', sans-serif; font-weight: 800; font-size: 2.8rem; margin-bottom: 0px; }
    .fusion-subtitle { color: #3B82F6; font-size: 1rem; letter-spacing: 2px; margin-bottom: 2rem; text-transform: uppercase; }
    .info-card { background: white; padding: 25px; border-radius: 18px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); border-left: 6px solid #3B82F6; margin-bottom: 25px; }
    .word-header { font-size: 2.2rem; font-weight: 700; color: #1e293b; }
    .reading-text { font-size: 1.3rem; color: #64748b; font-weight: 400; margin-left: 10px; }
    .tag-container { margin-top: 12px; display: flex; gap: 8px; }
    .tag-blue { background: #dbeafe; color: #1e40af; padding: 4px 12px; border-radius: 8px; font-size: 0.85rem; font-weight: 600; }
    .tag-red { background: #fee2e2; color: #991b1b; padding: 4px 12px; border-radius: 8px; font-size: 0.85rem; font-weight: 600; }
    .sentence-box { background: white; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 15px; transition: all 0.3s; }
    .sentence-box:hover { border-color: #3B82F6; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1); }
    </style>
    """, unsafe_allow_html=True)

if "playing_id" not in st.session_state:
    st.session_state.playing_id = None
if "last_result" not in st.session_state:
    st.session_state.last_result = None

def get_audio(text):
    if not text: return None
    try:
        tts = gTTS(text=text, lang='ja')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp
    except: return None
    # 3. 头部视觉展示
st.markdown('<h1 class="fusion-title">FUSION</h1>', unsafe_allow_html=True)
st.markdown('<p class="fusion-subtitle">智能化日语学习系统 1.0</p>', unsafe_allow_html=True)

# 4. 搜索组件（参考截图3的蓝白风格）
col_s1, col_s2 = st.columns([4, 1])
with col_s1:
    user_input = st.text_input("Search", placeholder="请输入中文单词或成语，如：画蛇添足、工作、爱情", label_visibility="collapsed")
with col_s2:
    search_btn = st.button("查询结果", type="primary", use_container_width=True)

# 逻辑触发
if (user_input or search_btn) and user_input:
    if not st.session_state.last_result or st.session_state.last_result.get('input') != user_input:
        with st.spinner('FUSION Engine 正在检索标准日语词库...'):
            prompt = f"""
            针对 '{user_input}'，联想一个最贴切的日语词并生成3个例句。
            必须严格输出JSON:
            {{
                "word": "日文汉字词",
                "reading": "平假名",
                "pitch_symbol": "[数字]",
                "pitch_type": "声调类型",
                "pos": "词性",
                "level": "JLPT级别",
                "tip": "发音提醒",
                "sentences": [
                    {{"jp":"日语句子","kana":"全假名","cn":"中文翻译","en":"英文翻译"}}
                ]
            }}
            """
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            res_data = json.loads(completion.choices[0].message.content)
            res_data['input'] = user_input
            st.session_state.last_result = res_data
            st.session_state.playing_id = None
# 5. 结果渲染层
if st.session_state.last_result:
    res = st.session_state.last_result
    
    st.markdown(f"#### 💡 これについて、以下の日本語が考えられます。")

    # 单词卡片框架 (参考截图1)
    st.markdown(f"""
    <div class="info-card">
        <div class="word-header">{res['word']}<span class="reading-text">（{res['reading']}）</span></div>
        <div class="tag-container">
            <span class="tag-blue">词性：{res['pos']}</span>
            <span class="tag-blue">难度：{res['level']}</span>
            <span class="tag-red">声调：{res['pitch_symbol']} {res['pitch_type']}</span>
        </div>
        <p style="margin-top:15px; color:#475569; font-style:italic;">💡 专家建议：{res['tip']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 主发音
    ca1, ca2 = st.columns([1, 4])
    with ca1:
        if st.button("🔊 播放单词", key="main_voice"):
            st.session_state.playing_id = "main"
    with ca2:
        if st.session_state.playing_id == "main":
            st.audio(get_audio(res['word']), format="audio/mp3", autoplay=True)

    st.divider()

    # 造句层 (参考截图2)
    st.subheader("📖 专家监修例句 (主谓宾结构)")
    for idx, s in enumerate(res['sentences'], 1):
        with st.container():
            st.markdown(f"""
            <div class="sentence-box">
                <p style="font-size:1.2rem; color:#1e293b; font-weight:600; margin-bottom:5px;">{idx}. {s['jp']}</p>
                <p style="color:#94a3b8; font-size:0.95rem; margin-bottom:12px;">{s['kana']}</p>
                <p style="color:#059669; margin-bottom:4px;">🇨🇳 {s['cn']}</p>
                <p style="color:#2563eb;">🇺🇸 {s['en']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 例句发音
            sa1, sa2 = st.columns([1, 4])
            with sa1:
                if st.button(f"🔊 朗读例句 {idx}", key=f"s_v_{idx}"):
                    st.session_state.playing_id = f"sent_{idx}"
            with sa2:
                if st.session_state.playing_id == f"sent_{idx}":
                    st.audio(get_audio(s['jp']), format="audio/mp3", autoplay=True)
