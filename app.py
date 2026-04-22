<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>日语单词背诵测验</title>
    <style>
        /* 样式 (CSS) */
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f4f7f6;
            color: #333;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            background-color: #fff;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        h1 {
            color: #d32f2f; /* 日语红色 */
            text-align: center;
            margin-bottom: 25px;
        }

        .score-board {
            text-align: center;
            font-size: 1.1em;
            margin-bottom: 20px;
            padding: 10px;
            border-bottom: 2px solid #eee;
        }

        #question-area {
            min-height: 150px;
        }

        #question-display-wrapper {
            display: flex; /* 使用 Flexbox 布局 */
            align-items: center; /* 垂直居中 */
            justify-content: center; /* 水平居中 */
            margin-bottom: 30px;
            padding: 15px;
            background-color: #ffebee; /* 淡粉色背景 */
            border-radius: 8px;
        }

        #question-display {
            font-size: 1.8em;
            font-weight: bold;
            margin-right: 15px; /* 与小喇叭的间距 */
        }

        #speak-button {
            background: none;
            border: none;
            cursor: pointer;
            font-size: 2em; /* 增大图标大小 */
            color: #d32f2f;
            transition: transform 0.1s;
        }

        #speak-button:hover {
            transform: scale(1.1);
        }
        
        .answer-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }

        .answer-button {
            width: 100%;
            padding: 15px;
            font-size: 1em;
            cursor: pointer;
            border: 2px solid #ccc;
            border-radius: 8px;
            background-color: #fff;
            transition: all 0.2s;
            text-align: left;
            position: relative; /* 用于定位星星特效 */
            overflow: hidden; /* 防止星星溢出按钮 */
        }

        .answer-button:hover:not(:disabled) {
            border-color: #d32f2f;
            background-color: #f8f8f8;
        }

        .correct {
            background-color: #4caf50 !important; /* 绿色 */
            color: white;
            border-color: #4caf50 !important;
        }

        .incorrect {
            background-color: #f44336 !important; /* 红色 */
            color: white;
            border-color: #f44336 !important;
        }

        /* ⭐️ 星星特效样式和动画 */
        .star-container {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 3em;
            line-height: 1;
            z-index: 10;
            opacity: 0;
            pointer-events: none; /* 确保它不干扰点击事件 */
        }
        
        /* 星星动画定义 */
        @keyframes star-burst {
            0% {
                opacity: 0.8;
                transform: translate(-50%, -50%) scale(0.5);
            }
            50% {
                opacity: 1;
                transform: translate(-50%, -50%) scale(2);
                text-shadow: 0 0 10px yellow;
            }
            100% {
                opacity: 0;
                transform: translate(-50%, -50%) scale(3);
            }
        }

        .star-animate {
            animation: star-burst 0.5s ease-out forwards; /* 播放动画 */
        }

        #result-message {
            text-align: center;
            font-size: 1.2em;
            margin-top: 15px;
            font-weight: bold;
            min-height: 30px;
        }
        
        /* 下一题和重启按钮样式 */
        .control-button {
            display: block;
            width: 200px;
            margin: 20px auto 0;
            padding: 12px;
            background-color: #1976d2;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1.1em;
            transition: background-color 0.2s;
        }
        .control-button:hover {
            background-color: #1565c0;
        }
        
        .hidden {
            display: none;
        }

        /* 错题本样式 */
        #error-log-area {
            margin-top: 30px;
            padding: 20px;
            background-color: #fce4ec; 
            border-radius: 8px;
            border: 1px solid #d32f2f;
        }

        #error-log-area h3 {
            color: #d32f2f;
            text-align: center;
            margin-bottom: 15px;
            border-bottom: 2px dashed #f8bbd0;
            padding-bottom: 5px;
        }

        .error-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px dotted #ffcdd2;
            font-size: 1em;
        }

        .error-item span:first-child {
            font-weight: bold;
            color: #444;
            flex-grow: 1;
        }

        .error-item span:last-child {
            color: #d32f2f;
            font-weight: bold;
        }
    </style>
</head>
<body>

