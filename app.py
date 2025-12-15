import streamlit as st
from duckduckgo_search import DDGS
import random
import time
import urllib.parse
import json
import os
from datetime import datetime
import re

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="İlginç Ürün Avcısı",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- VERİTABANI DOSYALARI ---
LIKES_FILE = "liked_products.json"
DISLIKES_FILE = "disliked_products.json"
LEARNED_KEYWORDS_FILE = "learned_keywords.json"

# --- SESSION STATE ---
if 'products' not in st.session_state:
    st.session_state.products = []
if 'search_count' not in st.session_state:
    st.session_state.search_count = 0

# --- VERİTABANI FONKSİYONLARI ---
def load_json(filename):
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return []

def save_json(filename, data):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except:
        pass

def load_learned_keywords():
    data = load_json(LEARNED_KEYWORDS_FILE)
    if isinstance(data, dict):
        return data
    return {"positive": {}, "negative": {}, "patterns": []}

def save_learned_keywords(data):
    save_json(LEARNED_KEYWORDS_FILE, data)

# --- BEĞENİ SİSTEMİ ---
def like_product(product):
    likes = load_json(LIKES_FILE)
    product['liked_at'] = datetime.now().isoformat()
    likes.append(product)
    save_json(LIKES_FILE, likes)
    learn_from_product(product, positive=True)
    return len(likes)

def dislike_product(product):
    dislikes = load_json(DISLIKES_FILE)
    product['disliked_at'] = datetime.now().isoformat()
    dislikes.append(product)
    save_json(DISLIKES_FILE, dislikes)
    learn_from_product(product, positive=False)
    return len(dislikes)

def learn_from_product(product, positive=True):
    keywords = load_learned_keywords()
    title = product.get('title', '').lower()
    words = re.findall(r'\b[a-zA-Z\u4e00-\u9fff]{2,}\b', title)
    stop_words = {'the', 'and', 'for', 'with', 'new', 'hot', 'sale', 'free', 'shipping',
                  'pcs', 'set', 'buy', 'get', 'off', 'best', 'top', 'good', 'great',
                  'item', 'product', 'quality', 'high', 'low', 'price', 'cheap', 'from'}
    target = "positive" if positive else "negative"
    for word in words:
        if word.lower() not in stop_words and len(word) > 2:
            if word not in keywords[target]:
                keywords[target][word] = 0
            keywords[target][word] += 1
    if product.get('category') and positive:
        if product['category'] not in keywords['patterns']:
            keywords['patterns'].append(product['category'])
    save_learned_keywords(keywords)

def get_smart_search_terms():
    keywords = load_learned_keywords()
    positive = keywords.get('positive', {})
    negative = keywords.get('negative', {})
    scores = {}
    for word, count in positive.items():
        scores[word] = count
    for word, count in negative.items():
        if word in scores:
            scores[word] -= count * 2
        else:
            scores[word] = -count * 2
    sorted_words = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [w for w, s in sorted_words[:10] if s > 0]

def get_preference_stats():
    likes = load_json(LIKES_FILE)
    dislikes = load_json(DISLIKES_FILE)
    keywords = load_learned_keywords()
    top_positive = sorted(keywords.get('positive', {}).items(), key=lambda x: x[1], reverse=True)[:5]
    top_negative = sorted(keywords.get('negative', {}).items(), key=lambda x: x[1], reverse=True)[:5]
    return {
        'total_likes': len(likes),
        'total_dislikes': len(dislikes),
        'top_positive': top_positive,
        'top_negative': top_negative,
        'patterns': keywords.get('patterns', [])[:5]
    }

# --- PLATFORMLAR ---
PLATFORMS = [
    "site:aliexpress.com",
    "site:alibaba.com",
    "site:dhgate.com",
    "site:amazon.com",
    "site:ebay.com",
    "site:wish.com",
    "site:banggood.com",
    "site:gearbest.com",
    "site:made-in-china.com",
    "site:etsy.com"
]

