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
    page_title="Çin Trend Avcısı Pro",
    page_icon="🎯",
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
if 'favorites' not in st.session_state:
    st.session_state.favorites = []

# --- FALLBACK UNSPLASH GÖRSELLERİ ---
FALLBACK_IMAGES = [
    "https://images.unsplash.com/photo-1558060370-d644479cb6f7?w=400&h=300&fit=crop",  # Toys
    "https://images.unsplash.com/photo-1566576912321-d58ddd7a6088?w=400&h=300&fit=crop",  # Colorful toys
    "https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=400&h=300&fit=crop",  # Kids toys
    "https://images.unsplash.com/photo-1558060370-d644479cb6f7?w=400&h=300&fit=crop",  # Plush
    "https://images.unsplash.com/photo-1596461404969-9ae70f2830c1?w=400&h=300&fit=crop",  # Figure
    "https://images.unsplash.com/photo-1608889825103-eb5ed706fc64?w=400&h=300&fit=crop",  # Mystery box style
    "https://images.unsplash.com/photo-1581235720704-06d3acfcb36f?w=400&h=300&fit=crop",  # Toy car
    "https://images.unsplash.com/photo-1594787318286-3d835c1d207f?w=400&h=300&fit=crop",  # Puzzle toy
]

# --- VERİ KAYDETME ---
FAVORITES_FILE = "favorites.json"

def load_favorites():
    try:
        if os.path.exists(FAVORITES_FILE):
            with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return []

