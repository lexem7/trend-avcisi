import streamlit as st
from duckduckgo_search import DDGS
import random
import time
import urllib.parse
import json
import os
from datetime import datetime
from collections import Counter
import re

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="Akıllı Ürün Avcısı",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- VERİTABANI DOSYALARI ---
LIKES_FILE = "liked_products.json"
DISLIKES_FILE = "disliked_products.json"
LEARNED_KEYWORDS_FILE = "learned_keywords.json"
SEARCH_HISTORY_FILE = "search_history.json"

# --- SESSION STATE ---
if 'products' not in st.session_state:
    st.session_state.products = []
if 'search_count' not in st.session_state:
    st.session_state.search_count = 0
if 'learned_terms' not in st.session_state:
    st.session_state.learned_terms = []

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
    """Ürünü beğen ve öğren"""
    likes = load_json(LIKES_FILE)

    # Ürünü kaydet
    product['liked_at'] = datetime.now().isoformat()
    likes.append(product)
    save_json(LIKES_FILE, likes)

    # Anahtar kelimeleri öğren
    learn_from_product(product, positive=True)

    return len(likes)

def dislike_product(product):
    """Ürünü beğenme ve öğren"""
    dislikes = load_json(DISLIKES_FILE)

    product['disliked_at'] = datetime.now().isoformat()
    dislikes.append(product)
    save_json(DISLIKES_FILE, dislikes)

    # Negatif öğrenme
    learn_from_product(product, positive=False)

    return len(dislikes)

def learn_from_product(product, positive=True):
    """Üründen anahtar kelimeler öğren"""
    keywords = load_learned_keywords()

    # Başlıktan kelimeler çıkar
    title = product.get('title', '').lower()

    # Önemli kelimeleri çıkar (2+ karakter, sayı değil)
    words = re.findall(r'\b[a-zA-Z\u4e00-\u9fff]{2,}\b', title)

    # Stop words (filtrelenecek)
    stop_words = {'the', 'and', 'for', 'with', 'new', 'hot', 'sale', 'free', 'shipping',
                  'pcs', 'set', 'buy', 'get', 'off', 'best', 'top', 'good', 'great',
                  'item', 'product', 'quality', 'high', 'low', 'price', 'cheap'}

    target = "positive" if positive else "negative"

    for word in words:
        if word.lower() not in stop_words and len(word) > 2:
            if word not in keywords[target]:
                keywords[target][word] = 0
            keywords[target][word] += 1

    # Kategori pattern'i kaydet
    if product.get('category') and positive:
        if product['category'] not in keywords['patterns']:
            keywords['patterns'].append(product['category'])

    save_learned_keywords(keywords)

def get_smart_search_terms():
    """Öğrenilen tercihlerden akıllı arama terimleri üret"""
    keywords = load_learned_keywords()

    # En çok beğenilen kelimeler
    positive = keywords.get('positive', {})
    negative = keywords.get('negative', {})

    # Pozitif - Negatif skor hesapla
    scores = {}
    for word, count in positive.items():
        scores[word] = count
    for word, count in negative.items():
        if word in scores:
            scores[word] -= count * 2  # Negatif daha ağır
        else:
            scores[word] = -count * 2

    # En yüksek skorlu kelimeleri al
    sorted_words = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_words = [w for w, s in sorted_words[:10] if s > 0]

    return top_words

def get_preference_stats():
    """Tercih istatistiklerini getir"""
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