# --- İLGİNÇ ÜRÜN KATEGORİLERİ ---
INTERESTING_CATEGORIES = {
    "🎰 Mini Otomatlar & Makineler": {
        "searches": [
            "mini gashapon machine capsule dispenser",
            "desktop candy vending machine",
            "mini claw machine toy",
            "gachapon egg machine small",
            "coin operated mini game",
            "capsule toy vending small",
            "desktop slot machine toy",
            "mini crane game machine",
            "candy grabber machine small",
            "egg twisting machine toy"
        ]
    },

    "🌊 Reçine & Epoksi Sanat Küpleri": {
        "searches": [
            "resin diorama cube ocean",
            "epoxy whale shark lamp",
            "titanic resin cube ship",
            "underwater world resin",
            "deep sea diorama cube",
            "jellyfish resin lamp",
            "resin aquarium cube art",
            "ocean scene epoxy cube",
            "shipwreck resin diorama",
            "coral reef resin art"
        ]
    },

    "📱 Telefon Hippers & Ekran Figürleri": {
        "searches": [
            "phone hippers figure screen",
            "sonny angel phone decoration",
            "screen buddy figure cute",
            "phone dust plug figure",
            "cable bite animal protector",
            "phone stand figure cute",
            "monitor buddy toy small",
            "laptop decoration figure",
            "screen hanger toy cute",
            "phone charm dangling figure"
        ]
    },

    "🎁 Mekanik Sürpriz Kutuları": {
        "searches": [
            "mechanical surprise box pop up",
            "explosion gift box diy",
            "spring loaded surprise box",
            "jumping scare box toy",
            "puzzle box secret compartment",
            "magic trick box disappear",
            "wooden puzzle box secret",
            "surprise explosion photo box",
            "pop up cube gift box",
            "mechanical iris box"
        ]
    },

    "🔮 Sihirli & İllüzyon Oyuncaklar": {
        "searches": [
            "infinity mirror cube toy",
            "hologram display small 3d",
            "levitating display magnetic",
            "optical illusion spinner",
            "impossible object puzzle",
            "magic cube transforming",
            "holographic projector small",
            "infinity cube fidget",
            "mirror illusion box",
            "floating ball magic toy"
        ]
    },

    "🌀 Kinetik & Hareket Oyuncakları": {
        "searches": [
            "perpetual motion desk toy",
            "kinetic sculpture small",
            "newton cradle premium",
            "gyroscope metal precision",
            "spinning top forever",
            "balance bird toy",
            "magnetic sculpture desk",
            "tumbling toy physics",
            "pendulum wave toy",
            "kinetic sand sculpture"
        ]
    },

    "🎭 Koleksiyon Blind Box Figürler": {
        "searches": [
            "designer blind box figure",
            "art toy collectible small",
            "popmart blind box",
            "labubu figure blind box",
            "molly blind box figure",
            "skullpanda blind box",
            "dimoo blind box",
            "hirono blind box",
            "farmer bob blind box",
            "baby three blind box"
        ]
    },

    "🦕 Mini Dünya & Diorama": {
        "searches": [
            "miniature world terrarium",
            "tiny diorama cube",
            "micro landscape glass",
            "miniature room box kit",
            "small world jar terrarium",
            "mini garden terrarium kit",
            "book nook diorama insert",
            "shadow box diorama small",
            "miniature scene glass dome",
            "tiny world snow globe"
        ]
    },

    "💡 LED & Işıklı Dekoratif": {
        "searches": [
            "led cloud light lamp",
            "neon sign small custom",
            "galaxy projector lamp",
            "thunder cloud lamp storm",
            "moon lamp levitating",
            "crystal ball lamp 3d",
            "aurora projector night",
            "jellyfish lamp lava",
            "plasma ball small",
            "fiber optic lamp color"
        ]
    },

    "🎪 Retro Mini Arcade": {
        "searches": [
            "mini arcade machine retro",
            "tiny pinball machine desk",
            "mini basketball game desktop",
            "small pacman arcade",
            "retro game console mini",
            "finger arcade game small",
            "mini claw arcade keychain",
            "pocket game machine retro",
            "tabletop arcade tiny",
            "mini tetris game handheld"
        ]
    },

    "🐙 Yaratık & Canavar Figürler": {
        "searches": [
            "monster blind box figure",
            "creature collectible small",
            "kaiju figure gashapon",
            "alien figure small toy",
            "cryptid figure collection",
            "monster hunter figure small",
            "yokai figure japanese",
            "lovecraft creature figure",
            "deep sea creature figure",
            "mutant figure blind box"
        ]
    },

    "🎨 Transforming & Şekil Değiştiren": {
        "searches": [
            "transforming cube puzzle",
            "shape shifting box toy",
            "magnetic blocks transform",
            "rubik snake puzzle",
            "infinity cube transform",
            "fidget cube transformer",
            "changeable magnetic cube",
            "morphing ball toy",
            "geometric transform toy",
            "magic snake cube"
        ]
    },

    "🌸 Kawaii & Japon Tarzı": {
        "searches": [
            "sanrio gashapon figure",
            "kuromi blind box small",
            "cinnamoroll figure mini",
            "sumikko gurashi figure",
            "rilakkuma capsule toy",
            "gudetama figure small",
            "pompompurin gashapon",
            "my melody figure mini",
            "japanese capsule toy cute",
            "kawaii desk figure small"
        ]
    },

    "🏰 Disney & Karakter Sürpriz": {
        "searches": [
            "disney doorables mini",
            "stitch blind box figure",
            "disney tsum tsum small",
            "pixar mystery mini",
            "marvel micro figure blind",
            "disney animator mini",
            "funko mystery mini disney",
            "disney villain small figure",
            "princess capsule figure",
            "toy story mini blind"
        ]
    },

    "🔧 Mekanik & Steampunk": {
        "searches": [
            "steampunk desk toy metal",
            "mechanical insect model",
            "clockwork toy vintage",
            "metal puzzle 3d mechanical",
            "steam engine model small",
            "gear cube puzzle metal",
            "mechanical spider model",
            "steampunk music box",
            "wind up metal toy",
            "mechanical bird automaton"
        ]
    },

    "🎲 Benzersiz Zar & Oyun": {
        "searches": [
            "unusual dice set unique",
            "liquid core dice",
            "sharp edge dice resin",
            "mini board game travel",
            "dice tower small",
            "metal dice premium",
            "glow dark dice set",
            "gemstone dice real",
            "spinner dice fidget",
            "fortune telling dice"
        ]
    },

    "🌿 Canlı Gibi & Simülasyon": {
        "searches": [
            "realistic food miniature",
            "fake food keychain japan",
            "simulation food toy",
            "miniature food blind box",
            "squishy realistic slow",
            "fake dessert display",
            "food sample replica",
            "mini cooking real tiny",
            "realistic fruit squishy",
            "fake sushi display"
        ]
    },

    "🎵 Müzik Kutusu & Melodi": {
        "searches": [
            "music box mechanism small",
            "hand crank music box",
            "crystal ball music box",
            "custom music box diy",
            "wooden music box vintage",
            "carousel music box mini",
            "snow globe music box",
            "piano music box small",
            "music box movement custom",
            "orgel music box japanese"
        ]
    }
}

