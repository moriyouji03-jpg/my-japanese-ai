import streamlit as st
from openai import OpenAI
import json
from gtts import gTTS
import io
import time

# --- 1. 核心数据库：100% 纯净五十音、拗音及实战金句 ---
KANA_DATA = {
    "清音-行": {
        "あ行": [("あ","ア","a"), ("い","イ","i"), ("う","ウ","u"), ("え","エ","e"), ("お","オ","o")],
        "か行": [("か","カ","ka"), ("き","キ","ki"), ("く","ク","ku"), ("け","ケ","ke"), ("こ","コ","ko")],
        "さ行": [("さ","サ","sa"), ("し","シ","shi"), ("す","ス","su"), ("せ","セ","se"), ("そ","ソ","so")],
        "た行": [("た","タ","ta"), ("ち","チ","chi"), ("つ","ツ","tsu"), ("て","テ","te"), ("と","ト","to")],
        "な行": [("な","ナ","na"), ("に","ニ","ni"), ("ぬ","ヌ","nu"), ("ね","ネ","ne"), ("の","ノ","no")],
        "は行": [("は","ハ","ha"), ("ひ","ヒ","hi"), ("ふ","フ","fu"), ("へ","ヘ","he"), ("ほ","ホ","ho")],
        "ま行": [("ま","マ","ma"), ("み","ミ","mi"), ("む","ム","mu"), ("め","メ","me"), ("も","モ","mo")],
        "や行": [("や","ヤ","ya"), (None,None,None), ("ゆ","ユ","yu"), (None,None,None), ("よ","ヨ","yo")],
        "ら行": [("ら","ラ","ra"), ("り","リ","ri"), ("る","ル","ru"), ("れ","レ","re"), ("ろ","ロ","ro")],
        "わ行": [("わ","ワ","wa"), (None,None,None), (None,None,None), (None,None,None), ("を","ヲ","wo")],
        "ん": [("ん","ン","n"), (None,None,None), (None,None,None), (None,None,None), (None,None,None)]
    },
    "清音-段": {
        "あ段": [("あ","ア","a"), ("か","カ","ka"), ("さ","サ","sa"), ("た","タ","ta"), ("な","ナ","na"), ("は","ハ","ha"), ("ま","マ","ma"), ("や","ヤ","ya"), ("ら","ラ","ra"), ("わ","ワ","wa")],
        "い段": [("い","イ","i"), ("き","キ","ki"), ("し","シ","shi"), ("ち","チ","chi"), ("に","ニ","ni"), ("ひ","ヒ","hi"), ("み","ミ","mi"), ("り","リ","ri")],
        "う段": [("う","ウ","u"), ("く","ク","ku"), ("す","ス","su"), ("つ","ツ","tsu"), ("ぬ","ヌ","nu"), ("ふ","フ","fu"), ("む","ム","mu"), ("ゆ","ユ","yu"), ("る","ル","ru")],
        "え段": [("え","エ","e"), ("け","ケ","ke"), ("せ","セ","se"), ("て","テ","te"), ("ね","ネ","ne"), ("へ","ヘ","he"), ("め","メ","me"), ("れ","レ","re")],
        "お段": [("お","オ","o"), ("こ","コ","ko"), ("そ","ソ","so"), ("と","ト","to"), ("の","ノ","no"), ("ほ","ホ","ho"), ("も","モ","mo"), ("よ","ヨ","yo"), ("ろ","ロ","ro")]
    },
    "浊音/半浊音": {
        "が行": [("が","ガ","ga"), ("ぎ","ギ","gi"), ("ぐ","グ","gu"), ("げ","ゲ","ge"), ("ご","ゴ","go")],
        "ざ行": [("ざ","ザ","za"), ("じ","ジ","ji"), ("ず","ズ","zu"), ("ぜ","ゼ","ze"), ("ぞ","ゾ","zo")],
        "だ行": [("だ","ダ","da"), ("ぢ","ヂ","ji"), ("づ","ヅ","zu"), ("で","デ","de"), ("ど","ド","do")],
        "ば行": [("ば","バ","ba"), ("び","ビ","bi"), ("ぶ","ブ","bu"), ("べ","ベ","be"), ("ぼ","ボ","bo")],
        "ぱ行": [("ぱ","パ","pa"), ("ぴ","ピ","pi"), ("ぷ","プ","pu"), ("ぺ","ペ","pe"), ("ぽ","ポ","po")]
    },
    "拗音体系": {
        "清拗音": [("きゃ","キャ","kya"), ("きゅ","キュ","kyu"), ("きょ","キョ","kyo"), ("しゃ","シャ","sha"), ("しゅ","シュ","shu"), ("しょ","ショ","sho"), ("ちゃ","チャ","cha"), ("ちゅ","チュ","chu"), ("ちょ","チョ","cho")],
        "浊拗音": [("ぎゃ","ギャ","gya"), ("ぎゅ","ギュ","gyu"), ("ぎょ","ギョ","gyo"), ("じゃ","ジャ","ja"), ("じゅ","ジュ","ju"), ("じょ","ジョ","jo")],
        "半浊拗音": [("ぴゃ","ピャ","pya"), ("ぴゅ","ピュ","pyu"), ("ぴょ","ピョ","pyo")]
    }
}