# --- ARAMA KATEGORİLERİ ---
SEARCH_CATEGORIES = {
    "🎰 Mini Otomat/Gashapon": {
        "base_terms": [
            "mini gashapon machine", "capsule vending machine toy",
            "desktop candy machine", "mini claw machine",
            "gachapon dispenser", "egg machine toy"
        ],
        "chinese": ["迷你扭蛋机", "桌面糖果机", "抓娃娃机"],
        "tags": ["gashapon", "vending", "machine", "capsule", "dispenser"]
    },

    "🌊 Reçine/Epoksi Sanat": {
        "base_terms": [
            "resin diorama cube", "epoxy ocean art",
            "resin whale lamp", "underwater resin",
            "titanic resin", "deep sea diorama"
        ],
        "chinese": ["树脂摆件", "海洋水晶", "环氧树脂"],
        "tags": ["resin", "epoxy", "diorama", "ocean", "cube", "lamp"]
    },

    "🎭 Karakter Figür (Stitch/Disney/Sanrio)": {
        "base_terms": [
            "stitch blind box", "disney mystery figure",
            "sanrio surprise", "kuromi gashapon",
            "hello kitty mystery", "cinnamoroll figure"
        ],
        "chinese": ["迪士尼盲盒", "三丽鸥扭蛋", "史迪仔手办"],
        "tags": ["stitch", "disney", "sanrio", "kuromi", "hello kitty", "blind box"]
    },

    "📱 Telefon Aksesuarı Figür": {
        "base_terms": [
            "phone hippers figure", "screen decoration toy",
            "cable bite protector", "phone holder figure",
            "phone charm cute", "dust plug figure"
        ],
        "chinese": ["手机挂件", "屏幕摆件", "数据线保护"],
        "tags": ["phone", "hippers", "screen", "cable", "holder"]
    },

    "🧲 Manyetik/Levitasyon": {
        "base_terms": [
            "magnetic levitation display", "floating globe",
            "levitating moon lamp", "magnetic desk toy",
            "anti gravity display", "floating plant pot"
        ],
        "chinese": ["磁悬浮", "悬浮地球仪", "磁力摆件"],
        "tags": ["magnetic", "levitation", "floating", "anti gravity"]
    },

    "💡 LED/Işıklı Oyuncak": {
        "base_terms": [
            "LED blind box", "glow surprise toy",
            "light up figure", "neon desk toy",
            "luminous mystery box", "glowing decoration"
        ],
        "chinese": ["发光盲盒", "LED玩具", "夜光摆件"],
        "tags": ["led", "glow", "light", "neon", "luminous"]
    },

    "🎪 Arcade/Eğlence Makinesi": {
        "base_terms": [
            "mini arcade machine", "desktop pinball",
            "mini basketball game", "finger game toy",
            "retro game console mini", "tabletop arcade"
        ],
        "chinese": ["迷你游戏机", "桌面弹珠", "复古街机"],
        "tags": ["arcade", "game", "pinball", "retro", "mini"]
    },

    "🌀 Kinetik/Hareket Oyuncak": {
        "base_terms": [
            "kinetic desk toy", "perpetual motion toy",
            "newton cradle", "spinning top metal",
            "gyroscope toy", "fidget kinetic"
        ],
        "chinese": ["永动机摆件", "动能玩具", "陀螺仪"],
        "tags": ["kinetic", "motion", "spinning", "gyroscope", "perpetual"]
    },

    "🎁 Mekanik Sürpriz Kutu": {
        "base_terms": [
            "mechanical surprise box", "pop up gift box",
            "explosion box diy", "spring loaded box",
            "puzzle box secret", "magic trick box"
        ],
        "chinese": ["机关礼盒", "弹出惊喜盒", "魔术盒"],
        "tags": ["mechanical", "surprise", "pop up", "spring", "puzzle"]
    },

    "🦑 Yaratık/Canavar Figür": {
        "base_terms": [
            "monster blind box", "creature figure",
            "alien toy figure", "cryptid figure",
            "kaiju toy small", "monster gashapon"
        ],
        "chinese": ["怪兽盲盒", "异形手办", "怪物扭蛋"],
        "tags": ["monster", "creature", "alien", "kaiju", "cryptid"]
    },

    "🎨 DIY/Montaj Oyuncak": {
        "base_terms": [
            "diy assembly toy", "build your own figure",
            "mechanical puzzle 3d", "wooden puzzle toy",
            "construction toy mini", "model kit small"
        ],
        "chinese": ["DIY拼装", "3D拼图", "木质模型"],
        "tags": ["diy", "assembly", "puzzle", "build", "model", "kit"]
    },

    "🔮 Sihirli/İllüzyon": {
        "base_terms": [
            "magic trick toy", "illusion toy desk",
            "hologram display small", "infinity mirror toy",
            "optical illusion toy", "magic cube puzzle"
        ],
        "chinese": ["魔术玩具", "全息投影", "无限镜"],
        "tags": ["magic", "illusion", "hologram", "infinity", "optical"]
    }
}