# --- ARAMA FONKSİYONLARI ---
def multi_platform_search(search_terms, max_results=12, max_retries=3):
    """Birden fazla platformda arama yap"""
    all_results = []

    # Rastgele 3-4 platform seç
    selected_platforms = random.sample(PLATFORMS, min(4, len(PLATFORMS)))

    # Rastgele 2-3 arama terimi seç
    selected_terms = random.sample(search_terms, min(3, len(search_terms)))

    for term in selected_terms:
        # Her terim için rastgele bir platform
        platform = random.choice(selected_platforms)
        query = f"{platform} {term}"

        results = search_with_retry(query, max_results=5, max_retries=max_retries)

        for r in results:
            r['platform'] = platform.replace('site:', '').replace('.com', '')
            r['search_term'] = term

        all_results.extend(results)

        # Rate limiting önlemi
        time.sleep(0.5)

    # Genel arama da ekle (site filtresi olmadan)
    general_term = random.choice(search_terms)
    general_results = search_with_retry(general_term, max_results=4, max_retries=max_retries)
    for r in general_results:
        r['platform'] = 'web'
        r['search_term'] = general_term
    all_results.extend(general_results)

    # Karıştır ve benzersiz yap
    seen_urls = set()
    unique_results = []
    random.shuffle(all_results)

    for r in all_results:
        if r['image'] not in seen_urls:
            seen_urls.add(r['image'])
            unique_results.append(r)
            if len(unique_results) >= max_results:
                break

    return unique_results