WEEKLY_CONTENT = [
    {"jp": "明日の朝、会議に出席しなければなりません。", "cn": "明早，必须参加会议。"},
    {"jp": "試験前は毎日単語を覚えなければなりません。", "cn": "在考试前，必须每天记单词。"},
    {"jp": "どんなに忙しくても期限を守らなければなりません。", "cn": "不管再忙，也必须遵守期限。"},
    {"jp": "急かさないで、もうすぐ終わるから。", "cn": "不急，马上就结束了。"},
    {"jp": "遠慮しないでどうぞ。ご自由にお取りください。", "cn": "请不要客气，请随便拿。"},
    {"jp": "そんなに急がないでください。", "cn": "请别这样急。"},
    {"jp": "遠慮しないで言ってください。", "cn": "请不要顾虑的说。"}
]

# ============================================================
# 职场聊天常用表现・50句（BIZCHAT_CONTENT）
# 使用方法：
# 1) 把下面这个列表整个粘贴到 app.py 里 WEEKLY_CONTENT 定义的下方
# 2) 把 st.radio 那一行的选项列表，加上 "职场聊天常用句"
# 3) 把最下面的 elif 代码块，加在 “每周 7 句” 那个 elif 块的后面
# ============================================================

BIZCHAT_CONTENT = [
    # ---- 報告・進捗（报告・进度） ----
    {"jp": "只今、資料の作成が終わりました。", "cn": "刚刚资料制作完成了。"},
    {"jp": "会議の準備がすべて完了しました。", "cn": "会议的准备工作全部完成了。"},
    {"jp": "本日の業務内容をご報告いたします。", "cn": "向您报告今天的工作内容。"},
    {"jp": "現在、A社との打ち合わせを進めております。", "cn": "目前正在推进与A公司的会谈。"},
    {"jp": "進捗は予定通りです。", "cn": "进度按计划进行。"},
    {"jp": "少し遅れておりますが、明日中には終わります。", "cn": "稍有延迟，但明天之内会完成。"},
    {"jp": "先ほどメールを送信いたしました。", "cn": "刚才已发送邮件。"},
    {"jp": "本件、対応が完了しましたのでご確認ください。", "cn": "此事已处理完毕，请确认。"},
    {"jp": "今週の目標を達成いたしました。", "cn": "本周目标已达成。"},
    {"jp": "詳細は添付ファイルをご確認ください。", "cn": "详情请确认附件。"},

    # ---- 休暇・遅刻の連絡（请假・迟到通知） ----
    {"jp": "本日、体調不良のため、少しお休みをいただきたいです。", "cn": "今天因身体不适，想请个假。"},
    {"jp": "電車が遅れており、10分ほど遅刻いたします。", "cn": "电车晚点，会迟到大约10分钟。"},
    {"jp": "明日、私用のため半休をいただきたく存じます。", "cn": "明天因私事想请半天假。"},
    {"jp": "子どもが熱を出したため、早退させていただきます。", "cn": "孩子发烧了，需要早退。"},
    {"jp": "明日、通院のため午前中お休みをいただきます。", "cn": "明天要去医院，上午请假。"},
    {"jp": "大変申し訳ありませんが、本日は在宅勤務にさせてください。", "cn": "非常抱歉，今天想申请在家办公。"},
    {"jp": "交通機関の遅延により、到着が遅れます。", "cn": "由于交通延误，会晚到。"},
    {"jp": "急な用事で外出いたします。戻りは15時の予定です。", "cn": "临时有事外出，预计15点回来。"},

    # ---- お詫び・ミスの説明（道歉・失误说明） ----
    {"jp": "ご迷惑をおかけして、申し訳ございません。", "cn": "给您添麻烦了，非常抱歉。"},
    {"jp": "私のミスで、資料に誤りがありました。訂正いたします。", "cn": "是我的失误，资料有误，我会更正。"},
    {"jp": "対応が遅くなり、大変失礼いたしました。", "cn": "处理迟了，非常失礼。"},
    {"jp": "確認不足で、ご迷惑をおかけしました。", "cn": "由于确认不足，给您带来了麻烦。"},
    {"jp": "すぐに修正いたしますので、少々お待ちください。", "cn": "我马上修正，请稍等。"},
    {"jp": "今後このようなことがないよう、注意いたします。", "cn": "今后会注意，避免再发生这种情况。"},
    {"jp": "お手数をおかけし、申し訳ございません。", "cn": "劳烦您了，非常抱歉。"},
    {"jp": "誤った情報をお伝えしてしまい、失礼いたしました。", "cn": "之前给您的信息有误，非常抱歉。"},

    # ---- 依頼・お願い（请求・拜托） ----
    {"jp": "お忙しいところ恐れ入りますが、ご確認いただけますか。", "cn": "百忙之中打扰了，能请您确认一下吗。"},
    {"jp": "こちらの資料をご確認いただけますでしょうか。", "cn": "能麻烦您确认一下这份资料吗。"},
    {"jp": "お手数ですが、明日までにご返信をお願いいたします。", "cn": "麻烦您在明天之前回复。"},
    {"jp": "ご都合がよろしければ、明日お時間をいただけますか。", "cn": "如果方便的话，明天能占用您一点时间吗。"},
    {"jp": "パスワードを教えていただけませんか。", "cn": "能告诉我一下密码吗。"},
    {"jp": "会議室の予約をお願いできますか。", "cn": "能麻烦您预约一下会议室吗。"},
    {"jp": "こちらにサインをお願いいたします。", "cn": "请在这里签字。"},
    {"jp": "資料を今週中に送っていただけますと助かります。", "cn": "如果能在本周内把资料发给我就太好了。"},
    {"jp": "もし可能であれば、少し早めにご対応いただけますか。", "cn": "如果可以的话，能麻烦您早一点处理吗。"},
    {"jp": "ご不明な点がございましたら、お知らせください。", "cn": "如有不清楚的地方，请告诉我。"},

    # ---- 確認・返信（确认・回复） ----
    {"jp": "かしこまりました。対応いたします。", "cn": "明白了，我会处理的。"},
    {"jp": "承知いたしました。", "cn": "知道了／明白了。"},
    {"jp": "確認いたしましたので、問題ございません。", "cn": "已经确认过了，没有问题。"},
    {"jp": "内容を確認の上、改めてご連絡いたします。", "cn": "确认内容后会再联系您。"},
    {"jp": "ご連絡ありがとうございます。確認いたします。", "cn": "谢谢您的联系，我这边确认一下。"},
    {"jp": "了解いたしました。明日までに準備いたします。", "cn": "了解了，明天之前准备好。"},
    {"jp": "その件については、明日回答いたします。", "cn": "那件事明天给您答复。"},
    {"jp": "確認が取れ次第、ご連絡いたします。", "cn": "一确认完就联系您。"},

    # ---- 感謝・挨拶（感谢・问候） ----
    {"jp": "いつもお世話になっております。", "cn": "一直以来承蒙您的关照。"},
    {"jp": "ご協力いただき、ありがとうございます。", "cn": "感谢您的协助。"},
    {"jp": "お疲れ様でした。", "cn": "辛苦了。"},
    {"jp": "助かりました。ありがとうございます。", "cn": "帮了大忙了，谢谢。"},
    {"jp": "今後ともよろしくお願いいたします。", "cn": "今后也请多关照。"},
    {"jp": "貴重なお時間をいただき、ありがとうございました。", "cn": "感谢您抽出宝贵的时间。"},
]


