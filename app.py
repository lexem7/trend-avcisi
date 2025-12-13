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
    page_title="Çin Oyuncak Trend Avcısı",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- VERİ KAYDETME ---
FAVORITES_FILE = "favorites.json"

def load_favorites():
    if os.path.exists(FAVORITES_FILE):
        with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_favorite(product):
    favorites = load_favorites()
    product['saved_at'] = datetime.now().isoformat()
    favorites.append(product)
    with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
        json.dump(favorites, f, ensure_ascii=False, indent=2)

# --- TASARIM ---
st.markdown("""
<style>
    .stApp { background-color: #0a0a0a; }

    .header-gradient {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 20px;
        margin-bottom: 30px;
        text-align: center;
    }

    .product-card {
        background: linear-gradient(145deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #0f3460;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        transition: transform 0.3s, box-shadow 0.3s;
    }
    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    .product-card img {
        border-radius: 12px;
        width: 100%;
        height: 200px;
        object-fit: cover;
    }

    .category-tag {
        background: linear-gradient(90deg, #f093fb, #f5576c);
        color: white;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        display: inline-block;
        margin: 5px 3px;
    }

    .source-tag {
        background: #00d4ff;
        color: black;
        padding: 3px 10px;
        border-radius: 10px;
        font-size: 11px;
        font-weight: bold;
    }

    .search-btn {
        background: linear-gradient(90deg, #FF512F 0%, #F09819 100%);
        color: white;
        padding: 15px 40px;
        border: none;
        border-radius: 30px;
        font-size: 18px;
        font-weight: bold;
        cursor: pointer;
        width: 100%;
    }

    .link-button {
        display: inline-block;
        padding: 8px 16px;
        margin: 5px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
        font-size: 12px;
    }
    .aliexpress-btn { background: #e62e04; color: white; }
    .alibaba-btn { background: #ff6a00; color: white; }
    .taobao-btn { background: #ff5000; color: white; }
    .google-btn { background: #4285f4; color: white; }

    .stats-box {
        background: #1a1a2e;
        border: 1px solid #0f3460;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }

    .chinese-text {
        font-size: 14px;
        color: #888;
        background: #1a1a2e;
        padding: 5px 10px;
        border-radius: 5px;
        display: inline-block;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- KATEGORİLER VE ANAHTAR KELİMELER ---

CATEGORIES = {
    "🎁 Blind Box / Sürpriz Kutu": {
        "keywords_en": [
            "blind box figure", "mystery box toys", "surprise figure box",
            "popmart blind box", "lucky bag toys", "random figure box",
            "secret figure collection", "gashapon capsule", "surprise egg toys"
        ],
        "keywords_cn": [
            "盲盒", "惊喜盒", "神秘盒子", "泡泡玛特", "福袋玩具",
            "扭蛋", "奇趣蛋", "惊喜蛋"
        ],
        "brands": [
            "Popmart", "52TOYS", "TOPTOY", "Miniso Blind Box", "Rolife",
            "Tokidoki", "Sonny Angel", "Labubu", "Dimoo", "Molly",
            "Skullpanda", "Hirono", "Crybaby"
        ]
    },

    "🎰 Gashapon / Kapsül Makine": {
        "keywords_en": [
            "gashapon machine", "capsule toy machine", "gachapon toys",
            "vending machine toy", "capsule figure dispenser", "mini gashapon",
            "desktop gashapon", "candy machine toy"
        ],
        "keywords_cn": [
            "扭蛋机", "胶囊玩具机", "迷你扭蛋机", "桌面扭蛋",
            "糖果机玩具", "投币玩具机"
        ],
        "brands": [
            "Bandai Gashapon", "Takara Tomy", "Epoch", "Kitan Club"
        ]
    },

    "🌊 Reçine / Epoksi Sanat": {
        "keywords_en": [
            "resin diorama", "epoxy resin art", "resin ocean diorama",
            "titanic resin", "whale resin lamp", "resin cube art",
            "ocean scene resin", "underwater diorama", "resin night light",
            "jellyfish lamp resin", "resin ship diorama"
        ],
        "keywords_cn": [
            "树脂摆件", "环氧树脂艺术", "海洋树脂", "水晶胶摆件",
            "树脂夜灯", "海洋场景树脂", "树脂立方体"
        ],
        "brands": []
    },

    "📱 Telefon Aksesuarı Figür": {
        "keywords_en": [
            "phone screen figure", "phone dust plug figure", "phone holder figure",
            "phone case decoration", "phone charm figure", "hippers phone",
            "phone attachment toy", "cable protector figure"
        ],
        "keywords_cn": [
            "手机支架摆件", "手机壳装饰", "手机挂件", "数据线保护套",
            "屏幕装饰"
        ],
        "brands": [
            "Sonny Angel Hippers", "Kitan Club"
        ]
    },

    "🦸 Anime / Karakter Figür": {
        "keywords_en": [
            "anime figure", "chibi figure", "nendoroid style", "anime blind box",
            "kawaii figure", "anime gacha", "character figure",
            "stitch figure", "disney mystery figure", "sanrio figure"
        ],
        "keywords_cn": [
            "动漫手办", "Q版手办", "卡通盲盒", "迪士尼盲盒",
            "史迪仔手办", "三丽鸥手办", "可爱手办"
        ],
        "brands": [
            "Disney", "Sanrio", "Stitch", "Kuromi", "Hello Kitty",
            "Cinnamoroll", "My Melody", "Doraemon", "Crayon Shin-chan"
        ]
    },

    "🎮 Mini Oyuncak / Gadget": {
        "keywords_en": [
            "fidget toy", "mini toy", "desk toy", "pocket toy",
            "stress relief toy", "decompression toy", "sensory toy",
            "magnetic toy", "kinetic toy", "infinity cube"
        ],
        "keywords_cn": [
            "解压玩具", "迷你玩具", "桌面玩具", "减压神器",
            "口袋玩具", "磁性玩具", "创意玩具"
        ],
        "brands": []
    },

    "🧸 Peluş / Yumuşak Oyuncak": {
        "keywords_en": [
            "plush blind bag", "mystery plush", "surprise plush",
            "mini plush collection", "keychain plush", "squishmallow mystery"
        ],
        "keywords_cn": [
            "毛绒盲袋", "惊喜毛绒", "迷你毛绒", "钥匙扣毛绒"
        ],
        "brands": [
            "Squishmallow", "Labubu Plush"
        ]
    },

    "🎃 Sezonluk / Özel Edisyon": {
        "keywords_en": [
            "halloween gashapon", "christmas blind box", "chinese new year figure",
            "limited edition figure", "seasonal mystery box", "holiday surprise toy"
        ],
        "keywords_cn": [
            "万圣节扭蛋", "圣诞盲盒", "新年手办", "限定版", "节日惊喜"
        ],
        "brands": []
    }
}

# Viral / Trend Anahtar Kelimeleri
VIRAL_TERMS = [
    "viral tiktok toy", "trending toy 2024", "popular blind box",
    "best seller figure", "hot toy china", "new release figure",
    "must have toy", "aesthetic toy", "desk aesthetic"
]

VIRAL_TERMS_CN = [
    "爆款玩具", "网红玩具", "热门盲盒", "抖音同款", "新品上市"
]


# --- ARAMA FONKSİYONLARI ---

def generate_search_query(category, include_viral=True, language="both"):
    """Rastgele arama sorgusu oluştur"""
    cat_data = CATEGORIES[category]

    queries = []

    # İngilizce sorgu
    if language in ["en", "both"]:
        base = random.choice(cat_data["keywords_en"])
        if cat_data["brands"] and random.random() > 0.5:
            base = random.choice(cat_data["brands"]) + " " + base
        if include_viral and random.random() > 0.3:
            base += " " + random.choice(VIRAL_TERMS)
        queries.append(base)

    # Çince sorgu
    if language in ["cn", "both"]:
        cn_query = random.choice(cat_data["keywords_cn"])
        if include_viral and random.random() > 0.5:
            cn_query += " " + random.choice(VIRAL_TERMS_CN)
        queries.append(cn_query)

    return queries


def search_products(query, max_results=6):
    """DuckDuckGo ile ürün ara"""
    results = []

    try:
        with DDGS() as ddgs:
            # Görsel arama
            images = list(ddgs.images(query, max_results=max_results))
            for img in images:
                results.append({
                    "type": "image",
                    "title": img.get("title", ""),
                    "image_url": img.get("image", ""),
                    "source_url": img.get("url", ""),
                    "source": img.get("source", "")
                })
    except Exception as e:
        st.warning(f"Görsel arama hatası: {str(e)[:50]}")

    return results


def generate_shopping_links(query):
    """E-ticaret sitesi linkleri oluştur"""
    encoded = urllib.parse.quote(query)

    return {
        "aliexpress": f"https://www.aliexpress.com/wholesale?SearchText={encoded}",
        "alibaba": f"https://www.alibaba.com/trade/search?SearchText={encoded}",
        "taobao": f"https://s.taobao.com/search?q={encoded}",
        "1688": f"https://s.1688.com/selloffer/offer_search.htm?keywords={encoded}",
        "google": f"https://www.google.com/search?q={encoded}&tbm=isch",
        "google_shopping": f"https://www.google.com/search?q={encoded}&tbm=shop"
    }


# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## 🎯 Arama Ayarları")

    # Kategori seçimi
    selected_categories = st.multiselect(
        "📦 Kategoriler",
        options=list(CATEGORIES.keys()),
        default=list(CATEGORIES.keys())[:3],
        help="Hangi kategorilerde arama yapılsın?"
    )

    # Dil seçimi
    search_language = st.radio(
        "🌐 Arama Dili",
        options=["both", "en", "cn"],
        format_func=lambda x: {"both": "🌍 Her İkisi", "en": "🇬🇧 İngilizce", "cn": "🇨🇳 Çince"}[x],
        index=0
    )

    # Viral filtresi
    include_viral = st.checkbox("🔥 Viral/Trend Kelimeler Ekle", value=True)

    # Sonuç sayısı
    results_per_query = st.slider("📊 Kategori Başına Sonuç", 3, 12, 6)

    st.markdown("---")

    # Özel arama
    st.markdown("## 🔍 Özel Arama")
    custom_query = st.text_input("Kendi arama terimini yaz", placeholder="örn: labubu vinyl face")

    st.markdown("---")

    # Favoriler
    st.markdown("## ⭐ Favorilerim")
    favorites = load_favorites()
    st.info(f"Kayıtlı: {len(favorites)} ürün")

    if st.button("📋 Favorileri Göster"):
        st.session_state.show_favorites = True


# --- ANA SAYFA ---
st.markdown("""
<div class="header-gradient">
    <h1 style="margin:0; font-size:2.5em;">🎯 ÇİN OYUNCAK TREND AVCISI</h1>
    <p style="margin:10px 0 0 0; font-size:1.2em; opacity:0.9;">
        Çin'den viral oyuncakları, sürpriz kutuları ve ilginç ürünleri keşfet!
    </p>
</div>
""", unsafe_allow_html=True)

# Hızlı istatistikler
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="stats-box">
        <h3 style="color:#667eea; margin:0;">📦 {len(CATEGORIES)}</h3>
        <p style="margin:0; color:#888;">Kategori</p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    total_keywords = sum(len(c["keywords_en"]) + len(c["keywords_cn"]) for c in CATEGORIES.values())
    st.markdown(f"""
    <div class="stats-box">
        <h3 style="color:#764ba2; margin:0;">🔑 {total_keywords}</h3>
        <p style="margin:0; color:#888;">Anahtar Kelime</p>
    </div>
    """, unsafe_allow_html=True)
with col3:
    total_brands = sum(len(c["brands"]) for c in CATEGORIES.values())
    st.markdown(f"""
    <div class="stats-box">
        <h3 style="color:#f093fb; margin:0;">🏷️ {total_brands}</h3>
        <p style="margin:0; color:#888;">Marka</p>
    </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown(f"""
    <div class="stats-box">
        <h3 style="color:#00d4ff; margin:0;">⭐ {len(favorites)}</h3>
        <p style="margin:0; color:#888;">Favori</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- ARAMA BUTONU ---
search_col1, search_col2, search_col3 = st.columns([1, 2, 1])
with search_col2:
    search_clicked = st.button("🚀 TREND AVLA!", type="primary", use_container_width=True)

# --- ÖZEL ARAMA ---
if custom_query:
    st.markdown("---")
    st.markdown(f"### 🔍 Özel Arama: '{custom_query}'")

    with st.spinner("Aranıyor..."):
        results = search_products(custom_query, max_results=12)
        links = generate_shopping_links(custom_query)

        # Linkler
        st.markdown(f"""
        <div style="margin: 20px 0;">
            <a href="{links['aliexpress']}" target="_blank" class="link-button aliexpress-btn">🛒 AliExpress</a>
            <a href="{links['alibaba']}" target="_blank" class="link-button alibaba-btn">🏭 Alibaba</a>
            <a href="{links['taobao']}" target="_blank" class="link-button taobao-btn">🛍️ Taobao</a>
            <a href="{links['google']}" target="_blank" class="link-button google-btn">🔍 Google</a>
        </div>
        """, unsafe_allow_html=True)

        if results:
            cols = st.columns(4)
            for i, result in enumerate(results):
                with cols[i % 4]:
                    st.markdown(f"""
                    <div class="product-card">
                        <img src="{result['image_url']}" onerror="this.src='https://via.placeholder.com/200?text=No+Image'">
                        <p style="font-size:12px; margin:10px 0 5px 0; color:#ccc; height:40px; overflow:hidden;">
                            {result['title'][:60]}...
                        </p>
                        <span class="source-tag">{result.get('source', 'Web')[:20]}</span>
                    </div>
                    """, unsafe_allow_html=True)

# --- ANA ARAMA ---
if search_clicked:
    if not selected_categories:
        st.error("⚠️ En az bir kategori seçmelisin!")
    else:
        st.markdown("---")

        all_results = []

        # Her kategori için ara
        for category in selected_categories:
            st.markdown(f"### {category}")

            with st.spinner(f"{category} taranıyor..."):
                queries = generate_search_query(category, include_viral, search_language)

                category_results = []
                for query in queries:
                    results = search_products(query, max_results=results_per_query // len(queries))
                    for r in results:
                        r['category'] = category
                        r['query'] = query
                    category_results.extend(results)
                    time.sleep(0.5)  # Rate limiting

                # Alışveriş linkleri
                main_query = queries[0] if queries else category
                links = generate_shopping_links(main_query)

                st.markdown(f"""
                <div style="margin: 10px 0;">
                    <span class="chinese-text">🔍 Aranan: {' | '.join(queries)}</span>
                </div>
                <div style="margin: 10px 0;">
                    <a href="{links['aliexpress']}" target="_blank" class="link-button aliexpress-btn">🛒 AliExpress</a>
                    <a href="{links['alibaba']}" target="_blank" class="link-button alibaba-btn">🏭 Alibaba</a>
                    <a href="{links['1688']}" target="_blank" class="link-button taobao-btn">🏭 1688</a>
                    <a href="{links['google']}" target="_blank" class="link-button google-btn">🔍 Google</a>
                </div>
                """, unsafe_allow_html=True)

                if category_results:
                    cols = st.columns(4)
                    for i, result in enumerate(category_results[:8]):
                        with cols[i % 4]:
                            st.markdown(f"""
                            <div class="product-card">
                                <img src="{result['image_url']}" onerror="this.src='https://via.placeholder.com/200?text=No+Image'">
                                <p style="font-size:11px; margin:10px 0 5px 0; color:#ccc; height:35px; overflow:hidden;">
                                    {result['title'][:50]}...
                                </p>
                                <span class="source-tag">{result.get('source', 'Web')[:15]}</span>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("Bu kategoride görsel bulunamadı. Yukarıdaki linklerden manuel arama yapabilirsin.")

                all_results.extend(category_results)

            st.markdown("<br>", unsafe_allow_html=True)

        # Özet
        st.markdown("---")
        st.success(f"✅ Toplam {len(all_results)} ürün bulundu!")

# --- FAVORİLER SAYFASI ---
if st.session_state.get('show_favorites', False):
    st.markdown("---")
    st.markdown("## ⭐ Kaydedilen Favoriler")

    favorites = load_favorites()
    if favorites:
        cols = st.columns(4)
        for i, fav in enumerate(favorites):
            with cols[i % 4]:
                st.markdown(f"""
                <div class="product-card">
                    <img src="{fav.get('image_url', '')}" onerror="this.src='https://via.placeholder.com/200?text=No+Image'">
                    <p style="font-size:12px; color:#ccc;">{fav.get('title', '')[:50]}</p>
                    <span class="category-tag">{fav.get('category', 'Genel')}</span>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Henüz favori eklenmemiş.")

    if st.button("❌ Kapat"):
        st.session_state.show_favorites = False
        st.rerun()

# --- FOOTER ---
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#666; padding:20px;">
    <p>🎯 Çin Oyuncak Trend Avcısı v2.0</p>
    <p style="font-size:12px;">
        Desteklenen Platformlar: AliExpress, Alibaba, 1688, Taobao, Google Shopping
    </p>
</div>
""", unsafe_allow_html=True)
