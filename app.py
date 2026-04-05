import streamlit as st

# 1. 页面基础设置
st.set_page_config(page_title="日语联想学习系统", layout="centered")

# 2. 标题和副标题 (对应截图1顶部)
st.title("🇯🇵 日本語学習 - 词汇与句子数据库")
st.write("N5-N4レベル学習システム")

# 3. 输入框 (对应截图1输入部分)
chinese_input = st.text_input("📚 请输入中文或成语：", placeholder="例如：下雨")

# 4. 展示区域 (只有输入后才显示)
if chinese_input:
    st.divider()
    
    # 模拟引导语和语音
    st.info("💡 これをみると、日本語の言葉を思い出します")
    
    # 单词卡片 (对应截图2)
    st.success(f"### 单词：雨 (あめ)  [1]型")
    st.warning("发音提醒：「あめがふる」的「ふ」是「f」音。绝对不要读成「下る」！")
    
    # 参考例句 (对应要求3)
    st.subheader("参考例句：")
    st.write("1. **雨が降ります。** (会下雨。)")
    st.write("2. **雨が降っています。** (正在下雨。)")
    st.write("3. **雨が降ったので、行きません。** (因为下雨，所以不去。)")
