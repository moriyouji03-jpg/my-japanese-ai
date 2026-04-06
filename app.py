import streamlit as st
from groq import Groq
import json
from gtts import gTTS
import io

# 1. 核心配置：API 钥匙
API_KEY = "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"
client = Groq(api_key=API_KEY)

# 定义发音生成器
def get_audio(text):
    try:
        tts = gTTS(text=text, lang='ja')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp
    except:
        return None

# 2. 页面美化
st.set_page_config(page_title="AI日语联想学习", layout="centered")
st.title("JP 日本語学習 - 智能联想系统 2.2")
st.caption("由 Llama-3.3 深度微调 - 专家级日语逻辑")
# 3. 交互逻辑
user_input = st.text_input("📝 请输入中文单词或成语：", placeholder="例如：名落孙山")

if user_input:
    with st.spinner('顶级专家正在严谨构思并校对中...'):
        try:
            # 强化 Prompt：降低随机性，强制输出标准日语
            prompt = f"""
            你是一位拥有20年经验的专业日语教师。请针对中文 '{user_input}'，
            联想一个逻辑最相关的**真实存在的常用日语单词**。
            
            严禁生成乱码或中文式日语。
            必须严格按以下JSON格式回复：
            {{
                "word": "标准日语汉字",
                "reading": "平假名",
                "pitch": "音调核数字",
                "pronunciation_tip": "一句发音建议",
                "sentences": ["标准例句1", "标准例句2", "标准例句3"]
            }}
            """
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "你是一个只输出严谨、正确日语JSON的机器人。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3, # 极低温度确保逻辑严密
                response_format={"type": "json_object"}
            )
            
            result = json.loads(completion.choices[0].message.content)
            
            # --- 结果展示 ---
            st.success(f"✨ 专家联想成功")
            
            col_w1, col_w2 = st.columns([3, 1])
            with col_w1:
                st.header(f"{result['word']} ({result['reading']})")
                st.write(f"**音调核：** {result['pitch']}")
            with col_w2:
                audio = get_audio(result['word'])
                if audio:
                    st.write("📢 单词发音")
                    st.audio(audio, format='audio/mp3')

            st.info(f"💡 专家建议：{result['pronunciation_tip']}")
            st.divider()
            
            st.subheader("📖 专家级例句练习")
            for idx, sent in enumerate(result['sentences'], 1):
                c1, c2 = st.columns([0.7, 0.3])
                with c1:
                    st.write(f"**{idx}.** {sent}")
                with c2:
                    sent_audio = get_audio(sent)
                    if sent_audio:
                        st.audio(sent_audio, format='audio/mp3')

        except Exception as e:
            st.error(f"❌ 逻辑模块波动，请尝试刷新。")