# --- ARAMA FONKSİYONLARI ---
def smart_search(category, use_learning=True):
    """Akıllı arama - öğrenilen tercihlerle zenginleştirilmiş"""
    cat_data = SEARCH_CATEGORIES[category]
    base_term = random.choice(cat_data["base_terms"])

    # Öğrenilen terimleri ekle
    if use_learning:
        learned = get_smart_search_terms()
        # Kategori tag'leriyle eşleşen öğrenilmiş terimler
        matching_learned = [w for w in learned if any(tag in w.lower() for tag in cat_data["tags"])]
        if matching_learned:
            base_term = f"{base_term} {random.choice(matching_learned)}"

    # Çeşitlilik ekle
    variations = ["2024", "new", "creative", "unique", "trending", "popular", "cute", "mini", "desktop"]
    final_query = f"{base_term} {random.choice(variations)}"

    return final_query, random.choice(cat_data["chinese"])

def search_products(query, max_results=8, max_retries=3):
    """DuckDuckGo ile ürün ara - retry logic ile"""
    results = []
    last_error = None

    for attempt in range(max_retries):
        try:
            # Her denemede küçük bir gecikme
            if attempt > 0:
                delay = 2 ** attempt  # Exponential backoff: 2, 4, 8 saniye
                time.sleep(delay)

            # DDGS instance'ı timeout ile oluştur
            ddgs = DDGS(timeout=20)

            # Arama yap
            images = list(ddgs.images(
                query,
                max_results=max_results + 5,
                safesearch='off'
            ))

            # Başarılı - sonuçları işle
            if images:
                # Rastgele seç
                if len(images) > max_results:
                    images = random.sample(images, max_results)

                for img in images:
                    image_url = img.get("image", "")
                    if image_url:  # Sadece geçerli görselleri ekle
                        results.append({
                            "id": hash(image_url) % 100000,
                            "title": img.get("title", "Ürün"),
                            "image": image_url,
                            "url": img.get("url", ""),
                            "source": img.get("source", ""),
                            "query": query
                        })

                if results:
                    return results  # Başarılı, sonuçları döndür

            # Sonuç yoksa farklı sorgu dene
            if not results and attempt < max_retries - 1:
                # Sorguyu basitleştir
                query_words = query.split()
                if len(query_words) > 2:
                    query = ' '.join(query_words[:3])
                continue

        except Exception as e:
            last_error = str(e)
            # Rate limiting veya bağlantı hatası durumunda bekle ve tekrar dene
            if attempt < max_retries - 1:
                continue

    # Tüm denemeler başarısız oldu
    if last_error:
        error_msg = last_error[:100] if len(last_error) > 100 else last_error
        if "ratelimit" in last_error.lower():
            st.warning("⏳ Çok fazla arama yapıldı. Lütfen 30 saniye bekleyin.")
        elif "timeout" in last_error.lower():
            st.warning("⌛ Bağlantı zaman aşımına uğradı. Tekrar deneyin.")
        else:
            st.warning(f"⚠️ Arama hatası: {error_msg}")
    else:
        st.info("🔍 Bu arama için sonuç bulunamadı. Farklı kategori deneyin.")

    return results

def generate_platform_links(query_en, query_cn):
    """Platform linkleri"""
    cn = urllib.parse.quote(query_cn)
    en = urllib.parse.quote(query_en)

    return {
        "1688": f"https://s.1688.com/selloffer/offer_search.htm?keywords={cn}",
        "taobao": f"https://s.taobao.com/search?q={cn}",
        "xhs": f"https://www.xiaohongshu.com/search_result?keyword={cn}",
        "douyin": f"https://www.douyin.com/search/{cn}",
        "alibaba": f"https://www.alibaba.com/trade/search?SearchText={en}",
        "google": f"https://www.google.com/search?q={en}&tbm=isch"
    }