<div class="container">
    <h1>🇯🇵 耿浩的每日日语测验 (50题)</h1>

    <div class="score-board">
        分数: <span id="current-score">0</span> / 50 | 
        进度: <span id="current-question-count">0</span> / <span id="total-questions">50</span>
    </div>

    <div id="quiz-screen">
        <div id="question-area">
            <div id="question-display-wrapper">
                <div id="question-display">...</div>
                <button id="speak-button" onclick="speakCurrentQuestion()">🔊</button>
            </div>

            <div class="answer-grid" id="answer-buttons">
            </div>
            <div id="result-message"></div>
        </div>
        
        <button id="next-button" class="control-button hidden" onclick="nextQuestion()">下一题</button>
    </div>

    <div id="final-screen" class="hidden">
        <h2>🎉 测验完成！</h2>
        <p style="font-size: 1.5em; text-align: center;">您的最终得分是: <span id="final-score" style="color: #d32f2f; font-weight: bold;"></span> / 50</p >
        <button class="control-button" onclick="startQuiz()">重新开始</button>

        <div id="error-log-area" class="hidden">
            <h3>📝 错题回顾</h3>
            <div id="incorrect-list">
            </div>
        </div>
    </div>
</div>

<script>
        // 单词数据 (JavaScript Array/JSON)
// 格式: [ "日语单词 (可以包含假名)", "平假名/片假名/音译", "中文释义" ]
// 原有 350 个单词 + 新增 150 个单词 = 500 词汇量

