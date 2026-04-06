import streamlit as st
from groq import Groq
import json

# 1. 页面基础设置 (对应截图1的顶部)
st.set_page_config(page_title="AI日语联想学习", layout="centered")

# 2. 检查是否有 AI 钥匙 (API Key)
client = Groq(api_key="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")

st.title("🇯🇵 日本語学習 - 智能联想系统")
st.caption("基于 Llama3 驱动的 N5-N4 深度学习助手")

# 3. 输入框 (用户输入中文或成语)
user_input = st.text_input("📚 请输入中文单词或成语：", placeholder="例如：胸有成竹")

if user_input:
    with st.spinner('顶级专家正在为您联想最合适的日语表达...'):
        # 专家指令集 (Prompt) - 确保输出符合 NHK 和 N4/N5 标准
        prompt = f"""
        你是一位精通中日双语的教育专家。请针对用户输入的词语 '{user_input}' 执行：
        1. 联想一个最贴切的N5-N4级别日语核心单词。
        2. 标注NHK标准音调核（如 [0], [1]）。
        3. 给出1句专业的发音提醒。
        4. 生成3句严谨的N5-N4水平例句，必须包含主谓宾。
        
        必须严格按以下JSON格式输出，禁止任何多余文字：
        {{
            "word": "单词",
            "kana": "假名",
            "accent": "音调",
            "remind": "提醒内容",
            "s1": ["日文例句", "平假名读音", "中文翻译"],
            "s2": ["日文例句", "平假名读音", "中文翻译"],
            "s3": ["日文例句", "平假名读音", "中文翻译"]
        }}
        """
        
        try:
            # 调用 Groq AI 接口
            completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192",
                response_format={"type": "json_object"}
            )
            res = json.loads(completion.choices[0].message.content)

            # 4. 视觉与听觉展示 (对应截图2)
            st.divider()
            
            # 自动播放系统引导语音
            st.audio(f"https://dict.youdao.com/dictvoice?audio=これをみると、日本語の言葉を思い出します&le=jap")
            st.info("💡 これをみると、日本語の言葉を思い出します")

            # 单词核心卡片 (彩色背景模拟截图)
            st.success(f"### {res['word']} ({res['kana']})  音调：{res['accent']}")
            st.warning(f"⚠️ 发音提醒：{res['remind']}")

            # 三条标准例句 (对应截图3)
            st.subheader("参考例句 (N5-N4级别)：")
            for key in ['s1', 's2', 's3']:
                st.write(f"**{res[key][0]}**")
                st.caption(f"发音：{res[key][1]}")
                st.write(f"中文：{res[key][2]}")
                # 每一句都配上发音按钮
                st.audio(f"https://dict.youdao.com/dictvoice?audio={res[key][0]}&le=jap")
                st.divider()
        
        except Exception as e:
            st.error("暂时无法获取内容，请检查 API Key 配置或网络。")