def search_with_retry(query, max_results=8, max_retries=3):
    """Retry logic ile arama"""
    results = []
    last_error = None

    for attempt in range(max_retries):
        try:
            if attempt > 0:
                time.sleep(2 ** attempt)

            ddgs = DDGS(timeout=20)
            images = list(ddgs.images(query, max_results=max_results + 5, safesearch='off'))

            if images:
                if len(images) > max_results:
                    images = random.sample(images, max_results)

                for img in images:
                    image_url = img.get("image", "")
                    if image_url:
                        results.append({
                            "id": hash(image_url) % 100000,
                            "title": img.get("title", "Ürün"),
                            "image": image_url,
                            "url": img.get("url", ""),
                            "source": img.get("source", ""),
                            "query": query
                        })

                if results:
                    return results

        except Exception as e:
            last_error = str(e)
            if attempt < max_retries - 1:
                continue

    return results

def generate_platform_links(query):
    """Platform linkleri oluştur"""
    en = urllib.parse.quote(query)

    return {
        "aliexpress": f"https://www.aliexpress.com/wholesale?SearchText={en}",
        "alibaba": f"https://www.alibaba.com/trade/search?SearchText={en}",
        "amazon": f"https://www.amazon.com/s?k={en}",
        "ebay": f"https://www.ebay.com/sch/i.html?_nkw={en}",
        "etsy": f"https://www.etsy.com/search?q={en}",
        "dhgate": f"https://www.dhgate.com/wholesale/search.do?searchkey={en}"
    }