const ALL_WORDS = [
    // --- 原有 350 个单词 ---
    ["食べる", "たべる", "吃"],
    ["飲む", "のむ", "喝"],
    ["話す", "はなす", "说话"],
    ["日本語", "にほんご", "日语"],
    ["私", "わたし", "我"],
    ["あなた", "あなた", "你"],
    ["はい", "はい", "是/是的"],
    ["いいえ", "いいえ", "不/不是"],
    ["ありがとう", "ありがとう", "谢谢"],
    ["おはよう", "おはよう", "早上好"],
    ["こんにちは", "こんにちは", "你好/下午好"],
    ["おやすみ", "おやすみ", "晚安"],
    ["ごめんなさい", "ごめんなさい", "对不起"],
    ["学校", "がっこう", "学校"],
    ["先生", "せんせい", "老师"],
    ["学生", "がくせい", "学生"],
    ["本", "ほん", "书"],
    ["犬", "いぬ", "狗"],
    ["猫", "ねこ", "猫"],
    ["車", "くるま", "车"],
    ["駅", "えき", "车站"],
    ["電気", "でんき", "电/灯"],
    ["水", "みず", "水"],
    ["お金", "おかね", "钱"],
    ["時間", "じかん", "时间"],
    ["今日", "きょう", "今天"],
    ["明日", "あした", "明天"],
    ["昨日", "きのう", "昨天"],
    ["見る", "みる", "看"],
    ["聞く", "きく", "听"],
    ["行く", "いく", "去"],
    ["来る", "くる", "来"],
    ["大きい", "おおきい", "大的"],
    ["小さい", "ちいさい", "小的"],
    ["新しい", "あたらしい", "新的"],
    ["古い", "ふるい", "旧的"],
    ["忙しい", "いそがしい", "忙碌的"],
    ["楽しい", "たのしい", "快乐的"],
    ["寒い", "さむい", "寒冷的"],
    ["暑い", "あつい", "炎热的"],
    ["好き", "すき", "喜欢"],
    ["嫌い", "きらい", "讨厌"],
    ["料理", "りょうり", "料理/烹饪"],
    ["映画", "えいが", "电影"],
    ["音楽", "おんがく", "音乐"],
    ["電話", "でんわ", "电话"],
    ["家族", "かぞく", "家人"],
    ["友達", "ともだち", "朋友"],
    ["会社", "かいしゃ", "公司"],
    ["仕事", "しごと", "工作"],
    ["買う", "かう", "买"],
    ["売る", "うる", "卖"],
    ["座る", "すわる", "坐"],
    ["立つ", "たつ", "站"],
    ["寝る", "ねる", "睡觉"],
    ["起きる", "おきる", "起床"],
    ["勉強する", "べんきょうする", "学习"],
    ["遊ぶ", "あそぶ", "玩耍"],
    ["走る", "はしる", "跑"],
    ["歩く", "あるく", "走/步行"],
    ["開ける", "あける", "打开"],
    ["閉める", "しめる", "关上"],
    ["始まる", "はじまる", "开始"],
    ["終わる", "おわる", "结束"],
    ["入れる", "いれる", "放进"],
    ["出す", "だす", "取出/拿出"],
    
    ["食べ物", "たべもの", "食物"],
    ["飲み物", "のみもの", "饮料"],
    ["朝ごはん", "あさごはん", "早餐"],
    ["昼ごはん", "ひるごはん", "午餐"],
    ["晩ごはん", "ばんごはん", "晚餐"],
    ["部屋", "へや", "房间"],
    ["家", "いえ", "家"],
    ["デパート", "デパート", "百货商店"],
    ["銀行", "ぎんこう", "银行"],
    ["郵便局", "ゆうびんきょく", "邮局"],
    ["病院", "びょういん", "医院"],
    ["空港", "くうこう", "机场"],
    ["町", "まち", "城镇"],
    ["国", "くに", "国家"],
    ["世界", "せかい", "世界"],
    ["上", "うえ", "上面"],
    ["下", "した", "下面"],
    ["前", "まえ", "前面"],
    ["後ろ", "うしろ", "后面"],
    ["中", "なか", "里面"],
    ["外", "そと", "外面"],
    ["右", "みぎ", "右边"],
    ["左", "ひだり", "左边"],
    ["隣", "となり", "旁边/隔壁"],
    ["間", "あいだ", "之间"],
    
    ["高い", "たかい", "高的/贵的"],
    ["安い", "やすい", "便宜的"],
    ["低い", "ひくい", "低的"],
    ["短い", "みじかい", "短的"],
    ["長い", "ながい", "长的"],
    ["早い", "はやい", "早的/快的"],
    ["遅い", "おそい", "迟的/慢的"],
    ["難しい", "むずかしい", "难的"],
    ["易しい", "やさしい", "简单的/温柔的"],
    ["良い", "いい/よい", "好的"],
    ["悪い", "わるい", "坏的"],
    ["多い", "おおい", "多的"],
    ["少ない", "すくない", "少的"],
    ["美しい", "うつくしい", "美丽的"],
    ["静か", "しずか", "安静的 (な形容词)"],
    ["賑やか", "にぎやか", "热闹的 (な形容词)"],
    ["便利", "べんり", "方便的 (な形容词)"],
    ["不便", "ふべん", "不方便的 (な形容词)"],
    ["元気", "げんき", "精神的/健康的 (な形容词)"],
    
    ["いつ", "いつ", "什么时候"],
    ["どこ", "どこ", "哪里"],
    ["だれ", "だれ", "谁"],
    ["どれ", "どれ", "哪个 (三者或以上)"],
    ["どう", "どう", "怎么样/如何"],
    ["どうして", "どうして", "为什么"],
    ["ここ", "ここ", "这里"],
    ["そこ", "そこ", "那里"],
    ["あそこ", "あそこ", "遥远那里"],
    
    ["一つ", "ひとつ", "一个"],
    ["二つ", "ふたつ", "两个"],
    ["三つ", "みっつ", "三个"],
    ["四つ", "よっつ", "四个"],
    ["五つ", "いつつ", "五个"],
    ["六つ", "むっつ", "六个"],
    ["七つ", "ななつ", "七个"],
    ["八つ", "やっつ", "八个"],
    ["九つ", "ここのつ", "九个"],
    ["十", "とお", "十个"],
    
    ["月曜日", "げつようび", "星期一"],
    ["火曜日", "かようび", "星期二"],
    ["水曜日", "すいようび", "星期三"],
    ["木曜日", "もくようび", "星期四"],
    ["金曜日", "きんようび", "星期五"],
    ["土曜日", "どようび", "星期六"],
    ["日曜日", "にちようび", "星期日"],
    
    ["お茶", "おちゃ", "茶"],
    ["コーヒー", "コーヒー", "咖啡"],
    ["ジュース", "ジュース", "果汁"],
    ["牛乳", "ぎゅうにゅう", "牛奶"],
    ["パン", "パン", "面包"],
    ["ご飯", "ごはん", "饭/米饭"],
    ["卵", "たまご", "鸡蛋"],
    ["肉", "にく", "肉"],
    ["魚", "さかな", "鱼"],
    ["野菜", "やさい", "蔬菜"],
    
    ["手", "て", "手"],
    ["足", "あし", "脚/腿"],
    ["頭", "あたま", "头"],
    ["顔", "かお", "脸"],
    ["目", "め", "眼睛"],
    ["耳", "みみ", "耳朵"],
    ["口", "くち", "嘴巴"],
    
    ["どうぞ", "どうぞ", "请/请便"],
    ["いらっしゃいませ", "いらっしゃいませ", "欢迎光临"],
    ["いただきます", "いただきます", "我开动了 (饭前)"],
    ["ごちそうさま", "ごちそうさま", "谢谢款待 (饭后)"],

    ["住む", "すむ", "居住"],
    ["乗る", "のる", "乘坐"],
    ["降りる", "おりる", "下车/下（飞机等）"],
    ["使う", "つかう", "使用"],
    ["出す", "だす", "寄出/取出"],
    ["入る", "はいる", "进入"],
    ["切る", "きる", "切/剪"],
    ["送る", "おくる", "送/寄送"],
    ["もらう", "もらう", "得到/接受"],
    ["あげる", "あげる", "给"],
    ["習う", "ならう", "学习（向人）"],
    ["消す", "けす", "关掉/消除"],
    ["つける", "つける", "打开（电灯/空调）"],
    ["手伝う", "てつだう", "帮忙"],
    ["結婚する", "けっこんする", "结婚"],
    ["別れる", "わかれる", "分手/分别"],
    ["散歩する", "さんぽする", "散步"],
    ["練習する", "れんしゅうする", "练习"],
    ["洗濯する", "せんたくする", "洗衣服"],
    ["掃除する", "そうじする", "打扫"],
    ["予約する", "よやくする", "预约"],
    ["旅行する", "りょこうする", "旅行"],
    
    ["誰か", "だれか", "某人/有人"],
    ["何か", "なにか", "某事/有东西"],
    ["どこか", "どこか", "某地/有地方"],
    ["いつか", "いつか", "某时/总有一天"],
    ["皆", "みんな", "大家/全部"],
    ["方", "かた", "人（敬语）/方向"],
    ["所", "ところ", "地方/场所"],
    ["物", "もの", "物品"],
    
    ["美味しい", "おいしい", "美味的"],
    ["不味い", "まずい", "难吃的"],
    ["甘い", "あまい", "甜的"],
    ["辛い", "からい", "辣的/咸的/痛苦的"],
    ["酸っぱい", "すっぱい", "酸的"],
    ["苦い", "にがい", "苦的"],
    ["優しい", "やさしい", "和蔼的/容易的"],
    ["親切", "しんせつ", "亲切的 (な形容词)"],
    ["暇", "ひま", "空闲的 (な形容词)"],
    ["丈夫", "じょうぶ", "结实的/健康的 (な形容词)"],
    ["大変", "たいへん", "不得了的/够呛的 (な形容词)"],
    ["結構", "けっこう", "相当/足够/很好 (な形容词)"],
    
    ["ゼロ", "ゼロ", "零"],
    ["一", "いち", "一"],
    ["二", "に", "二"],
    ["三", "さん", "三"],
    ["四", "よん/し", "四"],
    ["五", "ご", "五"],
    ["六", "ろく", "六"],
    ["七", "なな/しち", "七"],
    ["八", "はち", "八"],
    ["九", "きゅう/く", "九"],
    ["十", "じゅう", "十"],
    ["百", "ひゃく", "百"],
    ["千", "せん", "千"],
    ["万", "まん", "万"],
    
    ["分", "ふん/ぷん", "分钟"],
    ["時", "じ", "点钟"],
    ["午前", "ごぜん", "上午"],
    ["午後", "ごご", "下午"],
    ["朝", "あさ", "早上"],
    ["昼", "ひる", "白天/中午"],
    ["晩/夜", "ばん/よる", "晚上/夜里"],
    ["先週", "せんしゅう", "上周"],
    ["今週", "こんしゅう", "这周"],
    ["来週", "らいしゅう", "下周"],
    ["先月", "せんげつ", "上个月"],
    ["今月", "こんげつ", "这个月"],
    ["来月", "らいげつ", "下个月"],
    ["去年", "きょねん", "去年"],
    ["今年", "ことし", "今年"],
    ["来年", "らいねん", "明年"],
    
    ["色", "いろ", "颜色"],
    ["赤", "あか", "红色"],
    ["青", "あお", "蓝色/青色"],
    ["黒", "くろ", "黑色"],
    ["白", "しろ", "白色"],
    ["黄色", "きいろ", "黄色"],
    ["茶色", "ちゃいろ", "棕色/茶色"],
    ["緑", "みどり", "绿色"],
    
    ["風", "かぜ", "风/感冒"],
    ["雨", "あめ", "雨"],
    ["雪", "ゆき", "雪"],
    ["天気", "てんき", "天气"],
    ["曇り", "くもり", "阴天"],
    ["太陽", "たいよう", "太阳"],
    ["月", "つき", "月亮"],
    ["星", "ほし", "星星"],
    
    ["郵便", "ゆうびん", "邮政/邮件"],
    ["切手", "きって", "邮票"],
    ["葉書", "はがき", "明信片"],
    ["封筒", "ふうとう", "信封"],
    ["荷物", "にもつ", "行李/包裹"],
    ["お土産", "おみやげ", "伴手礼/土特产"],
    ["財布", "さいふ", "钱包"],
    ["靴", "くつ", "鞋子"],
    ["傘", "かさ", "伞"],
    ["時計", "とけい", "钟表"],
    ["鍵", "かぎ", "钥匙"],
    ["机", "つくえ", "桌子"],
    ["椅子", "いす", "椅子"],
    ["窓", "まど", "窗户"],
    ["扉", "とびら", "门"],
    ["壁", "かべ", "墙壁"],
    
    ["お父さん", "おとうさん", "爸爸"],
    ["お母さん", "おかあさん", "妈妈"],
    ["お兄さん", "おにいさん", "哥哥"],
    ["お姉さん", "おねえさん", "姐姐"],
    ["弟", "おとうと", "弟弟"],
    ["妹", "いもうと", "妹妹"],
    ["息子", "むすこ", "儿子"],
    ["娘", "むすめ", "女儿"],
    ["夫", "おっと", "丈夫"],
    ["妻", "つま", "妻子"],
    
    ["動物", "どうぶつ", "动物"],
    ["鳥", "とり", "鸟"],
    ["魚", "さかな", "鱼"],
    ["虫", "むし", "虫子"],
    ["花", "はな", "花"],
    ["木", "き", "树"],
    ["山", "やま", "山"],
    ["川", "かわ", "河/川"],
    ["海", "うみ", "海"],
    ["湖", "みずうみ", "湖"],
    
    ["写真", "しゃしん", "照片"],
    ["絵", "え", "画"],
    ["手紙", "てがみ", "信"],
    ["新聞", "しんぶん", "报纸"],
    ["雑誌", "ざっし", "杂志"],
    ["辞書", "じしょ", "字典"],
    ["鉛筆", "えんぴつ", "铅笔"],
    ["ボールペン", "ボールペン", "圆珠笔"],
    
    ["疲れる", "つかれる", "疲倦"],
    ["病気", "びょうき", "生病"],
    ["薬", "くすり", "药"],
    ["熱", "ねつ", "发烧"],
    ["怪我", "けが", "受伤"],
    ["大丈夫", "だいじょうぶ", "没关系/不要紧 (な形容词)"],
    
    ["一生懸命", "いっしょうけんめい", "拼命/努力地"],
    ["よく", "よく", "经常/好好地"],
    ["時々", "ときどき", "有时/时常"],
    ["いつも", "いつも", "总是/一直"],
    ["全然", "ぜんぜん", "完全不 (后接否定)"],
    ["きっと", "きっと", "一定/必定"],
    ["多分", "たぶん", "大概/或许"],
    ["ぜひ", "ぜひ", "务必/一定"],
    
    ["お邪魔します", "おじゃまします", "打扰了 (访问时)"],
    ["失礼します", "しつれいします", "告辞了/失礼了"],
    ["おかえりなさい", "おかえりなさい", "欢迎回来"],
    ["ただいま", "ただいま", "我回来了"],
    ["お先に失礼します", "おさきにしつれいします", "我先失陪了 (下班时)"],
    ["お疲れ様でした", "おつかれさまでした", "您辛苦了"],
    ["いってきます", "いってきます", "我出门了"],
    ["いってらっしゃい", "いってらっしゃい", "您慢走"],
    ["おめでとうございます", "おめでとうございます", "恭喜"],

    // --- 新增 150 个单词 ---
    ["払う", "はらう", "支付"],
    ["脱ぐ", "ぬぐ", "脱（衣服、鞋子）"],
    ["着る", "きる", "穿（衣服）"],
    ["かぶる", "かぶる", "戴（帽子）"],
    ["かける", "かける", "戴（眼镜）/花（时间、金钱）"],
    ["忘れる", "わすれる", "忘记"],
    ["覚える", "おぼえる", "记住"],
    ["教える", "おしえる", "教/告诉"],
    ["貸す", "かす", "借出"],
    ["借りる", "かりる", "借入"],
    ["泳ぐ", "およぐ", "游泳"],
    ["疲れる", "つかれる", "疲倦"],
    ["始める", "はじめる", "开始（他动词）"],
    ["続ける", "つづける", "继续"],
    ["辞める", "やめる", "辞职/停止"],
    ["引く", "ひく", "拉/查（字典）"],
    ["押す", "おす", "推/按"],
    ["渡す", "わたす", "递给/交给"],
    ["帰る", "かえる", "回家/回去"],
    ["急ぐ", "いそぐ", "急忙"],
    ["役に立つ", "やくにたつ", "有用"],
    
    ["場所", "ばしょ", "地方/场所"],
    ["公園", "こうえん", "公园"],
    ["美術館", "びじゅつかん", "美术馆"],
    ["図書館", "としょかん", "图书馆"],
    ["体育館", "たいいくかん", "体育馆"],
    ["神社", "じんじゃ", "神社"],
    ["お寺", "おてら", "寺庙"],
    ["祭り", "まつり", "祭典"],
    ["歴史", "れきし", "历史"],
    ["未来", "みらい", "未来"],
    
    ["先生", "せんせい", "老师/医生（对人的尊称）"],
    ["医者", "いしゃ", "医生"],
    ["看護師", "かんごし", "护士"],
    ["警察", "けいさつ", "警察"],
    ["運転手", "うんてんしゅ", "司机"],
    ["歌手", "かしゅ", "歌手"],
    ["俳優", "はいゆう", "演员"],
    ["社長", "しゃちょう", "社长/总经理"],
    ["部長", "ぶちょう", "部长"],
    ["課長", "かちょう", "科长"],
    ["受付", "うけつけ", "接待处"],
    
    ["形", "かたち", "形状"],
    ["色", "いろ", "颜色"],
    ["味", "あじ", "味道"],
    ["におい", "におい", "气味"],
    ["音", "おと", "声音"],
    ["声", "こえ", "人声"],
    ["様子", "ようす", "样子/情况"],
    ["理由", "りゆう", "理由"],
    ["目的", "もくてき", "目的"],
    ["方法", "ほうほう", "方法"],
    
    ["大変", "たいへん", "糟糕/不得了"],
    ["簡単", "かんたん", "简单的 (な形容词)"],
    ["複雑", "ふくざつ", "复杂的 (な形容词)"],
    ["丁寧", "ていねい", "礼貌的/细致的 (な形容词)"],
    ["必要", "ひつよう", "必要的 (な形容词)"],
    ["結構", "けっこう", "相当/很好"],
    ["だめ", "だめ", "不行/不好 (な形容词)"],
    ["嫌", "いや", "讨厌的/不愿意的 (な形容词)"],
    
    ["何回", "なんかい", "几次"],
    ["何冊", "なんさつ", "几本（册）"],
    ["何台", "なんだい", "几台（辆）"],
    ["何匹", "なんびき", "几只（小动物）"],
    ["何本", "なんぼん", "几根（细长物）"],
    ["何杯", "なんばい", "几杯（碗）"],
    ["何人", "なんにん", "几个人"],
    ["いくつ", "いくつ", "几个/几岁"],
    
    ["そして", "そして", "而且/然后（并列）"],
    ["それから", "それから", "然后/之后"],
    ["しかし", "しかし", "但是/然而（正式）"],
    ["でも", "でも", "但是/不过（口语）"],
    ["だから", "だから", "所以"],
    ["それで", "それで", "因此/于是"],
    ["それなのに", "それなのに", "尽管如此/却"],
    ["それとも", "それとも", "或者"],
    
    ["洋服", "ようふく", "西式服装"],
    ["和服", "わふく", "和服（日式服装）"],
    ["Tシャツ", "Tシャツ", "T恤"],
    ["ズボン", "ズボン", "裤子"],
    ["スカート", "スカート", "裙子"],
    ["上着", "うわぎ", "外套"],
    ["帽子", "ぼうし", "帽子"],
    ["めがね", "めがね", "眼镜"],
    ["指輪", "ゆびわ", "戒指"],
    ["ネックレス", "ネックレス", "项链"],
    
    ["音楽", "おんがく", "音乐"],
    ["歌", "うた", "歌"],
    ["絵", "え", "画/图画"],
    ["小説", "しょうせつ", "小说"],
    ["漫画", "まんが", "漫画"],
    ["手袋", "てぶくろ", "手套"],
    ["靴下", "くつした", "袜子"],
    ["ボタン", "ボタン", "按钮/纽扣"],
    ["レポート", "レポート", "报告"],
    ["データ", "データ", "数据"],
    
    ["会議", "かいぎ", "会议"],
    ["準備", "じゅんび", "准备"],
    ["発表", "はっぴょう", "发表/报告"],
    ["相談", "そうだん", "商量/咨询"],
    ["資料", "しりょう", "资料"],
    ["意見", "いけん", "意见"],
    ["質問", "しつもん", "提问/问题"],
    ["回答", "かいとう", "回答"],
    ["連絡", "れんらく", "联系"],
    ["報告", "ほうこく", "报告"],
    
    ["風邪", "かぜ", "感冒"],
    ["頭痛", "ずつう", "头痛"],
    ["腹痛", "ふくつう", "腹痛"],
    ["歯", "は", "牙齿"],
    ["喉", "のど", "嗓子"],
    ["体", "からだ", "身体"],
    ["健康", "けんこう", "健康 (な形容词)"],
    ["入院", "にゅういん", "住院"],
    ["退院", "たいいん", "出院"],
    ["手術", "しゅじゅつ", "手术"],
    
    ["趣味", "しゅみ", "爱好"],
    ["夢", "ゆめ", "梦想/梦"],
    ["生活", "せいかつ", "生活"],
    ["文化", "ぶんか", "文化"],
    ["習慣", "しゅうかん", "习惯"],
    ["景色", "けしき", "景色/风景"],
    ["経験", "けいけん", "经验"],
    ["技術", "ぎじゅつ", "技术"],
    ["未来", "みらい", "未来"],
    ["過去", "かこ", "过去"],
    
    ["最近", "さいきん", "最近"],
    ["今度", "こんど", "下次/这回"],
    ["まず", "まず", "首先"],
    ["次に", "つぎに", "其次/接着"],
    ["最後に", "さいごに", "最后"],
    ["もちろん", "もちろん", "当然"],
    ["なかなか", "なかなか", "很不/不容易"],
    ["たまに", "たまに", "偶尔"],
    
    ["お祝い", "おいわい", "祝贺/礼物"],
    ["プレゼント", "プレゼント", "礼物"],
    ["記念", "きねん", "纪念"],
    ["卒業", "そつぎょう", "毕业"],
    ["入学", "にゅうがく", "入学"],
    ["旅行", "りょこう", "旅行"],
    ["観光", "かんこう", "观光/旅游"],
    ["案内", "あんない", "向导/带路"],
    ["道", "みち", "道路"],
    ["信号", "しんごう", "信号灯"]
    ];

    const TOTAL_QUESTIONS_COUNT = 50; 
    let quizData = []; 
    let currentQuestionIndex = 0;
    let score = 0;
    let incorrectAnswers = []; 

    const questionDisplay = document.getElementById('question-display');
    const answerButtonsContainer = document.getElementById('answer-buttons');
    const scoreElement = document.getElementById('current-score');
    const countElement = document.getElementById('current-question-count');
    const resultMessage = document.getElementById('result-message');
    const quizScreen = document.getElementById('quiz-screen');
    const finalScreen = document.getElementById('final-screen');
    const finalScoreElement = document.getElementById('final-score');
    const nextButton = document.getElementById('next-button'); 
    const errorLogArea = document.getElementById('error-log-area'); 
    const incorrectList = document.getElementById('incorrect-list'); 
    
    // 语音合成相关变量
    const speakButton = document.getElementById('speak-button');
    let currentWordReading = ''; 

    // 随机打乱数组的函数 (Fisher-Yates)
    function shuffleArray(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
        return array;
    }

    // 语音朗读函数
    function speakJapanese() {
        if ('speechSynthesis' in window) {
            const textToSpeak = currentWordReading || '日本語'; 
            
            if (speechSynthesis.speaking) {
                speechSynthesis.cancel();
            }

            const utterance = new SpeechSynthesisUtterance(textToSpeak);
            utterance.lang = 'ja-JP'; 
            
            speechSynthesis.speak(utterance);
        } else {
            console.error('浏览器不支持Web语音合成API。');
        }
    }

    // 绑定到按钮上的点击事件
    function speakCurrentQuestion() {
        speakJapanese();
    }


    // 1. 初始化测验
    function startQuiz() {
        const sourceWords = ALL_WORDS.length >= TOTAL_QUESTIONS_COUNT ? 
                            shuffleArray([...ALL_WORDS]).slice(0, TOTAL_QUESTIONS_COUNT) :
                            shuffleArray([...ALL_WORDS]);
        
        quizData = [];
        incorrectAnswers = []; 
        
        // 生成测验数据
        sourceWords.forEach(word => {
            const [kanji, reading, meaning] = word;
            
            const allOtherWords = ALL_WORDS.filter(w => w[2] !== meaning);
            const wrongMeanings = shuffleArray(allOtherWords).slice(0, 3).map(w => w[2]);

            let options = shuffleArray([meaning, ...wrongMeanings]);

            while (options.length < 4) {
                 options.push("无法识别的释义"); 
                 options = shuffleArray(options);
            }

            quizData.push({
                questionText: `${kanji} (${reading})`,
                reading: reading, 
                correctAnswer: meaning,
                options: options.slice(0, 4),
                originalWord: kanji 
            });
        });

        currentQuestionIndex = 0;
        score = 0;
        
        // 界面初始化
        quizScreen.classList.remove('hidden');
        finalScreen.classList.add('hidden');
        errorLogArea.classList.add('hidden'); 
        nextButton.classList.add('hidden'); 
        document.getElementById('total-questions').textContent = quizData.length;

        loadQuestion();
    }

    // 2. 加载下一道题
    function loadQuestion() {
        if (currentQuestionIndex >= quizData.length) {
            endQuiz();
            return;
        }

        const currentQ = quizData[currentQuestionIndex];

        // 更新当前单词的朗读内容
        currentWordReading = currentQ.reading; 

        // 更新计分板
        scoreElement.textContent = score;
        countElement.textContent = currentQuestionIndex + 1; 
        resultMessage.textContent = '';
        nextButton.classList.add('hidden'); 

        // 显示问题
        questionDisplay.innerHTML = currentQ.questionText;

        // 生成答案按钮
        answerButtonsContainer.innerHTML = ''; 
        currentQ.options.forEach(option => {
            const button = document.createElement('button');
            button.classList.add('answer-button');
            button.textContent = option;
            
            // 添加星星特效容器
            const starSpan = document.createElement('span');
            starSpan.classList.add('star-container');
            starSpan.innerHTML = '⭐️';
            button.appendChild(starSpan);

            button.onclick = checkAnswer.bind(null, option, currentQ, starSpan); // 传递 starSpan 元素
            answerButtonsContainer.appendChild(button);
        });
    }

    // 3. 检查答案 (无自动跳转)
    function checkAnswer(selectedAnswer, currentQ, clickedStarSpan, event) {
        const clickedButton = event.target.closest('.answer-button'); // 确保我们拿到按钮元素
        const correctAnswer = currentQ.correctAnswer;
        
        // 禁用所有按钮
        Array.from(answerButtonsContainer.children).forEach(button => {
            button.disabled = true;
            if (button.textContent === correctAnswer) {
                button.classList.add('correct');
            }
        });
        
        let isCorrect = (selectedAnswer === correctAnswer);

        if (isCorrect) {
            score++;
            resultMessage.textContent = '✅ 正确！+1 分';
            clickedButton.classList.add('correct');
            
            // ⭐️ 触发星星特效
            clickedStarSpan.classList.add('star-animate');
            // 动画完成后移除动画类，以便下次点击时能再次触发
            setTimeout(() => {
                clickedStarSpan.classList.remove('star-animate');
            }, 500); // 动画时间为 0.5s
            
        } else {
            resultMessage.textContent = `❌ 错误。正确答案是: ${correctAnswer}`;
            clickedButton.classList.add('incorrect');
            
            // 记录错题
            incorrectAnswers.push({
                word: currentQ.questionText,
                correctMeaning: correctAnswer,
                userAnswer: selectedAnswer
            });
        }
        
        // 显示下一题按钮
        nextButton.classList.remove('hidden');
    }

    // 4. 手动跳转到下一题
    function nextQuestion() {
        currentQuestionIndex++;
        loadQuestion();
    }

    // 5. 结束测验并显示错题本
    function endQuiz() {
        if ('speechSynthesis' in window && speechSynthesis.speaking) {
            speechSynthesis.cancel();
        }

        quizScreen.classList.add('hidden');
        finalScreen.classList.remove('hidden');
        finalScoreElement.textContent = score;

        // 错题本生成
        if (incorrectAnswers.length > 0) {
            errorLogArea.classList.remove('hidden');
            incorrectList.innerHTML = ''; 
            
            incorrectAnswers.forEach(item => {
                const itemDiv = document.createElement('div');
                itemDiv.classList.add('error-item');
                itemDiv.innerHTML = `
                    <span>${item.word}</span> 
                    <span>: ${item.correctMeaning}</span>
                `;
                incorrectList.appendChild(itemDiv);
            });
        } else {
            errorLogArea.classList.add('hidden');
        }
    }


    // 页面加载完成后立即启动测验
    document.addEventListener('DOMContentLoaded', startQuiz);
</script>

</body>
</html>
