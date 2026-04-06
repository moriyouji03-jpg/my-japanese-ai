import streamlit as st
from groq import Groq
import json

# 1. 强制设定 API Key（直接焊死，排除 Secrets 干扰）
API_KEY = "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"
client = Groq(api_key=API_KEY)

# 2. 页面设置
st.set_page_config(page_title="AI日语联想学习", layout="centered")
st.title("JP 日本語学習 - 智能联想系统")
st.caption("基于 Llama3 驱动的 N5-N4 深度学习助手")

# 3. 输入框
user_input = st.text_input("📝 请输入中文单词或成语：", placeholder="例如：名落孙山")

if user_input:
    with st.spinner('顶级专家正在为您联想最合适的日语表达...'):
        try:
            # 专家指令集
            prompt = f"""
            你是一位精通中日双语的教育专家。请针对用户输入的词语 '{user_input}' 执行：
            1. 联想一个最贴切的N5-N4级别日语核心单词。
            2. 标注NHK标准音调核（如 [0], [1]）。
            3. 给出1句专业的发音提醒。
            4. 生成3句严谨的N5-N4水平例句，必须包含主谓宾。
            
            必须严格按以下JSON格式输出，禁止任何多余文字：
            {{
                "word": "单词",
                "reading": "假名",
                "pitch": "音调核",
                "pronunciation_tip": "发音建议",
                "sentences": ["例句1", "例句2", "例句3"]
            }}
            """
            
            # 调用 AI
            completion = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                response_format={"type": "json_object"}
            )
            
            # 解析结果
            result = json.loads(completion.choices[0].message.content)
            
            # 漂亮地展示出来
            st.success(f"✨ 联想成功：{result['word']}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("单词/假名", f"{result['word']} ({result['reading']})")
            with col2:
                st.metric("音调核", result['pitch'])
            
            st.info(f"💡 发音秘籍：{result['pronunciation_tip']}")
            
            st.subheader("📖 基础例句练习")
            for idx, sent in enumerate(result['sentences'], 1):
                st.write(f"{idx}. {sent}")

        except Exception as e:
            st.error(f"❌ 发生了一点意外：{str(e)}")
            st.warning("建议：请检查 Groq API Key 是否依然有效，或者稍微等几秒再试。")
