import streamlit as st
from duckduckgo_search import DDGS
import random
import time
import urllib.parse
import json
import os
from datetime import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="Fark Yaratan Ürün Avcısı",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SESSION STATE BAŞLAT ---
if 'products' not in st.session_state:
    st.session_state.products = []
if 'search_offset' not in st.session_state:
    st.session_state.search_offset = 0
if 'current_query' not in st.session_state:
    st.session_state.current_query = ""

# --- FALLBACK GÖRSELLERİ ---
FALLBACK_IMAGES = [
    "https://images.unsplash.com/photo-1558060370-d644479cb6f7?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1566576912321-d58ddd7a6088?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1596461404969-9ae70f2830c1?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1608889825103-eb5ed706fc64?w=400&h=300&fit=crop",
    "https://images.unsplash.com/photo-1581235720704-06d3acfcb36f?w=400&h=300&fit=crop",
]

# --- TASARIM ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    .stApp {
        background: linear-gradient(180deg, #0a0a0f 0%, #1a1a2e 100%);
        font-family: 'Inter', sans-serif;
    }

    .header-pro {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 50%, #4facfe 100%);
        padding: 40px;
        border-radius: 24px;
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 20px 60px rgba(240, 147, 251, 0.3);
    }

    .product-card-pro {
        background: linear-gradient(145deg, #1e1e2e 0%, #2a2a4a 100%);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 20px;
        padding: 0;
        margin-bottom: 25px;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
    }
    .product-card-pro:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 25px 80px rgba(240, 147, 251, 0.4);
        border-color: rgba(240, 147, 251, 0.5);
    }
    .product-card-pro img {
        width: 100%;
        height: 240px;
        object-fit: cover;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    .card-content {
        padding: 20px;
    }
    .card-title {
        font-size: 13px;
        font-weight: 600;
        color: #fff;
        margin-bottom: 12px;
        height: 38px;
        overflow: hidden;
        line-height: 1.4;
    }

    .platform-buttons {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-top: 12px;
    }
    .platform-btn {
        display: inline-flex;
        align-items: center;
        padding: 6px 10px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 600;
        font-size: 10px;
        transition: all 0.3s;
    }
    .platform-btn:hover {
        transform: scale(1.05);
        filter: brightness(1.2);
    }

    .xiaohongshu-btn { background: linear-gradient(135deg, #ff2442, #ff6b6b); color: white; }
    .douyin-btn { background: linear-gradient(135deg, #00f2ea, #ff0050); color: white; }
    .taobao-btn { background: linear-gradient(135deg, #ff5000, #ff8533); color: white; }
    .btn-1688 { background: linear-gradient(135deg, #ff6600, #ffaa00); color: white; }
    .alibaba-btn { background: linear-gradient(135deg, #ff6a00, #ee0a24); color: white; }
    .google-btn { background: linear-gradient(135deg, #4285f4, #34a853); color: white; }

    .category-badge {
        background: linear-gradient(90deg, #667eea, #764ba2);
        color: white;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 10px;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 10px;
    }

    .unique-badge {
        background: linear-gradient(90deg, #f5576c, #f093fb);
        color: white;
        padding: 3px 8px;
        border-radius: 10px;
        font-size: 9px;
        font-weight: 700;
    }

    .stats-card {
        background: linear-gradient(145deg, #1e1e2e, #2a2a4a);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 25px;
        text-align: center;
    }
    .stats-number {
        font-size: 2.2em;
        font-weight: 700;
        background: linear-gradient(135deg, #f093fb, #f5576c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .stats-label {
        color: #888;
        font-size: 13px;
        margin-top: 5px;
    }

    .search-info {
        background: rgba(240, 147, 251, 0.1);
        border: 1px solid rgba(240, 147, 251, 0.3);
        border-radius: 12px;
        padding: 15px 20px;
        margin: 20px 0;
    }

    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        margin: 30px 0;
    }

    .tip-box {
        background: rgba(79, 172, 254, 0.1);
        border: 1px solid rgba(79, 172, 254, 0.3);
        border-radius: 12px;
        padding: 15px;
        margin: 15px 0;
        font-size: 12px;
        color: #4facfe;
    }
</style>
""", unsafe_allow_html=True)

# --- FARK YARATAN ÜRÜN KATEGORİLERİ ---
# Sıradan değil, SUNUMU/MEKANİZMASI farklı olan ürünler

UNIQUE_CATEGORIES = {
    "🎰 Mini Gashapon Makinesi": {
        "description": "Masaüstü kapsül makineleri, çevirmeli oyuncak dağıtıcılar",
        "keywords_en": [
            "mini gashapon machine toy", "desktop capsule machine", "candy vending machine toy",
            "mini vending machine dispenser", "gachapon machine home", "capsule toy dispenser",
            "twist candy machine", "egg vending machine toy", "mini slot machine toy",
            "tabletop gashapon", "home capsule vending", "kids vending machine toy"
        ],
        "keywords_cn": [
            "迷你扭蛋机", "桌面扭蛋机", "糖果机玩具", "家用扭蛋机",
            "儿童投币机", "迷你售货机", "扭蛋机摆件", "自动售货机玩具",
            "桌上扭蛋机", "小型扭蛋机", "抓糖机", "迷你抓娃娃机"
        ]
    },

    "🎁 Mekanik Açılış Kutusu": {
        "description": "Düğmeye bas açılan, otomatik çıkan sürpriz kutular",
        "keywords_en": [
            "mechanical surprise box", "pop up gift box", "auto opening box",
            "spring loaded surprise", "mechanical unboxing", "push button surprise box",
            "self opening gift box", "mechanical reveal box", "ejecting surprise toy",
            "automatic pop out box", "button activated surprise"
        ],
        "keywords_cn": [
            "机械惊喜盒", "弹出礼盒", "自动开盒", "弹簧惊喜盒",
            "按键惊喜盒", "机关盒子", "自动弹出盒", "创意开盒",
            "惊喜弹射盒", "机械礼物盒"
        ]
    },

    "🎡 Çevirmeli/Dönen Oyuncak": {
        "description": "Çark çevir, rulet, dönen mekanizmalı oyuncaklar",
        "keywords_en": [
            "spinning wheel toy", "roulette toy", "wheel of fortune toy",
            "spin to win toy", "rotating surprise toy", "turntable toy game",
            "lucky wheel toy", "spinning game toy", "dial turn toy",
            "rotation mechanism toy", "spinning lottery toy"
        ],
        "keywords_cn": [
            "转盘玩具", "轮盘玩具", "幸运转盘", "旋转惊喜",
            "抽奖转盘", "旋转玩具", "大转盘玩具", "转转乐",
            "幸运轮盘", "旋转抽奖机"
        ]
    },

    "🎪 Pençeli Otomat / Mini Vinç": {
        "description": "Masaüstü mini vinç makineleri, pençeli oyuncak",
        "keywords_en": [
            "mini claw machine", "desktop crane game", "candy grabber machine",
            "mini arcade claw", "toy grabber machine", "small claw game",
            "usb claw machine", "tabletop crane toy", "mini grabber arcade",
            "home claw machine", "personal crane game"
        ],
        "keywords_cn": [
            "迷你抓娃娃机", "桌面夹娃娃机", "小型抓糖机", "家用抓娃娃",
            "USB夹娃娃机", "迷你夹公仔机", "儿童抓娃娃机", "桌上抓娃娃",
            "迷你娃娃机", "夹糖果机"
        ]
    },

    "🎲 Sürpriz Zar/Kart Dağıtıcı": {
        "description": "Otomatik kart çıkaran, zar atan mekanizmalar",
        "keywords_en": [
            "card dispenser toy", "automatic dice roller", "card ejector machine",
            "random card picker", "dice tower toy", "card shuffler dispenser",
            "mystery card machine", "trading card dispenser", "dice rolling machine",
            "card vending toy", "automatic card dealer toy"
        ],
        "keywords_cn": [
            "卡片分发器", "自动骰子机", "卡牌机", "抽卡机",
            "骰子塔", "卡片抽取器", "盲卡机", "集换卡分发器",
            "自动发牌机", "桌游配件"
        ]
    },

    "💡 Işıklı/LED Sürpriz": {
        "description": "Işık efektli, LED'li açılış deneyimi",
        "keywords_en": [
            "LED surprise box", "light up mystery box", "glowing blind box",
            "LED unboxing toy", "light effect surprise", "illuminated gift box",
            "neon surprise toy", "glow in dark blind box", "LED reveal toy",
            "light show surprise", "luminous mystery toy"
        ],
        "keywords_cn": [
            "发光盲盒", "LED惊喜盒", "灯光盲盒", "夜光盲盒",
            "发光礼盒", "LED揭示盒", "荧光盲盒", "闪光惊喜",
            "发光玩具盒", "灯效盲盒"
        ]
    },

    "🎵 Sesli/Müzikli Sürpriz": {
        "description": "Müzik çalan, ses efektli açılış kutuları",
        "keywords_en": [
            "musical surprise box", "sound effect toy box", "singing gift box",
            "melody surprise toy", "audio blind box", "music box surprise",
            "sound activated toy", "talking surprise box", "musical unboxing",
            "sound chip gift box"
        ],
        "keywords_cn": [
            "音乐盲盒", "发声惊喜盒", "音乐礼盒", "有声玩具盒",
            "音效盲盒", "唱歌礼盒", "发声玩具", "音乐机关盒",
            "语音盲盒", "声控惊喜"
        ]
    },

    "🌊 Sıvı/Akan Diorama": {
        "description": "İçinde sıvı akan, kar küresi tarzı ürünler",
        "keywords_en": [
            "liquid timer toy", "flowing sand art", "oil hourglass toy",
            "bubble motion toy", "liquid motion toy", "water snake toy",
            "dripping oil toy", "liquid filled desk toy", "mesmerizing liquid toy",
            "calming sensory bottle", "floating glitter toy"
        ],
        "keywords_cn": [
            "液体沙漏", "流沙摆件", "油滴玩具", "液体计时器",
            "水流玩具", "解压液体", "流动摆件", "油水分离玩具",
            "漂浮玩具", "减压水蛇"
        ]
    },

    "🧲 Manyetik Sürpriz": {
        "description": "Mıknatıs ile hareket eden, manyetik mekanizmalı",
        "keywords_en": [
            "magnetic levitation toy", "floating display", "magnetic sculpture",
            "magnetic desk toy", "levitating figure", "magnetic kinetic toy",
            "ferrofluid display", "magnetic fidget toy", "hovering toy display",
            "magnetic surprise toy", "anti gravity display"
        ],
        "keywords_cn": [
            "磁悬浮玩具", "磁力摆件", "悬浮展示", "磁性玩具",
            "磁力雕塑", "磁流体", "悬浮手办", "磁力减压",
            "反重力摆件", "磁吸玩具"
        ]
    },

    "🎭 Değişen/Dönüşen Figür": {
        "description": "Yüzü değişen, formu dönüşen figürler",
        "keywords_en": [
            "face changing figure", "morphing toy", "expression changing toy",
            "transforming display", "mood changing figure", "reversible plush",
            "flip face toy", "emotion changing toy", "shapeshifting figure",
            "two face figure", "rotating face display"
        ],
        "keywords_cn": [
            "变脸玩具", "表情变化", "翻转玩偶", "变形手办",
            "心情变化玩具", "双面玩偶", "可变表情", "变身玩具",
            "旋转换脸", "情绪玩具"
        ]
    },

    "📦 Çok Katmanlı Kutu": {
        "description": "Açtıkça açılan, iç içe sürpriz kutular",
        "keywords_en": [
            "nested surprise box", "multi layer gift box", "box in box surprise",
            "unfolding gift box", "layered mystery box", "expanding surprise box",
            "matryoshka style gift", "progressive unboxing", "endless box toy",
            "stacking surprise box"
        ],
        "keywords_cn": [
            "多层惊喜盒", "套娃礼盒", "层层惊喜", "展开礼盒",
            "嵌套盲盒", "递进惊喜", "俄罗斯套娃礼盒", "无限盒子",
            "叠叠乐礼盒", "多重惊喜盒"
        ]
    },

    "🎯 Hedef/Atış Oyuncak": {
        "description": "Vur-kazan tarzı, hedef odaklı sürpriz",
        "keywords_en": [
            "target shooting toy", "prize shooting game", "knock down toy",
            "aim and win toy", "shooting gallery toy", "carnival target game",
            "ball shooting prize", "dart prize game", "mini shooting arcade",
            "hit target surprise"
        ],
        "keywords_cn": [
            "射击玩具", "打靶玩具", "投球玩具", "瞄准游戏",
            "击倒玩具", "嘉年华射击", "飞镖奖品", "迷你射击机",
            "命中惊喜", "弹射玩具"
        ]
    }
}

# Trend/Viral Terimleri
VIRAL_TERMS_EN = ["viral", "trending", "hot sale", "best seller", "new 2024", "unique", "creative", "novelty"]
VIRAL_TERMS_CN = ["爆款", "网红", "热卖", "新款", "创意", "独特", "新奇"]


# --- ÇİN PLATFORMLARI LİNKLERİ ---
def generate_platform_links(query_en, query_cn):
    cn_encoded = urllib.parse.quote(query_cn)
    en_encoded = urllib.parse.quote(query_en)

    return {
        "xiaohongshu": {
            "name": "小红书",
            "icon": "📕",
            "url": f"https://www.xiaohongshu.com/search_result?keyword={cn_encoded}",
            "class": "xiaohongshu-btn"
        },
        "douyin": {
            "name": "抖音",
            "icon": "🎵",
            "url": f"https://www.douyin.com/search/{cn_encoded}",
            "class": "douyin-btn"
        },
        "taobao": {
            "name": "淘宝",
            "icon": "🛒",
            "url": f"https://s.taobao.com/search?q={cn_encoded}",
            "class": "taobao-btn"
        },
        "1688": {
            "name": "1688",
            "icon": "🏭",
            "url": f"https://s.1688.com/selloffer/offer_search.htm?keywords={cn_encoded}",
            "class": "btn-1688"
        },
        "alibaba": {
            "name": "Alibaba",
            "icon": "🌐",
            "url": f"https://www.alibaba.com/trade/search?SearchText={en_encoded}",
            "class": "alibaba-btn"
        },
        "google": {
            "name": "Google",
            "icon": "🔍",
            "url": f"https://www.google.com/search?q={en_encoded}&tbm=isch",
            "class": "google-btn"
        }
    }


# --- ARAMA FONKSİYONLARI ---
def create_search_query(category, add_viral=True):
    cat_data = UNIQUE_CATEGORIES[category]

    en_query = random.choice(cat_data["keywords_en"])
    cn_query = random.choice(cat_data["keywords_cn"])

    if add_viral and random.random() > 0.4:
        en_query += " " + random.choice(VIRAL_TERMS_EN)
        cn_query += " " + random.choice(VIRAL_TERMS_CN)

    return en_query, cn_query


def search_images_safe(query, max_results=8):
    results = []

    try:
        with DDGS() as ddgs:
            images = list(ddgs.images(query, max_results=max_results))

            for img in images:
                image_url = img.get("image", "")

                if not image_url or len(image_url) < 10:
                    image_url = random.choice(FALLBACK_IMAGES)
                    is_fallback = True
                else:
                    is_fallback = False

                results.append({
                    "title": img.get("title", "Ürün"),
                    "image_url": image_url,
                    "source_url": img.get("url", "#"),
                    "source": img.get("source", "Web"),
                    "is_fallback": is_fallback
                })

    except Exception as e:
        st.warning(f"⚠️ Arama hatası, alternatif görseller kullanılıyor...")
        for i in range(3):
            results.append({
                "title": f"Keşfedilecek Ürün",
                "image_url": random.choice(FALLBACK_IMAGES),
                "source_url": "#",
                "source": "Öneri",
                "is_fallback": True
            })

    return results


def fetch_products(category, add_viral=True, count=6):
    en_query, cn_query = create_search_query(category, add_viral)

    # Çeşitlilik için rastgele ek kelime
    extras = ["mini", "desktop", "home", "kids", "cute", "new", "toy"]
    modified_query = f"{en_query} {random.choice(extras)}"

    products = search_images_safe(modified_query, max_results=count)

    for product in products:
        product['category'] = category
        product['query_en'] = en_query
        product['query_cn'] = cn_query
        product['links'] = generate_platform_links(en_query, cn_query)
        product['description'] = UNIQUE_CATEGORIES[category]['description']

    return products


# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## 💎 Ürün Filtresi")

    selected_category = st.selectbox(
        "🎯 Kategori Seç",
        options=list(UNIQUE_CATEGORIES.keys()),
        index=0
    )

    # Kategori açıklaması
    st.markdown(f"""
    <div class="tip-box">
        💡 {UNIQUE_CATEGORIES[selected_category]['description']}
    </div>
    """, unsafe_allow_html=True)

    add_viral = st.checkbox("🔥 Viral Terimler Ekle", value=True)

    product_count = st.slider("📊 Ürün Sayısı", 4, 12, 6)

    st.markdown("---")

    if st.button("🗑️ Listeyi Temizle", use_container_width=True):
        st.session_state.products = []
        st.session_state.current_query = ""

    st.markdown("---")

    st.markdown("### 🌏 Platform Linkleri")
    st.markdown("""
    Her üründe:
    - 📕 Xiaohongshu (小红书)
    - 🎵 Douyin (抖音)
    - 🛒 Taobao (淘宝)
    - 🏭 1688 (Toptan)
    - 🌐 Alibaba
    """)


# --- ANA SAYFA ---

# Header
st.markdown("""
<div class="header-pro">
    <h1 style="margin:0; font-size:2.5em; font-weight:700;">💎 FARK YARATAN ÜRÜN AVCISI</h1>
    <p style="margin:15px 0 0 0; font-size:1.2em; opacity:0.95;">
        Sıradan değil, MEKANİZMASI FARKLI oyuncakları bul!
    </p>
    <p style="margin:10px 0 0 0; font-size:0.95em; opacity:0.8;">
        Mini Gashapon • Pençeli Otomat • Çevirmeli Kutu • LED Sürpriz
    </p>
</div>
""", unsafe_allow_html=True)

# İstatistikler
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="stats-card">
        <p class="stats-number">{len(UNIQUE_CATEGORIES)}</p>
        <p class="stats-label">Farklı Kategori</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    total_kw = sum(len(c["keywords_en"]) + len(c["keywords_cn"]) for c in UNIQUE_CATEGORIES.values())
    st.markdown(f"""
    <div class="stats-card">
        <p class="stats-number">{total_kw}</p>
        <p class="stats-label">Özel Anahtar Kelime</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="stats-card">
        <p class="stats-number">{len(st.session_state.products)}</p>
        <p class="stats-label">Bulunan Ürün</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="stats-card">
        <p class="stats-number">6</p>
        <p class="stats-label">Çin Platformu</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- ANA ARAMA ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🚀 FARKLI ÜRÜN BUL!", type="primary", use_container_width=True, key="main_search"):
        with st.spinner("🔍 Fark yaratan ürünler aranıyor..."):
            time.sleep(0.3)
            new_products = fetch_products(selected_category, add_viral, product_count)
            st.session_state.products.extend(new_products)
            st.session_state.current_query = selected_category

# --- ÜRÜN GÖSTER ---
if st.session_state.products:

    st.markdown(f"""
    <div class="search-info">
        <span style="color:#f093fb; font-size:14px;">
            🎯 <strong>{st.session_state.current_query}</strong> &nbsp;|&nbsp;
            <strong>{len(st.session_state.products)}</strong> ürün bulundu
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Grid
    cols = st.columns(3)

    for idx, product in enumerate(st.session_state.products):
        with cols[idx % 3]:
            links = product.get('links', {})

            platform_html = ""
            for key, link_data in links.items():
                platform_html += f'''
                    <a href="{link_data['url']}" target="_blank" class="platform-btn {link_data['class']}">
                        {link_data['icon']} {link_data['name']}
                    </a>
                '''

            fallback_note = '<span class="unique-badge">📷 Temsili</span>' if product.get('is_fallback') else ''

            st.markdown(f"""
            <div class="product-card-pro">
                <img src="{product['image_url']}"
                     onerror="this.src='{random.choice(FALLBACK_IMAGES)}'"
                     alt="Ürün">
                <div class="card-content">
                    <span class="category-badge">{product.get('category', '')[:25]}</span>
                    <p class="card-title">{product['title'][:55]}...</p>
                    <p style="font-size:10px; color:#888; margin:5px 0;">
                        {product.get('description', '')[:40]}...
                    </p>
                    {fallback_note}
                    <div class="platform-buttons">
                        {platform_html}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # DAHA FAZLA YÜKLE
    st.markdown("<br><br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 DAHA FAZLA GETİR", use_container_width=True, key="load_more"):
            with st.spinner("📦 Yeni ürünler yükleniyor..."):
                time.sleep(0.3)
                new_products = fetch_products(selected_category, add_viral, product_count)
                st.session_state.products.extend(new_products)
                st.rerun()

else:
    st.markdown("""
    <div style="text-align:center; padding:60px; color:#888;">
        <h2 style="color:#f093fb;">💎 Fark Yaratan Ürün Ara!</h2>
        <p>Sıradan blind box değil, <strong>mekanizması farklı</strong> ürünleri keşfet.</p>
        <br>
        <p style="font-size:14px;">
            🎰 Mini Gashapon Makinesi<br>
            🎪 Masaüstü Pençeli Otomat<br>
            🎡 Çevirmeli Çark Oyuncaklar<br>
            💡 LED/Işıklı Sürpriz Kutular<br>
            🧲 Manyetik Levitasyon
        </p>
    </div>
    """, unsafe_allow_html=True)


# --- FOOTER ---
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; color:#555; padding:30px;">
    <p style="font-size:16px; font-weight:600;">💎 Fark Yaratan Ürün Avcısı v4.0</p>
    <p style="font-size:12px; margin-top:10px;">
        Sıradan değil, SUNUMU FARKLI ürünler!
    </p>
</div>
""", unsafe_allow_html=True)