# --- TASARIM ---
st.markdown("""
<style>
    .stApp { background: #0a0a0f; }

    .header-box {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 2px solid #00d4ff;
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
        text-align: center;
    }

    .product-card {
        background: linear-gradient(145deg, #1a1a2e, #16213e);
        border: 1px solid #0f3460;
        border-radius: 16px;
        padding: 0;
        margin: 10px 0;
        overflow: hidden;
        transition: all 0.3s;
    }
    .product-card:hover {
        border-color: #00d4ff;
        transform: translateY(-5px);
    }

    .platform-tag {
        display: inline-block;
        background: #00d4ff;
        color: black;
        padding: 3px 8px;
        border-radius: 10px;
        font-size: 10px;
        font-weight: bold;
        margin: 5px 0;
    }

    .stats-box {
        background: rgba(0, 212, 255, 0.1);
        border: 1px solid #00d4ff;
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
    }

    .category-btn {
        background: linear-gradient(90deg, #667eea, #764ba2);
        border: none;
        padding: 10px 20px;
        border-radius: 25px;
        color: white;
        font-weight: 600;
    }

    .learned-tag {
        display: inline-block;
        background: #00b894;
        color: white;
        padding: 5px 12px;
        border-radius: 15px;
        margin: 3px;
        font-size: 12px;
    }
    .negative-tag {
        display: inline-block;
        background: #e94560;
        color: white;
        padding: 5px 12px;
        border-radius: 15px;
        margin: 3px;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## 🎯 Arama Ayarları")

    # Kategori seçimi
    selected_category = st.selectbox(
        "📂 Kategori Seç",
        options=list(INTERESTING_CATEGORIES.keys())
    )

    st.markdown("---")

    # İstatistikler
    stats = get_preference_stats()
    st.markdown(f"""
    <div class="stats-box">
        <h4 style="color:#00d4ff; margin:0;">📊 Öğrenme Durumu</h4>
        <p style="color:#ccc; margin:10px 0;">
            ❤️ Beğenilen: <strong>{stats['total_likes']}</strong><br>
            👎 Beğenilmeyen: <strong>{stats['total_dislikes']}</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)

    if stats['top_positive']:
        st.markdown("**✅ Sevdiğin:**")
        for word, count in stats['top_positive']:
            st.markdown(f'<span class="learned-tag">{word}</span>', unsafe_allow_html=True)

    if stats['top_negative']:
        st.markdown("**❌ Sevmediğin:**")
        for word, count in stats['top_negative']:
            st.markdown(f'<span class="negative-tag">{word}</span>', unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Temizle"):
            st.session_state.products = []
            st.rerun()
    with col2:
        if st.button("🔄 Sıfırla"):
            save_json(LIKES_FILE, [])
            save_json(DISLIKES_FILE, [])
            save_learned_keywords({"positive": {}, "negative": {}, "patterns": []})
            st.rerun()

# --- ANA SAYFA ---
st.markdown("""
<div class="header-box">
    <h1 style="color:#00d4ff; margin:0;">🎯 İLGİNÇ ÜRÜN AVCISI</h1>
    <p style="color:#ccc; margin-top:10px;">
        Multi-platform arama • Benzersiz ürünler • Öğrenen sistem
    </p>
</div>
""", unsafe_allow_html=True)

# Seçili kategori bilgisi
st.info(f"🔍 **{selected_category}** kategorisinde {len(INTERESTING_CATEGORIES[selected_category]['searches'])} farklı arama terimi ile taranacak")

# --- ARAMA BUTONLARI ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    search_clicked = st.button("🚀 ÜRÜN ARA", type="primary", use_container_width=True)

if search_clicked:
    with st.spinner("🔍 Platformlar taranıyor..."):
        category_data = INTERESTING_CATEGORIES[selected_category]
        results = multi_platform_search(category_data['searches'], max_results=12)

        for r in results:
            r['category'] = selected_category

        st.session_state.products = results
        st.session_state.search_count += 1

        if results:
            st.success(f"✅ {len(results)} ilginç ürün bulundu!")
        else:
            st.warning("⚠️ Sonuç bulunamadı. Tekrar deneyin.")

# Hızlı platform linkleri
if st.session_state.products:
    sample_query = random.choice(INTERESTING_CATEGORIES[selected_category]['searches'])
    links = generate_platform_links(sample_query)

    st.markdown("### 🌐 Direkt Platform Araması:")
    link_cols = st.columns(6)
    platforms_display = [
        ("AliExpress", links["aliexpress"], "#ff4747"),
        ("Alibaba", links["alibaba"], "#ff6a00"),
        ("Amazon", links["amazon"], "#ff9900"),
        ("eBay", links["ebay"], "#0064d2"),
        ("Etsy", links["etsy"], "#f56400"),
        ("DHgate", links["dhgate"], "#ff5722")
    ]

    for i, (name, url, color) in enumerate(platforms_display):
        with link_cols[i]:
            st.markdown(f'<a href="{url}" target="_blank" style="background:{color}; color:white; padding:8px 15px; border-radius:20px; text-decoration:none; font-weight:bold; font-size:12px;">{name}</a>', unsafe_allow_html=True)

# --- ÜRÜN KARTLARI ---
if st.session_state.products:
    st.markdown("---")
    st.markdown(f"### 🎁 Bulunan Ürünler ({len(st.session_state.products)})")
    st.caption("Beğendiğine ❤️, beğenmediğine 👎 tıkla - sistem öğrenecek!")

    cols = st.columns(3)

    for idx, product in enumerate(st.session_state.products):
        with cols[idx % 3]:
            # Platform etiketi
            platform = product.get('platform', 'web')
            st.markdown(f'<span class="platform-tag">{platform.upper()}</span>', unsafe_allow_html=True)

            # Görsel
            if product.get('image'):
                try:
                    st.image(product['image'], use_container_width=True)
                except:
                    st.markdown("🖼️ Görsel yüklenemedi")

            # Başlık
            title = product.get('title', '')[:80]
            st.markdown(f"**{title}**" if title else "**Ürün**")

            # Butonlar
            btn_col1, btn_col2, btn_col3 = st.columns(3)

            with btn_col1:
                if st.button("❤️", key=f"like_{idx}_{product.get('id', idx)}"):
                    count = like_product(product)
                    st.toast(f"Beğenildi! ({count})")
                    st.rerun()

            with btn_col2:
                if st.button("👎", key=f"dislike_{idx}_{product.get('id', idx)}"):
                    count = dislike_product(product)
                    st.toast(f"Kaydedildi!")
                    st.rerun()

            with btn_col3:
                if product.get('url'):
                    st.markdown(f'<a href="{product["url"]}" target="_blank">🔗</a>', unsafe_allow_html=True)

            st.markdown("---")

    # Daha fazla yükle
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 DAHA FAZLA ÜRÜN GETİR", use_container_width=True):
        with st.spinner("Yeni ürünler aranıyor..."):
            time.sleep(1)
            category_data = INTERESTING_CATEGORIES[selected_category]
            new_results = multi_platform_search(category_data['searches'], max_results=9)

            if new_results:
                for r in new_results:
                    r['category'] = selected_category
                st.session_state.products.extend(new_results)
                st.success(f"✅ {len(new_results)} yeni ürün eklendi!")
            st.rerun()

else:
    st.markdown("""
    <div style="text-align:center; padding:50px; color:#888;">
        <h2>🎯 Nasıl Çalışır?</h2>
        <p style="font-size:18px;">1. Kategori seç</p>
        <p style="font-size:18px;">2. "ÜRÜN ARA" butonuna tıkla</p>
        <p style="font-size:18px;">3. Birden fazla platform aynı anda taranır</p>
        <p style="font-size:18px;">4. Beğendiklerine ❤️ tıkla, sistem öğrensin!</p>
        <br>
        <p style="color:#00d4ff; font-size:16px;">
            🚀 AliExpress, Alibaba, Amazon, eBay, Etsy, DHgate<br>
            hepsi tek seferde taranıyor!
        </p>
    </div>
    """, unsafe_allow_html=True)

# --- BEĞENİLENLER ---
st.markdown("---")
with st.expander("❤️ Beğendiğin Ürünler"):
    liked = load_json(LIKES_FILE)
    if liked:
        like_cols = st.columns(4)
        for i, item in enumerate(liked[-12:]):
            with like_cols[i % 4]:
                if item.get('image'):
                    try:
                        st.image(item['image'], use_container_width=True)
                    except:
                        pass
                st.caption(item.get('title', '')[:40])
    else:
        st.info("Henüz beğenilen ürün yok.")

# --- FOOTER ---
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#555; padding:20px;">
    <p>🎯 İlginç Ürün Avcısı v7.0</p>
    <p style="font-size:12px;">Multi-platform • Akıllı arama • Öğrenen sistem</p>
</div>
""", unsafe_allow_html=True)
