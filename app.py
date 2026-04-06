import streamlit as st
from groq import Groq
import json
from gtts import gTTS
import io

# 1. 核心配置：API 钥匙直接嵌入
API_KEY = "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"
client = Groq(api_key=API_KEY)

# 定义发音生成器：将文字转为音频流
def get_audio(text):
    if not text or text == "未获取到内容":
        return None
    try:
        tts = gTTS(text=text, lang='ja')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp
    except:
        return None

# 2. 页面美化设置
st.set_page_config(page_title="AI日语联想学习", layout="centered")
st.title("JP 日本語学習 - 智能联想系统 2.3")
st.caption("逻辑加固版 - 解决内容缺失与翻译错误")
# 3. 交互逻辑
user_input = st.text_input("📝 请输入中文单词或成语：", placeholder="例如：名落孙山")

if user_input:
    with st.spinner('专家正在精准校对所有字段，请稍候...'):
        try:
            # 强化指令：通过范例强制 AI 填满所有字段，降低幻觉
            prompt = f"""
            你是一位严谨的日语教育专家。请针对中文输入 '{user_input}' 联想一个最贴切的日语单词。
            
            必须严格遵守以下输出规范：
            1. 必须联想真实的、常用的日语词汇（如：工作 -> 仕事）。
            2. JSON中的所有字段（word, reading, pitch, pronunciation_tip, sentences）严禁为空。
            3. 即使是简单的词，也要生成完整的3句标准日语例句。
            
            范例参考：
            输入：秋
            输出：{{ 
                "word": "秋", 
                "reading": "あき", 
                "pitch": "[1]", 
                "pronunciation_tip": "注意‘あ’的开口度要自然", 
                "sentences": ["秋は涼しい季節です。", "公園で秋の紅葉を見ます。", "美味しい秋の味覚を楽しみましょう。"] 
            }}

            请处理当前输入：{user_input}
            """
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "你是一个严谨的日语老师，只输出完整且准确的JSON数据。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2, # 极低温度确保逻辑稳定
                response_format={"type": "json_object"}
            )
            
            # 使用 .get() 方法安全获取数据，防止空字段崩溃
            data = json.loads(completion.choices[0].message.content)
            res = {
                "word": data.get("word", "未获取内容"),
                "reading": data.get("reading", "未获取内容"),
                "pitch": data.get("pitch", "未知"),
                "tip": data.get("pronunciation_tip", "请参考录音进行练习"),
                "sents": data.get("sentences", ["例句生成失败", "例句生成失败", "例句生成失败"])
            }
            
            # --- 结果展示界面 ---
            st.success("✨ 专家联想成功")
            
            col_w1, col_w2 = st.columns([3, 1])
            with col_w1:
                st.header(f"{res['word']} ({res['reading']})")
                st.write(f"**音调核：** {res['pitch']}")
            with col_w2:
                word_audio = get_audio(res['word'])
                if word_audio:
                    st.write("📢 单词发音")
                    st.audio(word_audio, format='audio/mp3')

            st.info(f"💡 专家建议：{res['tip']}")
            st.divider()
            
            st.subheader("📖 专家级例句练习")
            for idx, s in enumerate(res['sents'], 1):
                col_a, col_b = st.columns([0.75, 0.25])
                with col_a:
                    st.write(f"**{idx}.** {s}")
                with col_b:
                    sent_audio = get_audio(s)
                    if sent_audio:
                        st.audio(sent_audio, format='audio/mp3')

        except Exception as e:
            st.error("❌ 发生了点小麻烦，请再按一次回车尝试。")
