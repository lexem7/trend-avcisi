import streamlit as st
from duckduckgo_search import DDGS
import random
import time
import urllib.parse
import hashlib
from datetime import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="Çin Niş Ürün Bulucu",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SESSION STATE ---
if 'products' not in st.session_state:
    st.session_state.products = []
if 'used_queries' not in st.session_state:
    st.session_state.used_queries = set()
if 'search_count' not in st.session_state:
    st.session_state.search_count = 0

# --- TASARIM ---
st.markdown("""
<style>
    .stApp { background: #0d0d0d; }

    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 2px solid #0f3460;
        padding: 30px;
        border-radius: 20px;
        margin-bottom: 25px;
        text-align: center;
    }

    .platform-card {
        background: linear-gradient(145deg, #1a1a2e, #0f3460);
        border: 1px solid #e94560;
        border-radius: 16px;
        padding: 20px;
        margin: 10px 0;
        text-align: center;
    }

    .platform-link {
        display: block;
        padding: 15px 20px;
        margin: 8px 0;
        border-radius: 12px;
        text-decoration: none;
        font-weight: 700;
        font-size: 14px;
        transition: all 0.3s;
        text-align: left;
    }
    .platform-link:hover {
        transform: translateX(10px);
        filter: brightness(1.2);
    }

    .xhs { background: linear-gradient(90deg, #ff2442, #ff6b6b); color: white; }
    .douyin { background: linear-gradient(90deg, #00f2ea, #ff0050); color: white; }
    .taobao { background: linear-gradient(90deg, #ff5000, #ff8533); color: white; }
    .ali1688 { background: linear-gradient(90deg, #ff6600, #ffaa00); color: white; }
    .alibaba { background: linear-gradient(90deg, #e94560, #ff6b6b); color: white; }

    .keyword-tag {
        display: inline-block;
        background: #e94560;
        color: white;
        padding: 8px 15px;
        border-radius: 20px;
        margin: 5px;
        font-size: 13px;
        font-weight: 600;
    }

    .chinese-keyword {
        display: inline-block;
        background: #0f3460;
        border: 1px solid #e94560;
        color: #00d4ff;
        padding: 8px 15px;
        border-radius: 20px;
        margin: 5px;
        font-size: 14px;
        font-weight: 600;
    }

    .tip-card {
        background: rgba(233, 69, 96, 0.1);
        border: 1px solid #e94560;
        border-radius: 12px;
        padding: 20px;
        margin: 20px 0;
    }

    .product-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 20px;
    }

    .product-item {
        background: #1a1a2e;
        border: 1px solid #0f3460;
        border-radius: 12px;
        overflow: hidden;
    }
    .product-item img {
        width: 100%;
        height: 180px;
        object-fit: cover;
    }
    .product-item .info {
        padding: 15px;
    }

    .copy-btn {
        background: #e94560;
        color: white;
        border: none;
        padding: 8px 15px;
        border-radius: 8px;
        cursor: pointer;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# --- NİŞ ÜRÜN VERİTABANI ---
# Gerçekten FARKLI olan ürünler - lisanslı değil, mekanizması özel

NICHE_PRODUCTS = {
    "🎰 Masaüstü Gashapon/Otomat": {
        "search_terms": [
            # Çok spesifik İngilizce
            "mini gashapon machine desktop", "capsule vending machine toy kids",
            "candy dispenser machine home", "gumball machine toy small",
            "twist egg machine toy", "desktop slot machine toy",
            "coin operated toy machine mini", "prize vending machine small"
        ],
        "chinese_terms": [
            "迷你扭蛋机 桌面", "糖果机 儿童 家用", "扭蛋机 投币 小型",
            "自动售货机 玩具 迷你", "抓糖机 桌上", "扭蛋机 可爱"
        ],
        "1688_search": "迷你扭蛋机",
        "taobao_search": "桌面扭蛋机 儿童"
    },

    "🏗️ Reçine/Epoksi Diorama Küp": {
        "search_terms": [
            "resin diorama cube ocean", "epoxy resin whale lamp",
            "resin titanic diorama", "underwater scene resin cube",
            "deep sea resin art", "ocean world resin lamp",
            "resin jellyfish night light", "3d resin ocean cube"
        ],
        "chinese_terms": [
            "树脂立方体 海洋", "环氧树脂 鲸鱼灯", "水晶胶 摆件 海洋",
            "树脂 泰坦尼克", "深海 树脂 夜灯", "海洋 水晶球"
        ],
        "1688_search": "树脂摆件 海洋 创意",
        "taobao_search": "树脂立方体 海洋场景"
    },

    "🎪 Mini Pençeli Makine": {
        "search_terms": [
            "mini claw machine usb", "desktop crane game toy",
            "small claw grabber machine", "candy claw machine mini",
            "personal arcade claw game", "tabletop grabber machine"
        ],
        "chinese_terms": [
            "迷你抓娃娃机 USB", "桌面夹娃娃机", "小型抓糖机",
            "家用抓娃娃机", "儿童夹公仔机"
        ],
        "1688_search": "迷你抓娃娃机 桌面",
        "taobao_search": "迷你抓娃娃机 儿童"
    },

    "📱 Telefon Ekran Figürü": {
        "search_terms": [
            "phone screen figure hippers", "phone decoration figure cute",
            "phone holder figure kawaii", "screen attachment toy figure",
            "phone dust plug figure", "cable bite protector cute"
        ],
        "chinese_terms": [
            "手机屏幕 挂件 可爱", "手机支架 摆件 创意",
            "数据线保护套 卡通", "手机装饰 小人"
        ],
        "1688_search": "手机屏幕挂件 创意",
        "taobao_search": "手机装饰 可爱摆件"
    },

    "🧲 Manyetik Levitasyon": {
        "search_terms": [
            "magnetic levitation display", "floating globe lamp",
            "magnetic floating plant pot", "levitating moon lamp",
            "anti gravity display stand", "magnetic floating speaker"
        ],
        "chinese_terms": [
            "磁悬浮 摆件", "悬浮地球仪", "磁悬浮 月球灯",
            "磁悬浮 花盆", "反重力 展示架"
        ],
        "1688_search": "磁悬浮摆件 创意",
        "taobao_search": "磁悬浮 装饰品"
    },

    "🌊 Sıvı Hareket Oyuncak": {
        "search_terms": [
            "liquid motion timer", "oil hourglass toy",
            "liquid bubble toy desk", "water snake fidget",
            "floating color mix toy", "sensory liquid toy"
        ],
        "chinese_terms": [
            "液体沙漏 创意", "油滴 计时器", "解压 液体玩具",
            "水蛇 减压", "流沙 摆件"
        ],
        "1688_search": "液体沙漏 解压玩具",
        "taobao_search": "液体计时器 创意"
    },

    "🎡 Mekanik Çark/Rulet": {
        "search_terms": [
            "spinning wheel game toy", "roulette wheel toy kids",
            "fortune wheel toy small", "prize wheel spinner toy",
            "lucky draw wheel mini", "spinning decision maker"
        ],
        "chinese_terms": [
            "转盘 玩具 抽奖", "轮盘 游戏 儿童", "幸运转盘 小型",
            "旋转 抽奖机", "大转盘 桌面"
        ],
        "1688_search": "抽奖转盘 玩具",
        "taobao_search": "幸运转盘 儿童"
    },

    "💡 LED Sürpriz Kutu": {
        "search_terms": [
            "led light gift box", "glow surprise box",
            "light up mystery box", "neon gift box toy",
            "illuminated blind box", "LED unboxing toy"
        ],
        "chinese_terms": [
            "发光 礼盒 创意", "LED 惊喜盒", "夜光 盲盒",
            "发光 玩具盒", "灯光 礼物盒"
        ],
        "1688_search": "发光礼盒 创意",
        "taobao_search": "LED惊喜盒 发光"
    },

    "🎭 Yüz Değiştiren Figür": {
        "search_terms": [
            "face changing doll toy", "reversible mood plush",
            "flip expression toy", "emotion changing figure",
            "two face plush toy", "mood flip octopus"
        ],
        "chinese_terms": [
            "变脸 玩具", "翻转 表情 玩偶", "双面 毛绒",
            "心情 变化 玩具", "表情包 玩偶"
        ],
        "1688_search": "翻转玩偶 表情",
        "taobao_search": "变脸玩具 创意"
    },

    "📦 Sürpriz Mekanizma Kutu": {
        "search_terms": [
            "pop up surprise box mechanism", "spring loaded gift box",
            "explosion gift box diy", "mechanical surprise box",
            "auto open gift box", "puzzle surprise box"
        ],
        "chinese_terms": [
            "弹出 礼盒 机关", "爆炸 礼盒", "惊喜盒子 创意",
            "机关 礼物盒", "自动 弹出 盒子"
        ],
        "1688_search": "创意礼盒 机关",
        "taobao_search": "惊喜盒子 弹出"
    },

    "🎲 Otomatik Kart/Zar": {
        "search_terms": [
            "automatic card dealer toy", "dice roller tower",
            "card shuffler dispenser", "random card picker machine",
            "dice rolling machine toy", "card ejector toy"
        ],
        "chinese_terms": [
            "自动发牌机", "骰子塔 桌游", "洗牌机 玩具",
            "抽卡机 儿童", "随机 骰子机"
        ],
        "1688_search": "自动发牌机 玩具",
        "taobao_search": "骰子塔 桌游配件"
    },

    "🎯 Mini Arcade Oyun": {
        "search_terms": [
            "mini arcade game machine", "retro game console small",
            "desktop arcade toy", "mini pinball machine toy",
            "small basketball game toy", "finger sports mini game"
        ],
        "chinese_terms": [
            "迷你游戏机 桌面", "复古街机 小型", "弹珠机 玩具",
            "投篮机 迷你", "桌面 游戏机"
        ],
        "1688_search": "迷你游戏机 桌面",
        "taobao_search": "迷你街机 复古"
    }
}


def generate_unique_query(category):
    """Her seferinde FARKLI sorgu üret"""
    data = NICHE_PRODUCTS[category]

    # Daha önce kullanılmamış bir sorgu bul
    available_en = [q for q in data["search_terms"] if q not in st.session_state.used_queries]
    available_cn = [q for q in data["chinese_terms"] if q not in st.session_state.used_queries]

    if not available_en:
        st.session_state.used_queries.clear()
        available_en = data["search_terms"]
        available_cn = data["chinese_terms"]

    en_query = random.choice(available_en)
    cn_query = random.choice(available_cn) if available_cn else data["chinese_terms"][0]

    st.session_state.used_queries.add(en_query)

    # Çeşitlilik için ek terimler
    variations = ["2024", "new", "creative", "unique", "trending", "popular", "best"]
    en_query_varied = f"{en_query} {random.choice(variations)}"

    return en_query_varied, cn_query, data["1688_search"], data["taobao_search"]


def search_with_variety(query, max_results=6):
    """Çeşitli sonuçlar getir"""
    results = []

    try:
        with DDGS() as ddgs:
            # Zaman bazlı farklılık için
            time_hash = hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:8]
            varied_query = f"{query} {time_hash[:3]}"

            images = list(ddgs.images(query, max_results=max_results * 2))

            # Rastgele seç (her seferinde farklı sonuçlar)
            if len(images) > max_results:
                images = random.sample(images, max_results)

            for img in images:
                results.append({
                    "title": img.get("title", ""),
                    "image": img.get("image", ""),
                    "url": img.get("url", ""),
                    "source": img.get("source", "")
                })
    except Exception as e:
        pass

    return results


def create_platform_links(cn_query, en_query, search_1688, search_taobao):
    """Platform linkleri oluştur"""
    cn_encoded = urllib.parse.quote(cn_query)
    en_encoded = urllib.parse.quote(en_query)
    s1688_encoded = urllib.parse.quote(search_1688)
    staobao_encoded = urllib.parse.quote(search_taobao)

    return {
        "xiaohongshu": f"https://www.xiaohongshu.com/search_result?keyword={cn_encoded}",
        "douyin": f"https://www.douyin.com/search/{cn_encoded}",
        "taobao": f"https://s.taobao.com/search?q={staobao_encoded}",
        "1688": f"https://s.1688.com/selloffer/offer_search.htm?keywords={s1688_encoded}",
        "alibaba": f"https://www.alibaba.com/trade/search?SearchText={en_encoded}",
        "google": f"https://www.google.com/search?q={en_encoded}&tbm=isch"
    }


# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## 🔮 Kategori Seç")

    selected_category = st.selectbox(
        "Ürün Tipi",
        options=list(NICHE_PRODUCTS.keys()),
        index=0
    )

    st.markdown("---")

    st.markdown("### ⚠️ ÖNEMLİ")
    st.markdown("""
    **DuckDuckGo sınırlıdır!**

    Gerçek niş ürünleri bulmak için
    aşağıdaki **Çin platformu linklerini**
    kullan. Orada direkt Çince ile ara!
    """)

    st.markdown("---")

    if st.button("🗑️ Aramayı Sıfırla", use_container_width=True):
        st.session_state.products = []
        st.session_state.used_queries.clear()
        st.session_state.search_count = 0


# --- ANA SAYFA ---
st.markdown("""
<div class="main-header">
    <h1 style="color:#e94560; margin:0;">🔮 ÇİN NİŞ ÜRÜN BULUCU</h1>
    <p style="color:#ccc; margin-top:10px;">
        Sıradan değil, GERÇEKTEN FARKLI ürünleri bul!
    </p>
</div>
""", unsafe_allow_html=True)

# --- SEÇİLİ KATEGORİ BİLGİSİ ---
st.markdown(f"## {selected_category}")

cat_data = NICHE_PRODUCTS[selected_category]

# Anahtar kelimeler göster
st.markdown("### 🔑 Bu Kategoride Aranacak Kelimeler:")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**İngilizce:**")
    for term in cat_data["search_terms"][:4]:
        st.markdown(f'<span class="keyword-tag">{term}</span>', unsafe_allow_html=True)

with col2:
    st.markdown("**Çince (Kopyala ve Yapıştır):**")
    for term in cat_data["chinese_terms"][:4]:
        st.markdown(f'<span class="chinese-keyword">{term}</span>', unsafe_allow_html=True)

st.markdown("---")

# --- PLATFORM LİNKLERİ (EN ÖNEMLİ KISIM) ---
st.markdown("### 🌏 DİREKT ÇİN PLATFORMLARINDA ARA")
st.markdown("*Bu linkler seni doğrudan Çince arama sonuçlarına götürür:*")

en_q, cn_q, s1688, staobao = generate_unique_query(selected_category)
links = create_platform_links(cn_q, en_q, s1688, staobao)

col1, col2 = st.columns(2)

with col1:
    st.markdown(f'''
    <a href="{links['1688']}" target="_blank" class="platform-link ali1688">
        🏭 1688.com - TOPTAN FİYAT<br>
        <small>Arama: {s1688}</small>
    </a>
    ''', unsafe_allow_html=True)

    st.markdown(f'''
    <a href="{links['taobao']}" target="_blank" class="platform-link taobao">
        🛒 Taobao - PERAKENDE<br>
        <small>Arama: {staobao}</small>
    </a>
    ''', unsafe_allow_html=True)

    st.markdown(f'''
    <a href="{links['alibaba']}" target="_blank" class="platform-link alibaba">
        🌐 Alibaba - TOPTAN (EN)<br>
        <small>Arama: {en_q[:30]}...</small>
    </a>
    ''', unsafe_allow_html=True)

with col2:
    st.markdown(f'''
    <a href="{links['xiaohongshu']}" target="_blank" class="platform-link xhs">
        📕 Xiaohongshu - TREND<br>
        <small>Arama: {cn_q}</small>
    </a>
    ''', unsafe_allow_html=True)

    st.markdown(f'''
    <a href="{links['douyin']}" target="_blank" class="platform-link douyin">
        🎵 Douyin - VİRAL VİDEO<br>
        <small>Arama: {cn_q}</small>
    </a>
    ''', unsafe_allow_html=True)

    st.markdown(f'''
    <a href="{links['google']}" target="_blank" class="platform-link" style="background:#4285f4; color:white;">
        🔍 Google Images<br>
        <small>Arama: {en_q[:30]}...</small>
    </a>
    ''', unsafe_allow_html=True)

# Kopyalanabilir Çince arama terimi
st.markdown("---")
st.markdown("### 📋 Kopyala & Yapıştır için Çince Terimler:")

copy_terms = " | ".join(cat_data["chinese_terms"][:3])
st.code(copy_terms, language=None)

st.markdown(f"**1688 için:** `{s1688}`")
st.markdown(f"**Taobao için:** `{staobao}`")

# --- GÖRSEL ARAMA (BONUS) ---
st.markdown("---")
st.markdown("### 🖼️ Örnek Görseller (DuckDuckGo)")
st.markdown("*Not: Gerçek niş ürünler için yukarıdaki Çin platformu linklerini kullan!*")

if st.button("🔍 Örnek Görseller Getir", type="primary", use_container_width=True):
    with st.spinner("Aranıyor..."):
        st.session_state.search_count += 1

        # Her tıklamada farklı sorgu
        query_index = st.session_state.search_count % len(cat_data["search_terms"])
        search_query = cat_data["search_terms"][query_index]

        results = search_with_variety(search_query, max_results=6)

        if results:
            cols = st.columns(3)
            for i, result in enumerate(results):
                with cols[i % 3]:
                    if result.get("image"):
                        st.image(result["image"], use_container_width=True)
                        st.caption(result.get("title", "")[:50])
        else:
            st.warning("Görsel bulunamadı. Yukarıdaki platform linklerini dene!")

# --- İPUÇLARI ---
st.markdown("---")
st.markdown("""
<div class="tip-card">
    <h4 style="color:#e94560; margin-top:0;">💡 NİŞ ÜRÜN BULMA İPUÇLARI</h4>
    <ol style="color:#ccc;">
        <li><strong>1688.com</strong> - Çin'in en büyük toptan platformu. Fabrika fiyatları!</li>
        <li><strong>Xiaohongshu</strong> - Çinli influencer'ların paylaştığı trend ürünler</li>
        <li><strong>Douyin</strong> - Viral olan ürünleri bul (TikTok'un Çin versiyonu)</li>
        <li>Çince terimleri kopyala ve direkt platformlarda ara</li>
        <li>Ürün görselini Google Lens ile tersine ara</li>
    </ol>
</div>
""", unsafe_allow_html=True)

# --- TÜM ÇİNCE TERİMLER ---
st.markdown("---")
st.markdown("### 📚 Tüm Kategoriler için Çince Arama Terimleri")

with st.expander("Tüm Çince Terimleri Göster"):
    for cat_name, cat_data in NICHE_PRODUCTS.items():
        st.markdown(f"**{cat_name}**")
        st.code(" | ".join(cat_data["chinese_terms"]), language=None)
        st.markdown(f"1688: `{cat_data['1688_search']}` | Taobao: `{cat_data['taobao_search']}`")
        st.markdown("---")

# --- FOOTER ---
st.markdown("""
<div style="text-align:center; color:#555; padding:30px;">
    <p>🔮 Çin Niş Ürün Bulucu v5.0</p>
    <p style="font-size:12px;">Platform linkleri ile doğrudan Çin sitelerinde ara!</p>
</div>
""", unsafe_allow_html=True)