def save_favorites_to_file(favorites):
    try:
        with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
            json.dump(favorites, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

# --- TASARIM (DARK MODE PRO) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    .stApp {
        background: linear-gradient(180deg, #0a0a0f 0%, #1a1a2e 100%);
        font-family: 'Inter', sans-serif;
    }

    .header-pro {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        padding: 40px;
        border-radius: 24px;
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
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
        box-shadow: 0 25px 80px rgba(102, 126, 234, 0.4);
        border-color: rgba(102, 126, 234, 0.5);
    }
    .product-card-pro img {
        width: 100%;
        height: 220px;
        object-fit: cover;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    .card-content {
        padding: 20px;
    }
    .card-title {
        font-size: 14px;
        font-weight: 600;
        color: #fff;
        margin-bottom: 12px;
        height: 42px;
        overflow: hidden;
        line-height: 1.4;
    }

    /* Platform Butonları */
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
        font-size: 11px;
        transition: all 0.3s;
    }
    .platform-btn:hover {
        transform: scale(1.05);
        filter: brightness(1.2);
    }

    /* Platform Renkleri */
    .xiaohongshu-btn { background: linear-gradient(135deg, #ff2442, #ff6b6b); color: white; }
    .douyin-btn { background: linear-gradient(135deg, #00f2ea, #ff0050); color: white; }
    .taobao-btn { background: linear-gradient(135deg, #ff5000, #ff8533); color: white; }
    .btn-1688 { background: linear-gradient(135deg, #ff6600, #ffaa00); color: white; }
    .alibaba-btn { background: linear-gradient(135deg, #ff6a00, #ee0a24); color: white; }
    .google-btn { background: linear-gradient(135deg, #4285f4, #34a853); color: white; }

    .source-badge {
        background: rgba(0, 212, 255, 0.2);
        color: #00d4ff;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 10px;
        font-weight: 600;
        display: inline-block;
    }

    .category-badge {
        background: linear-gradient(90deg, #f093fb, #f5576c);
        color: white;
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 10px;
    }

    .stats-card {
        background: linear-gradient(145deg, #1e1e2e, #2a2a4a);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 25px;
        text-align: center;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
    }
    .stats-number {
        font-size: 2.5em;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea, #f093fb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .stats-label {
        color: #888;
        font-size: 14px;
        margin-top: 5px;
    }

    .load-more-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 18px 50px;
        border: none;
        border-radius: 30px;
        font-size: 18px;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.3s;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.4);
    }
    .load-more-btn:hover {
        transform: scale(1.05);
        box-shadow: 0 15px 50px rgba(102, 126, 234, 0.6);
    }

    .search-info {
        background: rgba(102, 126, 234, 0.1);
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 12px;
        padding: 15px 20px;
        margin: 20px 0;
    }
    .search-info-text {
        color: #a0a0ff;
        font-size: 13px;
    }

    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        margin: 30px 0;
    }

    .fallback-badge {
        background: rgba(255, 193, 7, 0.2);
        color: #ffc107;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 9px;
        margin-left: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- SMART NOVELTY KATEGORİLERİ ---

SMART_CATEGORIES = {
    "🔧 Mekanik Sürpriz (Mechanical)": {
        "keywords_en": [
            "mechanical blind box", "wind up toy mechanism", "clockwork toy",
            "gear mechanism toy", "mechanical movement figure", "kinetic blind box",
            "self moving toy", "mechanical surprise toy", "motor driven toy"
        ],
        "keywords_cn": [
            "机械盲盒", "发条玩具", "齿轮玩具", "机械结构玩具",
            "自动玩具", "机械惊喜", "动力玩具", "机械手办"
        ]
    },

    "🌀 Fizik & Yerçekimi (Gravity/Physics)": {
        "keywords_en": [
            "gravity defying toy", "physics toy", "balancing toy figure",
            "levitating display", "magnetic levitation toy", "pendulum toy",
            "kinetic sculpture toy", "perpetual motion toy", "gyroscope toy"
        ],
        "keywords_cn": [
            "重力玩具", "物理玩具", "平衡玩具", "磁悬浮玩具",
            "陀螺玩具", "动能雕塑", "永动玩具", "科学玩具"
        ]
    },

    "🦋 Dönüşüm Sürprizi (Transformation)": {
        "keywords_en": [
            "transformation toy", "morphing figure", "shape shifting toy",
            "deformation blind box", "converting toy", "transformer style toy",
            "changeable figure", "multi form toy", "metamorphosis toy"
        ],
        "keywords_cn": [
            "变形玩具", "变形盲盒", "变形金刚", "可变形手办",
            "形态转换玩具", "多形态玩具", "变身玩具"
        ]
    },

    "🎰 Yaratıcı Gashapon (Creative Gashapon)": {
        "keywords_en": [
            "creative gashapon", "unique capsule toy", "designer gashapon",
            "art toy gashapon", "collectible capsule", "premium gashapon",
            "limited gashapon", "special edition capsule", "innovative vending toy"
        ],
        "keywords_cn": [
            "创意扭蛋", "设计师扭蛋", "艺术扭蛋", "限定扭蛋",
            "高端扭蛋", "特别版扭蛋", "收藏扭蛋", "精品扭蛋"
        ]
    },

    "🌊 Reçine Sanat Diorama": {
        "keywords_en": [
            "resin diorama cube", "epoxy ocean art", "resin whale lamp",
            "underwater scene resin", "titanic resin art", "deep sea diorama",
            "resin jellyfish lamp", "ocean cube art", "3d resin scene"
        ],
        "keywords_cn": [
            "树脂立方体", "海洋树脂", "环氧树脂艺术", "水晶胶摆件",
            "深海场景", "树脂夜灯", "海洋立方体", "树脂工艺品"
        ]
    },

    "🎭 Sürreal & Sanat Oyuncak": {
        "keywords_en": [
            "designer toy", "art figure", "surreal toy", "abstract figure",
            "artist collaboration toy", "gallery toy", "museum figure",
            "conceptual toy", "avant garde figure"
        ],
        "keywords_cn": [
            "设计师玩具", "艺术手办", "潮流玩具", "抽象手办",
            "艺术家联名", "概念玩具", "收藏艺术品", "限量艺术玩具"
        ]
    },

    "📱 Akıllı Telefon Aksesuarı": {
        "keywords_en": [
            "phone hippers figure", "screen attachment toy", "phone holder figure",
            "cable bite figure", "phone decoration toy", "magnetic phone toy",
            "phone stand figure", "cute phone accessory"
        ],
        "keywords_cn": [
            "手机支架玩具", "屏幕挂件", "数据线保护套", "手机装饰",
            "磁吸手机架", "创意手机配件", "可爱手机挂件"
        ]
    },

    "🎪 İnteraktif & Sürpriz": {
        "keywords_en": [
            "interactive blind box", "surprise reveal toy", "unboxing experience",
            "mystery reveal figure", "hidden feature toy", "secret compartment toy",
            "puzzle blind box", "discovery toy"
        ],
        "keywords_cn": [
            "互动盲盒", "惊喜揭示", "隐藏款玩具", "解密玩具",
            "秘密隔层", "探索玩具", "谜题盲盒", "发现玩具"
        ]
    }
}

# Viral / Trend Anahtar Kelimeleri
VIRAL_TERMS = [
    "viral 2024", "tiktok trending", "xiaohongshu viral", "douyin hot",
    "best seller", "new release", "limited edition", "must have",
    "aesthetic desk", "collector item"
]

VIRAL_TERMS_CN = [
    "爆款", "网红", "抖音同款", "小红书推荐", "热门",
    "新品", "限定", "必入", "潮流", "收藏级"
]


# --- ÇİN PLATFORMLARI İÇİN DERİN ARAMA LİNKLERİ ---

def generate_chinese_search_links(query_en, query_cn):
    """Çin platformları için derin arama linkleri oluştur"""

    # Çince sorgu için URL encode
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

def generate_search_query(category, include_viral=True):
    """Akıllı arama sorgusu oluştur"""
    cat_data = SMART_CATEGORIES[category]

    # İngilizce ve Çince sorgu
    en_query = random.choice(cat_data["keywords_en"])
    cn_query = random.choice(cat_data["keywords_cn"])

    # Viral terim ekle
    if include_viral and random.random() > 0.3:
        en_query += " " + random.choice(VIRAL_TERMS)
        cn_query += " " + random.choice(VIRAL_TERMS_CN)

    return en_query, cn_query


def search_products_safe(query, max_results=8):
    """Güvenli ürün arama - hata yönetimi ile"""
    results = []

    try:
        with DDGS() as ddgs:
            images = list(ddgs.images(query, max_results=max_results))

            for img in images:
                image_url = img.get("image", "")

                # Görsel URL kontrolü
                if not image_url or len(image_url) < 10:
                    image_url = random.choice(FALLBACK_IMAGES)
                    is_fallback = True
                else:
                    is_fallback = False

                results.append({
                    "title": img.get("title", "Ürün Başlığı Yok"),
                    "image_url": image_url,
                    "source_url": img.get("url", "#"),
                    "source": img.get("source", "Web"),
                    "is_fallback": is_fallback
                })

    except Exception as e:
        # Hata durumunda fallback ürünler oluştur
        st.warning(f"⚠️ Arama hatası, yedek görseller kullanılıyor...")
        for i in range(3):
            results.append({
                "title": f"Keşfedilecek Ürün #{i+1}",
                "image_url": random.choice(FALLBACK_IMAGES),
                "source_url": "#",
                "source": "Öneri",
                "is_fallback": True
            })

    return results


def load_more_products(category, include_viral=True, count=6):
    """Daha fazla ürün yükle"""
    en_query, cn_query = generate_search_query(category, include_viral)

    # Farklı sonuçlar için sorguya random ek
    variation = random.choice(["new", "hot", "best", "unique", "special", "rare"])
    modified_query = f"{en_query} {variation}"

    new_products = search_products_safe(modified_query, max_results=count)

    # Her ürüne kategori ve sorgu bilgisi ekle
    for product in new_products:
        product['category'] = category
        product['query_en'] = en_query
        product['query_cn'] = cn_query
        product['links'] = generate_chinese_search_links(en_query, cn_query)

    return new_products


# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## 🎯 Arama Ayarları")

    # Kategori seçimi
    selected_category = st.selectbox(
        "📦 Kategori Seç",
        options=list(SMART_CATEGORIES.keys()),
        index=0,
        help="Hangi tür akıllı oyuncakları arıyorsun?"
    )

    # Viral filtresi
    include_viral = st.checkbox("🔥 Viral/Trend Terimleri Ekle", value=True)

    # Sonuç sayısı
    results_count = st.slider("📊 Yüklenecek Ürün Sayısı", 4, 12, 6)

    st.markdown("---")

    # Yeni arama butonu
    if st.button("🔄 Yeni Arama Başlat", use_container_width=True):
        st.session_state.products = []
        st.session_state.search_offset = 0
        st.session_state.current_query = selected_category

    st.markdown("---")

    # Platform bilgisi
    st.markdown("### 🌏 Desteklenen Platformlar")
    st.markdown("""
    - 📕 **Xiaohongshu** (小红书)
    - 🎵 **Douyin** (抖音)
    - 🛒 **Taobao** (淘宝)
    - 🏭 **1688** (Toptan)
    - 🌐 **Alibaba**
    - 🔍 **Google Images**
    """)

    st.markdown("---")

    # Favoriler
    favorites = load_favorites()
    st.markdown(f"### ⭐ Favoriler: {len(favorites)}")


# --- ANA SAYFA ---

# Header
st.markdown("""
<div class="header-pro">
    <h1 style="margin:0; font-size:2.8em; font-weight:700;">🎯 ÇİN TREND AVCISI PRO</h1>
    <p style="margin:15px 0 0 0; font-size:1.3em; opacity:0.95;">
        Xiaohongshu • Douyin • 1688 • Taobao | Akıllı Oyuncak Keşfi
    </p>
</div>
""", unsafe_allow_html=True)

# İstatistikler
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="stats-card">
        <p class="stats-number">{len(SMART_CATEGORIES)}</p>
        <p class="stats-label">Akıllı Kategori</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    total_kw = sum(len(c["keywords_en"]) + len(c["keywords_cn"]) for c in SMART_CATEGORIES.values())
    st.markdown(f"""
    <div class="stats-card">
        <p class="stats-number">{total_kw}</p>
        <p class="stats-label">Anahtar Kelime</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="stats-card">
        <p class="stats-number">{len(st.session_state.products)}</p>
        <p class="stats-label">Yüklenen Ürün</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="stats-card">
        <p class="stats-number">6</p>
        <p class="stats-label">Platform</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- ANA ARAMA BUTONU ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🚀 TREND AVLA!", type="primary", use_container_width=True, key="main_search"):
        with st.spinner("🔍 Çin pazarları taranıyor..."):
            time.sleep(0.5)
            new_products = load_more_products(selected_category, include_viral, results_count)
            st.session_state.products.extend(new_products)
            st.session_state.current_query = selected_category

# --- ÜRÜN KARTLARI ---
if st.session_state.products:

    # Arama bilgisi
    st.markdown(f"""
    <div class="search-info">
        <span class="search-info-text">
            🔍 <strong>{st.session_state.current_query}</strong> kategorisinde
            <strong>{len(st.session_state.products)}</strong> ürün bulundu
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Ürün grid
    cols = st.columns(3)

    for idx, product in enumerate(st.session_state.products):
        with cols[idx % 3]:
            links = product.get('links', {})
            fallback_badge = '<span class="fallback-badge">Temsili</span>' if product.get('is_fallback') else ''

            # Platform butonları HTML
            platform_html = ""
            for key, link_data in links.items():
                platform_html += f'''
                    <a href="{link_data['url']}" target="_blank" class="platform-btn {link_data['class']}">
                        {link_data['icon']} {link_data['name']}
                    </a>
                '''

            st.markdown(f"""
            <div class="product-card-pro">
                <img src="{product['image_url']}"
                     onerror="this.src='{random.choice(FALLBACK_IMAGES)}'"
                     alt="{product['title'][:30]}">
                <div class="card-content">
                    <span class="category-badge">{product.get('category', 'Trend')[:20]}</span>
                    <p class="card-title">{product['title'][:60]}...</p>
                    <span class="source-badge">{product.get('source', 'Web')[:15]}{fallback_badge}</span>

                    <div class="platform-buttons">
                        {platform_html}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # --- DAHA FAZLA YÜKLE BUTONU ---
    st.markdown("<br><br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 DAHA FAZLA ÜRÜN GETİR", use_container_width=True, key="load_more"):
            with st.spinner("📦 Yeni ürünler yükleniyor..."):
                time.sleep(0.5)
                new_products = load_more_products(selected_category, include_viral, results_count)
                st.session_state.products.extend(new_products)
                st.rerun()

else:
    # Boş durum
    st.markdown("""
    <div style="text-align:center; padding:60px; color:#666;">
        <h2>🎯 Trend Avına Başla!</h2>
        <p>Yukarıdaki butona tıklayarak Çin pazarlarını taramaya başla.</p>
        <p style="font-size:14px; margin-top:20px;">
            Xiaohongshu, Douyin, 1688, Taobao platformlarına özel derin arama linkleri ile
            <br>en ilginç ve viral oyuncakları keşfet!
        </p>
    </div>
    """, unsafe_allow_html=True)


# --- FOOTER ---
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; color:#555; padding:30px;">
    <p style="font-size:16px; font-weight:600;">🎯 Çin Trend Avcısı Pro v3.0</p>
    <p style="font-size:12px; margin-top:10px;">
        📕 Xiaohongshu • 🎵 Douyin • 🛒 Taobao • 🏭 1688 • 🌐 Alibaba
    </p>
    <p style="font-size:11px; color:#444; margin-top:15px;">
        Akıllı Oyuncak Keşfi | Mekanik • Fizik • Dönüşüm • Gashapon
    </p>
</div>
""", unsafe_allow_html=True)