# --- TASARIM ---
st.markdown("""
<style>
    .stApp { background: #0a0a0f; }

    .header-box {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 2px solid #e94560;
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
        border-color: #e94560;
        transform: translateY(-5px);
    }
    .product-card img {
        width: 100%;
        height: 200px;
        object-fit: cover;
    }
    .product-info {
        padding: 15px;
    }

    .like-btn {
        background: linear-gradient(90deg, #00b894, #00cec9);
        color: white;
        border: none;
        padding: 8px 20px;
        border-radius: 20px;
        cursor: pointer;
        font-weight: 600;
    }
    .dislike-btn {
        background: linear-gradient(90deg, #e94560, #ff6b6b);
        color: white;
        border: none;
        padding: 8px 20px;
        border-radius: 20px;
        cursor: pointer;
        font-weight: 600;
    }

    .stats-box {
        background: rgba(233, 69, 96, 0.1);
        border: 1px solid #e94560;
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
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

    .platform-btn {
        display: inline-block;
        padding: 5px 10px;
        margin: 3px;
        border-radius: 8px;
        text-decoration: none;
        font-size: 11px;
        font-weight: 600;
    }
    .p-1688 { background: #ff6600; color: white; }
    .p-taobao { background: #ff5000; color: white; }
    .p-xhs { background: #ff2442; color: white; }
    .p-alibaba { background: #ff6a00; color: white; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## 🧠 Akıllı Tercih Sistemi")

    # İstatistikler
    stats = get_preference_stats()

    st.markdown(f"""
    <div class="stats-box">
        <h4 style="color:#e94560; margin:0;">📊 Öğrenme Durumu</h4>
        <p style="color:#ccc; margin:10px 0;">
            ❤️ Beğenilen: <strong>{stats['total_likes']}</strong><br>
            👎 Beğenilmeyen: <strong>{stats['total_dislikes']}</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Öğrenilen pozitif kelimeler
    if stats['top_positive']:
        st.markdown("**✅ Sevdiğin Özellikler:**")
        for word, count in stats['top_positive']:
            st.markdown(f'<span class="learned-tag">{word} ({count})</span>', unsafe_allow_html=True)

    # Öğrenilen negatif kelimeler
    if stats['top_negative']:
        st.markdown("**❌ Sevmediğin Özellikler:**")
        for word, count in stats['top_negative']:
            st.markdown(f'<span class="negative-tag">{word} ({count})</span>', unsafe_allow_html=True)

    st.markdown("---")

    # Kategori seçimi
    selected_category = st.selectbox(
        "🎯 Kategori",
        options=list(SEARCH_CATEGORIES.keys())
    )

    use_learning = st.checkbox("🧠 Öğrenilmiş tercihleri kullan", value=True)

    st.markdown("---")

    # Sıfırlama
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Aramayı Sıfırla"):
            st.session_state.products = []
    with col2:
        if st.button("🔄 Öğrenmeyi Sıfırla"):
            save_json(LIKES_FILE, [])
            save_json(DISLIKES_FILE, [])
            save_learned_keywords({"positive": {}, "negative": {}, "patterns": []})
            st.rerun()

# --- ANA SAYFA ---
st.markdown("""
<div class="header-box">
    <h1 style="color:#e94560; margin:0;">🧠 AKILLI ÜRÜN AVCISI</h1>
    <p style="color:#ccc; margin-top:10px;">
        Beğendikçe öğrenen, sana özel ürünler bulan sistem
    </p>
</div>
""", unsafe_allow_html=True)

# Öğrenme durumu göster
learned_terms = get_smart_search_terms()
if learned_terms:
    st.info(f"🧠 Öğrenilen tercihler: {', '.join(learned_terms[:5])}")

# --- ARAMA ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🔍 ÜRÜN ARA", type="primary", use_container_width=True):
        with st.spinner("Akıllı arama yapılıyor..."):
            query_en, query_cn = smart_search(selected_category, use_learning)

            st.session_state.current_query_en = query_en
            st.session_state.current_query_cn = query_cn

            results = search_products(query_en, max_results=9)

            for r in results:
                r['category'] = selected_category

            st.session_state.products = results
            st.session_state.search_count += 1

# Platform linkleri
if hasattr(st.session_state, 'current_query_en'):
    links = generate_platform_links(
        st.session_state.get('current_query_en', ''),
        st.session_state.get('current_query_cn', '')
    )

    st.markdown("### 🌏 Çin Platformlarında Ara:")
    link_cols = st.columns(6)
    with link_cols[0]:
        st.markdown(f'<a href="{links["1688"]}" target="_blank" class="platform-btn p-1688">🏭 1688</a>', unsafe_allow_html=True)
    with link_cols[1]:
        st.markdown(f'<a href="{links["taobao"]}" target="_blank" class="platform-btn p-taobao">🛒 Taobao</a>', unsafe_allow_html=True)
    with link_cols[2]:
        st.markdown(f'<a href="{links["xhs"]}" target="_blank" class="platform-btn p-xhs">📕 小红书</a>', unsafe_allow_html=True)
    with link_cols[3]:
        st.markdown(f'<a href="{links["douyin"]}" target="_blank" class="platform-btn" style="background:#00f2ea; color:black;">🎵 抖音</a>', unsafe_allow_html=True)
    with link_cols[4]:
        st.markdown(f'<a href="{links["alibaba"]}" target="_blank" class="platform-btn p-alibaba">🌐 Alibaba</a>', unsafe_allow_html=True)
    with link_cols[5]:
        st.markdown(f'<a href="{links["google"]}" target="_blank" class="platform-btn" style="background:#4285f4; color:white;">🔍 Google</a>', unsafe_allow_html=True)

# --- ÜRÜN KARTLARI ---
if st.session_state.products:
    st.markdown("---")
    st.markdown(f"### 🎯 Bulunan Ürünler ({len(st.session_state.products)})")
    st.markdown("*Beğendiğin ürünlere ❤️, beğenmediklerine 👎 tıkla. Sistem öğrenecek!*")

    cols = st.columns(3)

    for idx, product in enumerate(st.session_state.products):
        with cols[idx % 3]:
            # Görsel
            if product.get('image'):
                st.image(product['image'], use_container_width=True)

            # Başlık
            st.markdown(f"**{product.get('title', '')[:60]}...**")

            # Beğeni butonları
            btn_col1, btn_col2 = st.columns(2)

            with btn_col1:
                if st.button("❤️ Beğen", key=f"like_{idx}_{product.get('id', idx)}"):
                    count = like_product(product)
                    st.success(f"Beğenildi! (Toplam: {count})")
                    st.rerun()

            with btn_col2:
                if st.button("👎 Beğenme", key=f"dislike_{idx}_{product.get('id', idx)}"):
                    count = dislike_product(product)
                    st.warning(f"Kaydedildi! (Toplam: {count})")
                    st.rerun()

            st.markdown("---")

    # Daha fazla yükle
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 DAHA FAZLA ÜRÜN GETİR", use_container_width=True):
        with st.spinner("Yeni ürünler aranıyor..."):
            # Önceki aramadan beri biraz bekle
            time.sleep(1)
            query_en, query_cn = smart_search(selected_category, use_learning)
            new_results = search_products(query_en, max_results=6)
            if new_results:
                for r in new_results:
                    r['category'] = selected_category
                st.session_state.products.extend(new_results)
                st.success(f"✅ {len(new_results)} yeni ürün eklendi!")
            st.rerun()

else:
    st.markdown("""
    <div style="text-align:center; padding:50px; color:#888;">
        <h3>🧠 Nasıl Çalışır?</h3>
        <p>1. Kategori seç ve ara</p>
        <p>2. Beğendiğin ürünlere ❤️ tıkla</p>
        <p>3. Beğenmediklerine 👎 tıkla</p>
        <p>4. Sistem senin zevkini öğrenir!</p>
        <br>
        <p style="color:#e94560;">
            Ne kadar çok beğeni/beğenmeme yaparsan,<br>
            sistem o kadar akıllı olur!
        </p>
    </div>
    """, unsafe_allow_html=True)

# --- BEĞENİLEN ÜRÜNLER ---
st.markdown("---")
with st.expander("❤️ Beğendiğin Ürünleri Gör"):
    liked = load_json(LIKES_FILE)
    if liked:
        like_cols = st.columns(4)
        for i, item in enumerate(liked[-8:]):  # Son 8 beğeni
            with like_cols[i % 4]:
                if item.get('image'):
                    st.image(item['image'], use_container_width=True)
                st.caption(item.get('title', '')[:30])
    else:
        st.info("Henüz beğenilen ürün yok. Aramaya başla!")

# --- FOOTER ---
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#555; padding:20px;">
    <p>🧠 Akıllı Ürün Avcısı v6.1</p>
    <p style="font-size:12px;">Beğendikçe öğrenen, sana özel ürün bulan sistem</p>
    <p style="font-size:10px; color:#444;">Gelişmiş hata yönetimi ve retry sistemi ile</p>
</div>
""", unsafe_allow_html=True)