# ============================================================
# ① st.radio 那一行，改成加入新选项（在 with st.sidebar: 里面）：
# ============================================================
#
# menu = st.radio("功能模块", ["AI 词汇专家", "五十音实验室", "每周 7 句", "职场聊天常用句"], index=0)


# ============================================================
# ② 在 “elif menu == "每周 7 句":” 那个代码块之后，加上这一段：
# ============================================================
#
# elif menu == "职场聊天常用句":
#     st.header("职场聊天常用表现　50句")
#     st.caption("按场景分类：报告进度 / 请假迟到 / 道歉说明 / 请求拜托 / 确认回复 / 感谢问候")
#     for i, item in enumerate(BIZCHAT_CONTENT, 1):
#         with st.expander(f"第 {i} 句：{item['jp']}"):
#             st.write(f"🇨🇳 中文：{item['cn']}")
#             if st.button("🔊 点击朗读该句", key=f"biz_{i}"):
#                 play_audio(item['jp'])

#*******************************************************************************************************************************************************************
# --- 2. 发音引擎核心 (物理强制重置版) ---
def play_audio(text_input):
    # 使用空容器强行清空之前的音频状态
    audio_placeholder = st.empty()
    try:
        def calibrate(t):
            # 锁定原音：は和へ直接映射为片假名发送给引擎，无多余符号，反应最快
            anchors = {"は": "ハ", "へ": "ヘ", "を": "ヲ"}
            return anchors.get(t, t)

        if isinstance(text_input, list):
            processed_text = "、".join([calibrate(t) for t in text_input if t])
        else:
            processed_text = calibrate(text_input)

        tts = gTTS(text=processed_text, lang='ja', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        
        # 物理注入：直接生成带 autoplay 的音频组件
        with audio_placeholder:
            st.audio(fp, format="audio/mp3", autoplay=True)
    except:
        pass

def get_expert_translation(u_in):
    try:
        client = OpenAI(api_key=st.secrets["NEW_API_KEY"], base_url=st.secrets["NEW_BASE_URL"])
        prompt = f"专家翻译'{u_in}'。JSON结构：word, reading, pos, level, pitch, sentences(3个含jp, kana, cn)。"
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "顶尖传译专家。只输出JSON。"}, {"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except: return None

# --- 3. UI 布局与样式 ---
st.set_page_config(page_title="FUSION Pro v4.5", layout="wide")

st.markdown("""<style>
    [data-testid="stSidebar"] { background-color: #0F172A !important; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label { 
        color: #FFFFFF !important; font-weight: 500 !important; 
    }
    audio { display:none !important; }
    .word-box { background:white; padding:15px; border-radius:12px; box-shadow:0 8px 20px rgba(0,0,0,0.05); border:1px solid #E5E7EB; text-align:center; }
    .card-item { border:1px solid #E2E8F0; padding:12px; border-radius:10px; margin-bottom:10px; background:#F8FAFC; border-left: 6px solid #1E3A8A; }
    .kana-card { background: white; border: 1px solid #E2E8F0; border-radius: 12px; padding: 10px 0; text-align: center; }
    .hiragana { font-size: 2rem; font-weight: bold; color: #1E3A8A; line-height: 1.1; }
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.title("FUSION Pro")
    menu = st.radio("功能模块", ["AI 词汇专家", "五十音实验室", "每周 7 句", "职场聊天常用句"], index=0)

# --- 模块 A: AI 词汇专家 (渲染加固) ---
if menu == "AI 词汇专家":
    st.header("AI 词汇专家")
    u_in = st.text_input("请输入中文词汇", placeholder="落实、对接")
    
    query = u_in.strip() if u_in else "你好"
    
    if query:
        if "last_query" not in st.session_state or st.session_state.last_query != query:
            res = get_expert_translation(query)
            if res:
                st.session_state.res_cache = res
                st.session_state.last_query = query
                play_audio("これについて、以下の日本語が考えられます")

        display = st.session_state.get('res_cache')
        if display:
            st.markdown(f"""<div class="word-box" style="max-width:650px; margin:auto;">
                <h1 style="color:#1E3A8A; margin:0;">{display.get('word','')}</h1>
                <p style="color:#3B82F6; font-size:1.2rem; font-weight:bold; margin:5px 0;">【{display.get('reading','')}】</p>
                <div style="font-size:0.8rem; color:#64748B;">🏷️ {display.get('pos','')} | 🏆 {display.get('level','')} | 📈 {display.get('pitch','')}型</div>
            </div>""", unsafe_allow_html=True)
            
            # 独立按钮区
            _, cm, _ = st.columns([1,1,1])
            if cm.button("🔊 播放单词正音", key=f"p_{query}"):
                play_audio(display.get('word',''))

            st.markdown("---")
            st.subheader("📖 专业场景例句")
            for i, s in enumerate(display.get('sentences', []), 1):
                st.markdown(f'<div class="card-item"><b>{i}. {s.get("jp","")}</b><br><small>{s.get("kana","")}</small><br><span style="color:#059669;">{s.get("cn","")}</span></div>', unsafe_allow_html=True)
                if st.button(f"🔊 朗读例句 {i}", key=f"sent_{query}_{i}"):
                    play_audio(s.get("jp",""))

# --- 模块 B: 五十音实验室 ---
elif menu == "五十音实验室":
    st.header("五十音实验室")
    selected_tab = st.segmented_control("音系", list(KANA_DATA.keys()), default="清音-行")
    
    if selected_tab in KANA_DATA:
        sub_cat = st.selectbox("分类", list(KANA_DATA[selected_tab].keys()))
        current_list = KANA_DATA[selected_tab][sub_cat]
        
        if st.button(f"🔊 节奏连读：{sub_cat}", use_container_width=True):
            play_audio([item[0] for item in current_list if item[0]])
                
        st.markdown("---")
        num_cols = 5 if "行" in sub_cat or "段" in sub_cat or "浊" in sub_cat else 3
        cols = st.columns(num_cols)
        for idx, item in enumerate(current_list):
            if item[0]:
                with cols[idx % num_cols]:
                    st.markdown(f"""<div class="kana-card">
                        <div class="hiragana">{item[0]}</div>
                        <div style="color:#64748B; font-size:0.9rem;">{item[1]}</div>
                        <div style="color:#3B82F6; font-weight:600;">{item[2]}</div>
                    </div>""", unsafe_allow_html=True)
                    if st.button("🔊", key=f"btn_{sub_cat}_{idx}"):
                        play_audio(item[0])

# --- 模块 C: 每周 7 句 ---
elif menu == "每周 7 句":
    st.header("每周 7 句实战金句")
    for i, item in enumerate(WEEKLY_CONTENT, 1):
        with st.expander(f"第 {i} 句：{item['jp']}"):
            st.write(f"🇨🇳 中文：{item['cn']}")
            if st.button(f"🔊 点击朗读该句", key=f"wk_{i}"):
                play_audio(item['jp'])

elif menu == "职场聊天常用句":
     st.header("职场聊天常用表现　50句")
     st.caption("按场景分类：报告进度 / 请假迟到 / 道歉说明 / 请求拜托 / 确认回复 / 感谢问候")
     for i, item in enumerate(BIZCHAT_CONTENT, 1):
         with st.expander(f"第 {i} 句：{item['jp']}"):
             st.write(f"🇨🇳 中文：{item['cn']}")
             if st.button("🔊 点击朗读该句", key=f"biz_{i}"):
                 play_audio(item['jp'])
