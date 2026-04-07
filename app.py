import streamlit as st
from groq import Groq
import json
from gtts import gTTS
import io

# 1. 配置
API_KEY = "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"
client = Groq(api_key=API_KEY)

# 2. 注入 FUSION 顶级科学 UI 样式 (参考截图1, 2)
st.markdown("""
    <style>
    /* 强制标题单行并美化 */
    .fusion-banner {
        white-space: nowrap;
        color: #1E3A8A;
        font-size: 2.2rem;
        font-weight: 800;
        padding-bottom: 10px;
        border-bottom: 3px solid #3B82F6;
        margin-bottom: 30px;
        font-family: 'Inter', sans-serif;
    }
    /* 科学卡片布局 */
    .info-card { 
        background: white; 
        padding: 25px; 
        border-radius: 18px; 
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05); 
        border-left: 6px solid #3B82F6; 
        margin-bottom: 25px; 
    }
    .index-circle {
        background: #3B82F6;
        color: white;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-right: 12px;
        font-size: 0.9rem;
    }
    .kana-sub { background: #F3F4F6; color: #6B7280; padding: 3px 8px; border-radius: 5px; font-size: 0.85rem; }
    /* 隐藏原生播放器，实现点击即播的清爽感 */
    .stAudio { display: none; } 
    </style>
    """, unsafe_allow_html=True)

# 初始化播放状态
if "audio_config" not in st.session_state:
    st.session_state.audio_config = {"text": None, "slow": False, "key": 0}
if "last_result" not in st.session_state:
    st.session_state.last_result = None

def get_audio(text, slow=False):
    if not text: return None
    try:
        tts = gTTS(text=text, lang='ja', slow=slow)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp
    except: return None
        # 3. 顶部单行标题
st.markdown('<div class="fusion-banner">FUSION 智能化日语学习系统 1.0</div>', unsafe_allow_html=True)

# 4. 搜索区 (参考截图3)
col_s1, col_s2 = st.columns([4, 1])
with col_s1:
    user_input = st.text_input("", placeholder="输入中文词，即刻开启专家级联想学习...", label_visibility="collapsed")
with col_s2:
    search_btn = st.button("查询结果", type="primary", use_container_width=True)

# 核心逻辑
if (user_input or search_btn) and user_input:
    if not st.session_state.last_result or st.session_state.last_result.get('input') != user_input:
        with st.spinner('FUSION Engine 正在进行科学建模...'):
            prompt = f"""
            你是一位顶尖日语教育专家。针对输入 '{user_input}'，联想一个最贴切的日语词并生成3个例句。
            必须严格输出JSON:
            {{
                "word": "汉字词", "reading": "假名", "pos": "词性", "level": "JLPT级别", "pitch": "[数字]",
                "sentences": [
                    {{"jp":"原文","kana":"全假名","cn":"中文翻译","en":"English"}}
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
            # 5. 结果渲染
if st.session_state.last_result:
    res = st.session_state.last_result
    
    # 衔接语
    st.markdown(f"#### 💡 これについて、以下の日本語が考えられます。")

    # 单词卡片
    with st.container():
        c1, c2 = st.columns([0.75, 0.25])
        with c1:
            st.markdown(f"""
            <div class="info-card">
                <div style="font-size: 2.2rem; font-weight: 700;">{res['word']} <span style="font-size: 1.2rem; color: #64748b; font-weight: 400;">({res['reading']})</span></div>
                <div style="margin-top: 10px; color: #3B82F6; font-weight: 600;">🏷️ {res['pos']} | {res['level']} | 声调: {res['pitch']}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2 if 'col2' in locals() else c2: # 兼容处理
            if st.button("🔊 播放单词", key="v_main", use_container_width=True):
                st.session_state.audio_config = {"text": res['word'], "slow": False, "key": st.session_state.audio_config["key"]+1}

    st.divider()

    # 科学例句卡片层 (参考截图2)
    st.subheader("参考文例 (3つの例文)")
    for idx, s in enumerate(res['sentences'], 1):
        col_text, col_btn = st.columns([0.7, 0.3])
        
        with col_text:
            st.markdown(f"""
            <div style="display: flex; align-items: flex-start; margin-bottom: 25px;">
                <div class="index-circle">{idx}</div>
                <div>
                    <div style="font-size: 1.25rem; font-weight: 600; color: #1E293B;">{s['jp']}</div>
                    <div style="margin-top: 4px;"><span class="kana-sub">{s['kana']}</span></div>
                    <div style="color: #059669; margin-top: 10px; border-left: 3px solid #E5E7EB; padding-left: 12px; font-size: 0.95rem;">{s['cn']}</div>
                    <div style="color: #64748b; font-size: 0.85rem; padding-left: 15px;">{s['en']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_btn:
            # 双速按钮：参考截图2的绿/红配色
            if st.button(f"🟢 普通の速さ", key=f"norm_{idx}", use_container_width=True):
                st.session_state.audio_config = {"text": s['jp'], "slow": False, "key": st.session_state.audio_config["key"]+1}
            
            if st.button(f"🔴 ゆっくり", key=f"slow_{idx}", use_container_width=True):
                st.session_state.audio_config = {"text": s['jp'], "slow": True, "key": st.session_state.audio_config["key"]+1}

    # 底部隐形播放触发器（核心：不产生视觉干扰）
    if st.session_state.audio_config["text"]:
        # 每次点击按钮，此处的 key 都会变化，强制重新加载音频实现点哪读哪
        with st.empty():
            audio_stream = get_audio(st.session_state.audio_config["text"], slow=st.session_state.audio_config["slow"])
            if audio_stream:
                st.audio(audio_stream, format="audio/mp3", autoplay=True)
