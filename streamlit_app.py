# -*- coding: utf-8 -*-
# MOMO 商品搜尋分析儀表板 - 美化版 + 商品自選 + 關鍵字下拉
# 使用方式：streamlit run momo_streamlit_app.py

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import time
from datetime import datetime

# ══════════════════════════════════════════════════════════════
#  頁面基礎設定
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="MOMO 商品價格分析",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════
#  Session State 初始化
# ══════════════════════════════════════════════════════════════
if "selected_items" not in st.session_state:
    st.session_state.selected_items = set()
if "df_result" not in st.session_state:
    st.session_state.df_result = pd.DataFrame()
if "last_keyword" not in st.session_state:
    st.session_state.last_keyword = ""

# ══════════════════════════════════════════════════════════════
#  全域 CSS 樣式注入
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans TC', sans-serif;
}

/* ── 主背景 ── */
.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    min-height: 100vh;
}

/* ── 主標題 ── */
.main-header {
    background: linear-gradient(90deg, #e94560, #f5a623);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.6rem;
    font-weight: 700;
    text-align: center;
    padding: 0.5rem 0;
    letter-spacing: 2px;
}

.sub-header {
    text-align: center;
    color: rgba(255,255,255,0.55);
    font-size: 0.95rem;
    margin-top: -0.5rem;
    margin-bottom: 1.5rem;
    letter-spacing: 1px;
}

/* ── 分隔線 ── */
hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, #e94560, transparent);
    margin: 1.5rem 0;
}

/* ── Metric 卡片 ── */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 16px;
    padding: 1.2rem 1rem;
    backdrop-filter: blur(10px);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
[data-testid="metric-container"]:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 30px rgba(233,69,96,0.25);
    border-color: rgba(233,69,96,0.4);
}
[data-testid="metric-container"] label {
    color: rgba(255,255,255,0.65) !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #f5a623 !important;
    font-size: 1.8rem !important;
    font-weight: 700 !important;
}

/* ── 側邊欄 ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.08);
}
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #f5a623 !important;
}

/* ── 主要按鈕 ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #e94560, #f5a623) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.65rem 2.5rem !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(233,69,96,0.4) !important;
    width: 100%;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(233,69,96,0.6) !important;
}

/* ── 次要按鈕 ── */
.stButton > button[kind="secondary"] {
    background: rgba(255,255,255,0.06) !important;
    color: rgba(255,255,255,0.8) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 10px !important;
    transition: all 0.2s ease !important;
    width: 100%;
}
.stButton > button[kind="secondary"]:hover {
    background: rgba(255,255,255,0.12) !important;
    border-color: rgba(245,166,35,0.5) !important;
}

/* ── 下載按鈕 ── */
.stDownloadButton > button {
    background: rgba(255,255,255,0.08) !important;
    color: #f5a623 !important;
    border: 1px solid rgba(245,166,35,0.4) !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}
.stDownloadButton > button:hover {
    background: rgba(245,166,35,0.15) !important;
    border-color: #f5a623 !important;
}

/* ── 資料表格 ── */
[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.1) !important;
}

/* ── 圖表容器 ── */
.chart-container {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1rem 1.2rem;
    margin: 0.5rem 0;
}

/* ── 自選商品卡片 ── */
.selected-card {
    background: linear-gradient(135deg,
        rgba(233,69,96,0.12), rgba(245,166,35,0.12));
    border: 1px solid rgba(245,166,35,0.35);
    border-radius: 14px;
    padding: 0.9rem 1.1rem;
    margin: 0.4rem 0;
    transition: all 0.2s ease;
}
.selected-card:hover {
    border-color: #f5a623;
    box-shadow: 0 4px 16px rgba(245,166,35,0.2);
}
.selected-card .card-name {
    color: rgba(255,255,255,0.88);
    font-size: 0.85rem;
    line-height: 1.4;
    margin-bottom: 0.3rem;
}
.selected-card .card-price {
    color: #f5a623;
    font-size: 1.15rem;
    font-weight: 700;
}
.selected-card .card-meta {
    color: rgba(255,255,255,0.4);
    font-size: 0.75rem;
    margin-top: 0.2rem;
}

/* ── Badge ── */
.stat-badge {
    display: inline-block;
    background: linear-gradient(135deg,
        rgba(233,69,96,0.2), rgba(245,166,35,0.2));
    border: 1px solid rgba(245,166,35,0.3);
    border-radius: 20px;
    padding: 2px 12px;
    font-size: 0.78rem;
    color: #f5a623;
    margin: 2px;
}

/* ── 空狀態 ── */
.empty-state {
    text-align: center;
    padding: 4rem 2rem;
    color: rgba(255,255,255,0.35);
}
.empty-state .icon { font-size: 4rem; margin-bottom: 1rem; }
.empty-state p { font-size: 1.1rem; }

/* ── Progress bar ── */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #e94560, #f5a623) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.04);
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    color: rgba(255,255,255,0.6) !important;
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #e94560, #f5a623) !important;
    color: white !important;
}

/* ── Slider ── */
.stSlider > div > div > div > div {
    background: linear-gradient(90deg, #e94560, #f5a623) !important;
}

/* ── 關鍵字確認標籤 ── */
.keyword-confirm {
    background: rgba(245,166,35,0.1);
    border: 1px solid rgba(245,166,35,0.3);
    border-radius: 8px;
    padding: 6px 12px;
    margin-top: 4px;
    font-size: 0.82rem;
    color: rgba(255,255,255,0.5);
}
.keyword-confirm b {
    color: #f5a623;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  Plotly 統一主題
# ══════════════════════════════════════════════════════════════
PLOTLY_TEMPLATE = "plotly_dark"
COLOR_PRIMARY   = "#e94560"
COLOR_SECONDARY = "#f5a623"
COLOR_PALETTE   = [
    "#e94560", "#f5a623", "#00d4ff", "#7b2ff7",
    "#00c896", "#ff6b9d", "#c9d6ff", "#ffecd2",
]

def apply_chart_style(fig, title="", height=480):
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title=dict(
            text=title,
            font=dict(size=16, color="#f5a623", family="Noto Sans TC"),
            x=0.02,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.02)",
        font=dict(color="rgba(255,255,255,0.75)", family="Noto Sans TC"),
        height=height,
        margin=dict(l=20, r=20, t=60, b=20),
        legend=dict(
            bgcolor="rgba(255,255,255,0.05)",
            bordercolor="rgba(255,255,255,0.1)",
            borderwidth=1,
        ),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.06)",
                     zerolinecolor="rgba(255,255,255,0.1)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.06)",
                     zerolinecolor="rgba(255,255,255,0.1)")
    return fig

# ══════════════════════════════════════════════════════════════
#  主標題
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="main-header">🛒 MOMO 商品價格分析儀表板</div>',
            unsafe_allow_html=True)
st.markdown('<div class="sub-header">即時爬取 · 智慧分析 · 商品自選比較</div>',
            unsafe_allow_html=True)
st.markdown("---")

# ══════════════════════════════════════════════════════════════
#  側邊欄
# ══════════════════════════════════════════════════════════════

# ── 預設關鍵字清單 ────────────────────────────────────────────
PRESET_KEYWORDS = [
    "✏️ 自行輸入…",
    "🎧 耳機",
    "💻 筆電",
    "🖱 滑鼠",
    "⌨️ 鍵盤",
    "📱 手機",
    "📷 相機",
    "🖥 螢幕",
    "🎮 遊戲手把",
    "📦 行動電源",
    "🔊 藍牙喇叭",
    "⌚ 智慧手錶",
    "🧹 掃地機器人",
    "❄️ 空氣清淨機",
    "🖨 印表機",
    "📡 路由器",
    "🎙 麥克風",
    "💡 智慧燈泡",
]

with st.sidebar:
    st.markdown("## 🔎 搜尋設定")

    # ── ① 下拉選單 ──────────────────────────────────────────
    selected_preset = st.selectbox(
        "選擇商品類別",
        options=PRESET_KEYWORDS,
        index=1,                      # 預設選「耳機」
        help="選擇預設類別，或選「自行輸入」填寫關鍵字",
    )

    # ── ② 依選擇決定 keyword ────────────────────────────────
    if selected_preset == "✏️ 自行輸入…":
        # 顯示文字輸入框
        keyword = st.text_input(
            "請輸入關鍵字",
            placeholder="例如：空氣炸鍋、電競椅…",
            key="custom_keyword",
        ).strip()
        if not keyword:
            st.markdown(
                '<div class="keyword-confirm">⚠️ 請輸入搜尋關鍵字</div>',
                unsafe_allow_html=True,
            )
    else:
        # 去掉 emoji 前綴，取純中文關鍵字
        keyword = selected_preset.split(" ", 1)[-1].strip()
        st.markdown(
            f'<div class="keyword-confirm">🔑 搜尋關鍵字：<b>{keyword}</b></div>',
            unsafe_allow_html=True,
        )

    # ── ③ 抓取筆數 ──────────────────────────────────────────
    max_items = st.slider(
        "抓取筆數", 10, 200, 50, step=10,
        help="建議 50~100 筆",
    )

    st.markdown("---")
    st.markdown("## 📊 圖表選項")
    show_line_chart = st.checkbox("💹 價格趨勢折線圖", value=True)
    show_bar_chart  = st.checkbox("📊 品牌商品數長條圖", value=True)
    show_pie_chart  = st.checkbox("🥧 價格區間圓餅圖", value=True)
    show_sunburst   = st.checkbox("☀️ 品牌旭日圖", value=True)
    show_box_plot   = st.checkbox("📦 品牌價格箱型圖", value=True)
    show_scatter    = st.checkbox("🔵 價格散佈圖", value=True)

    st.markdown("---")

    # ── 自選清單摘要 ─────────────────────────────────────────
    n_sel = len(st.session_state.selected_items)
    st.markdown(
        f"## 🧺 自選清單 &nbsp;"
        f"<span style='background:linear-gradient(135deg,#e94560,#f5a623);"
        f"color:white;border-radius:50%;padding:1px 7px;font-size:0.8rem;'>"
        f"{n_sel}</span>",
        unsafe_allow_html=True,
    )

    if n_sel == 0:
        st.markdown(
            '<p style="color:rgba(255,255,255,0.3);font-size:0.82rem;">尚未選取任何商品</p>',
            unsafe_allow_html=True,
        )
    else:
        df_now = st.session_state.df_result
        if not df_now.empty:
            sel_df_side = df_now.loc[df_now.index.isin(st.session_state.selected_items)]
            st.markdown(
                f'<p style="color:rgba(255,255,255,0.5);font-size:0.78rem;">'
                f'已選 {n_sel} 件 ｜ 合計 ${sel_df_side["價格"].sum():,}</p>',
                unsafe_allow_html=True,
            )
            for _, row in sel_df_side.head(5).iterrows():
                name_short = row["品名"][:22] + "…" if len(row["品名"]) > 22 else row["品名"]
                st.markdown(f"""
                <div style="background:rgba(245,166,35,0.08);border-left:2px solid #f5a623;
                            border-radius:6px;padding:5px 8px;margin:3px 0;">
                    <span style="color:rgba(255,255,255,0.75);font-size:0.78rem;">{name_short}</span><br>
                    <span style="color:#f5a623;font-weight:700;font-size:0.88rem;">${row['價格']:,}</span>
                </div>""", unsafe_allow_html=True)
            if n_sel > 5:
                st.markdown(
                    f'<p style="color:rgba(255,255,255,0.3);font-size:0.75rem;'
                    f'text-align:center;">…還有 {n_sel-5} 件</p>',
                    unsafe_allow_html=True,
                )

        if st.button("🗑 清空自選清單", type="secondary"):
            st.session_state.selected_items = set()
            st.rerun()

    st.markdown("---")
    search_btn = st.button("🔍 開始搜尋", type="primary")
    st.markdown("""
    <div style="color:rgba(255,255,255,0.3);font-size:0.75rem;
                line-height:1.8;margin-top:0.5rem;">
    📌 資料來源：MOMO 購物<br>
    ⏱ 快取時間：5 分鐘<br>
    ⚠️ 請勿頻繁大量抓取
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  爬蟲函數
# ══════════════════════════════════════════════════════════════
@st.cache_data(ttl=300)
def fetch_momo_data(keyword: str, max_items: int) -> pd.DataFrame:
    url = "https://apisearch.momoshop.com.tw/momoSearchCloud/moec/textSearch"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/127.0.0.0 Safari/537.36"
        )
    }
    all_products: list[dict] = []
    page = 1
    progress_bar = st.progress(0, text="準備中…")
    status_text  = st.empty()

    while len(all_products) < max_items:
        payload = {
            "host": "momoshop", "flag": "searchEngine",
            "data": {
                "specialGoodsType": "", "isBrandSeriesPage": "false",
                "authorNo": "", "originalCateCode": "", "cateType": "",
                "searchValue": keyword, "cateCode": "", "cateLevel": "-1",
                "cp":"N","NAM":"N","first":"N","freeze":"N","superstore":"N",
                "tvshop":"N","china":"N","tomorrow":"N","stockYN":"N",
                "prefere":"N","threeHours":"N","video":"N","cycle":"N",
                "cod":"N","superstorePay":"N","showType":"chessboardType",
                "curPage": str(page), "priceS":"0","priceE":"9999999",
                "searchType":"1","reduceKeyword":"","isFuzzy":"0",
                "rtnCateDatainfo": {
                    "cateCode":"","cateLv":"-1","keyword":keyword,
                    "curPage":str(page),"historyDoPush":"false",
                    "timestamp": int(time.time()*1000),
                },
                "flag":2018,"serviceCode":"MT01",
                "addressSearchData":{},"adSource":"tenmax",
            },
        }
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=10)
            if resp.status_code == 200:
                data     = resp.json()
                products = data.get("rtnSearchData",{}).get("goodsInfoList",[])
                if not products:
                    break
                for p in products:
                    if len(all_products) >= max_items:
                        break
                    name      = p.get("goodsName","")
                    price_str = p.get("goodsPrice","0")
                    try:
                        price = int(price_str.replace("$","").replace(",",""))
                        all_products.append({"品名":name,"價格":price,"頁面":page})
                    except ValueError:
                        continue
                pct = min(len(all_products)/max_items, 1.0)
                progress_bar.progress(pct,
                    text=f"⏳ 已抓取 {len(all_products)}/{max_items} 筆…")
                status_text.markdown(
                    f'<span class="stat-badge">第 {page} 頁</span>'
                    f'<span class="stat-badge">共 {len(all_products)} 筆</span>',
                    unsafe_allow_html=True)
                page += 1
                time.sleep(0.5)
            else:
                st.error(f"❌ 請求失敗，狀態碼：{resp.status_code}")
                break
        except Exception as e:
            st.error(f"❌ 抓取時發生錯誤：{e}")
            break

    progress_bar.empty()
    status_text.empty()
    return pd.DataFrame(all_products)

# ══════════════════════════════════════════════════════════════
#  輔助函數
# ══════════════════════════════════════════════════════════════
PRICE_BINS   = [0, 500, 1000, 2000, 5000, float("inf")]
PRICE_LABELS = ["超值區 <500","經濟區 500-1000","中價區 1000-2000",
                "高價區 2000-5000","頂級區 >5000"]

def categorize_price(price):
    for i, upper in enumerate(PRICE_BINS[1:]):
        if price < upper:
            return PRICE_LABELS[i]
    return PRICE_LABELS[-1]

COMMON_BRANDS = [
    "Apple","Sony","Samsung","Xiaomi","ASUS","Acer","HP","Lenovo",
    "Dell","MSI","Razer","Logitech","JBL","Beats","Bose",
    "Sennheiser","Audio-Technica","Jabra","Anker","Philips","Panasonic",
]

def extract_brand(name):
    upper = name.upper()
    for b in COMMON_BRANDS:
        if b.upper() in upper:
            return b
    return "其他品牌"

def analyze_data(df):
    return {
        "總商品數":   len(df),
        "平均價格":   df["價格"].mean(),
        "最高價格":   df["價格"].max(),
        "最低價格":   df["價格"].min(),
        "價格標準差": df["價格"].std(),
        "中位數價格": df["價格"].median(),
    }

# ══════════════════════════════════════════════════════════════
#  自選比較面板
# ══════════════════════════════════════════════════════════════
def render_compare_panel(df: pd.DataFrame):
    sel_idx = st.session_state.selected_items
    if not sel_idx:
        return

    sel_df = df.loc[df.index.isin(sel_idx)].copy().reset_index(drop=True)
    n = len(sel_df)

    st.markdown("---")
    st.markdown(f"""
    <div style="background:linear-gradient(90deg,rgba(233,69,96,0.15),rgba(245,166,35,0.15));
                border:1px solid rgba(245,166,35,0.35);border-radius:14px;
                padding:1rem 1.5rem;margin-bottom:1rem;">
        <span style="font-size:1.3rem;font-weight:700;color:#f5a623;">
            🧺 自選商品比較面板
        </span>
        <span style="color:rgba(255,255,255,0.5);font-size:0.85rem;margin-left:1rem;">
            已選 {n} 件商品
        </span>
    </div>
    """, unsafe_allow_html=True)

    ca, cb, cc, cd = st.columns(4)
    with ca: st.metric("已選件數", f"{n} 件")
    with cb: st.metric("最低價", f"${sel_df['價格'].min():,}")
    with cc: st.metric("最高價", f"${sel_df['價格'].max():,}")
    with cd: st.metric("平均價", f"${sel_df['價格'].mean():,.0f}")

    st.markdown("#### 📌 已選商品清單")
    cols_per_row = 3
    rows = [sel_df.iloc[i:i+cols_per_row] for i in range(0, len(sel_df), cols_per_row)]

    for row_df in rows:
        cols = st.columns(cols_per_row)
        for col, (_, item) in zip(cols, row_df.iterrows()):
            with col:
                name_short = item["品名"][:40] + "…" if len(item["品名"]) > 40 else item["品名"]
                diff = item["價格"] - sel_df["價格"].mean()
                diff_str = (
                    f'<span style="color:#00c896;">▼ ${abs(diff):,.0f} 低於均價</span>'
                    if diff < 0 else
                    f'<span style="color:#e94560;">▲ ${diff:,.0f} 高於均價</span>'
                )
                st.markdown(f"""
                <div class="selected-card">
                    <div class="card-name">{name_short}</div>
                    <div class="card-price">${item['價格']:,}</div>
                    <div class="card-meta">🏷 {item['品牌']} &nbsp;|&nbsp; {item['價格區間']}</div>
                    <div style="font-size:0.75rem;margin-top:0.3rem;">{diff_str}</div>
                </div>""", unsafe_allow_html=True)

    st.markdown("#### 📊 自選商品圖表比較")
    tab1, tab2, tab3 = st.tabs(["📊 橫向長條圖", "🔵 散佈比較", "📋 數據表"])

    with tab1:
        sel_df["品名短"] = sel_df["品名"].str[:25] + "…"
        sel_df_sorted   = sel_df.sort_values("價格", ascending=True)
        avg_all         = df["價格"].mean()
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            y=sel_df_sorted["品名短"], x=sel_df_sorted["價格"],
            orientation="h",
            marker=dict(
                color=sel_df_sorted["價格"],
                colorscale=[[0, COLOR_PRIMARY],[1, COLOR_SECONDARY]],
                showscale=True, colorbar=dict(title="價格"),
            ),
            text=[f"${p:,}" for p in sel_df_sorted["價格"]],
            textposition="outside", textfont=dict(color="white"),
        ))
        fig_bar.add_vline(
            x=avg_all, line_dash="dash", line_color=COLOR_SECONDARY,
            annotation_text=f"全體均價 ${avg_all:,.0f}",
            annotation_font_color=COLOR_SECONDARY,
        )
        apply_chart_style(fig_bar, "自選商品價格比較", height=max(300, n*55+80))
        fig_bar.update_xaxes(title_text="價格 (NT$)")
        st.plotly_chart(fig_bar, use_container_width=True)

    with tab2:
        fig_sc = go.Figure()
        fig_sc.add_trace(go.Scatter(
            x=list(range(len(df))), y=df["價格"],
            mode="markers", name="全體商品",
            marker=dict(color="rgba(255,255,255,0.12)", size=5),
            hoverinfo="skip",
        ))
        fig_sc.add_trace(go.Scatter(
            x=sel_df.index.tolist(), y=sel_df["價格"],
            mode="markers+text", name="自選商品",
            marker=dict(color=COLOR_SECONDARY, size=14,
                        line=dict(color=COLOR_PRIMARY, width=2), symbol="star"),
            text=[f"${p:,}" for p in sel_df["價格"]],
            textposition="top center",
            textfont=dict(color=COLOR_SECONDARY, size=10),
            hovertemplate="<b>%{customdata}</b><br>價格：$%{y:,}<extra></extra>",
            customdata=sel_df["品名"].str[:20],
        ))
        apply_chart_style(fig_sc, "自選商品在全體中的位置", height=420)
        fig_sc.update_xaxes(title_text="商品序號")
        fig_sc.update_yaxes(title_text="價格 (NT$)")
        st.plotly_chart(fig_sc, use_container_width=True)

    with tab3:
        show_cols = ["品名","價格","品牌","價格區間"]
        display   = sel_df[show_cols].copy()
        display.index = range(1, len(display)+1)
        st.dataframe(display, use_container_width=True)
        csv_sel = sel_df[show_cols].to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label=f"📥 下載自選清單 CSV（{n} 筆）",
            data=csv_sel,
            file_name=f"MOMO_自選_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
        )

# ══════════════════════════════════════════════════════════════
#  商品自選列表
# ══════════════════════════════════════════════════════════════
def render_item_selector(df: pd.DataFrame, keyword: str):
    st.markdown("## 🧺 商品自選")
    st.markdown(
        '<p style="color:rgba(255,255,255,0.5);font-size:0.88rem;margin-top:-0.5rem;">'
        '勾選感興趣的商品，即時加入比較清單 👇</p>',
        unsafe_allow_html=True,
    )

    fc1, fc2, fc3, fc4 = st.columns([2, 2, 1, 1])
    with fc1:
        brand_options = ["全部品牌"] + sorted(df["品牌"].unique().tolist())
        filter_brand  = st.selectbox("篩選品牌", brand_options, key="filter_brand")
    with fc2:
        range_options = ["全部區間"] + PRICE_LABELS
        filter_range  = st.selectbox("篩選價格區間", range_options, key="filter_range")
    with fc3:
        price_min = int(df["價格"].min())
        price_max = int(df["價格"].max())
        filter_price = st.slider(
            "價格範圍", min_value=price_min, max_value=price_max,
            value=(price_min, price_max), key="filter_price",
        )
    with fc4:
        sort_by = st.selectbox("排序方式",
                               ["預設順序","價格由低到高","價格由高到低"],
                               key="sort_by")

    mask = pd.Series([True]*len(df), index=df.index)
    if filter_brand != "全部品牌":
        mask &= df["品牌"] == filter_brand
    if filter_range != "全部區間":
        mask &= df["價格區間"] == filter_range
    mask &= (df["價格"] >= filter_price[0]) & (df["價格"] <= filter_price[1])

    filtered_df = df[mask].copy()
    if sort_by == "價格由低到高":
        filtered_df = filtered_df.sort_values("價格", ascending=True)
    elif sort_by == "價格由高到低":
        filtered_df = filtered_df.sort_values("價格", ascending=False)

    ba, bb, bc = st.columns([1, 1, 4])
    with ba:
        if st.button("✅ 全選（篩選結果）", type="secondary"):
            for idx in filtered_df.index:
                st.session_state.selected_items.add(idx)
            st.rerun()
    with bb:
        if st.button("❌ 取消全選", type="secondary"):
            for idx in filtered_df.index:
                st.session_state.selected_items.discard(idx)
            st.rerun()
    with bc:
        st.markdown(
            f'<p style="color:rgba(255,255,255,0.4);font-size:0.82rem;padding-top:0.6rem;">'
            f'篩選結果：{len(filtered_df)} 件 ｜ 已選：{len(st.session_state.selected_items)} 件</p>',
            unsafe_allow_html=True,
        )

    PAGE_SIZE   = 20
    total_pages = max(1, (len(filtered_df)-1)//PAGE_SIZE+1)

    if f"page_{keyword}" not in st.session_state:
        st.session_state[f"page_{keyword}"] = 1
    current_page = st.session_state[f"page_{keyword}"]

    pa, pb, pc = st.columns([1, 3, 1])
    with pa:
        if st.button("◀ 上一頁", type="secondary", disabled=(current_page<=1)):
            st.session_state[f"page_{keyword}"] -= 1
            st.rerun()
    with pb:
        st.markdown(
            f'<p style="text-align:center;color:rgba(255,255,255,0.5);">'
            f'第 {current_page} / {total_pages} 頁</p>',
            unsafe_allow_html=True,
        )
    with pc:
        if st.button("下一頁 ▶", type="secondary", disabled=(current_page>=total_pages)):
            st.session_state[f"page_{keyword}"] += 1
            st.rerun()

    start   = (current_page-1)*PAGE_SIZE
    page_df = filtered_df.iloc[start:start+PAGE_SIZE]

    for idx, row in page_df.iterrows():
        is_selected = idx in st.session_state.selected_items
        col_chk, col_info, col_price, col_badge = st.columns([0.5, 5, 1.5, 1.5])

        with col_chk:
            checked = st.checkbox("", value=is_selected,
                                  key=f"chk_{idx}", label_visibility="collapsed")
            if checked != is_selected:
                if checked:
                    st.session_state.selected_items.add(idx)
                else:
                    st.session_state.selected_items.discard(idx)
                st.rerun()

        with col_info:
            name_display = row["品名"][:55]+"…" if len(row["品名"])>55 else row["品名"]
            highlight = (
                "border-left:3px solid #f5a623;background:rgba(245,166,35,0.06);"
                if is_selected else ""
            )
            st.markdown(
                f'<div style="padding:6px 10px;border-radius:6px;{highlight}">'
                f'<span style="color:rgba(255,255,255,0.85);font-size:0.87rem;">'
                f'{name_display}</span></div>',
                unsafe_allow_html=True,
            )

        with col_price:
            price_color = "#00c896" if row["價格"] < df["價格"].mean() else "#e94560"
            st.markdown(
                f'<div style="text-align:right;padding:6px 4px;">'
                f'<span style="color:{price_color};font-weight:700;font-size:1rem;">'
                f'${row["價格"]:,}</span></div>',
                unsafe_allow_html=True,
            )

        with col_badge:
            st.markdown(
                f'<div style="text-align:center;padding:6px 0;">'
                f'<span class="stat-badge">{row["品牌"]}</span></div>',
                unsafe_allow_html=True,
            )

    st.markdown("---")

# ══════════════════════════════════════════════════════════════
#  主邏輯
# ══════════════════════════════════════════════════════════════
if search_btn:
    if not keyword:
        st.warning("⚠️ 請輸入或選擇搜尋關鍵字。")
        st.stop()

    if keyword != st.session_state.last_keyword:
        st.session_state.selected_items = set()
        st.session_state.last_keyword   = keyword

    with st.spinner("🔄 正在連線 MOMO 並抓取資料，請稍候…"):
        df = fetch_momo_data(keyword, max_items)

    if df.empty:
        st.markdown("""
        <div class="empty-state">
            <div class="icon">🔍</div>
            <p>未找到相關商品，請嘗試其他關鍵字。</p>
        </div>""", unsafe_allow_html=True)
        st.stop()

    df["價格區間"] = df["價格"].apply(categorize_price)
    df["品牌"]    = df["品名"].apply(extract_brand)
    analysis      = analyze_data(df)
    st.session_state.df_result = df

    # ── 統計指標 ──────────────────────────────────────────
    st.markdown("## 📈 基本統計")
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    for col, (label, value) in zip(
        [c1,c2,c3,c4,c5,c6],
        [
            ("🛍 總商品數",  f"{analysis['總商品數']:,}"),
            ("💰 平均價格",  f"${analysis['平均價格']:,.0f}"),
            ("📈 最高價格",  f"${analysis['最高價格']:,}"),
            ("📉 最低價格",  f"${analysis['最低價格']:,}"),
            ("📊 中位數",    f"${analysis['中位數價格']:,.0f}"),
            ("📐 標準差",    f"${analysis['價格標準差']:,.0f}"),
        ],
    ):
        with col:
            st.metric(label, value)

    st.markdown("---")

    render_item_selector(df, keyword)
    render_compare_panel(df)

    # ── 資料表格 ──────────────────────────────────────────
    st.markdown("---")
    st.markdown("## 📋 商品資料一覽")
    tab_t1, tab_t2 = st.tabs(["🗂 精簡檢視（前 30 筆）", "📄 完整資料"])
    with tab_t1:
        d = df[["品名","價格","價格區間","品牌","頁面"]].head(30).copy()
        d.index = range(1, len(d)+1)
        st.dataframe(d, use_container_width=True, height=380)
    with tab_t2:
        st.dataframe(df, use_container_width=True, height=380)

    csv_all = df.to_csv(index=False, encoding="utf-8-sig")
    st.download_button(
        label=f"📥 下載完整資料 CSV（{len(df)} 筆）",
        data=csv_all,
        file_name=f"MOMO_{keyword}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
    )

    st.markdown("---")

    # ── 視覺化圖表 ────────────────────────────────────────
    st.markdown("## 📊 全體資料視覺化")

    if show_line_chart:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("### 💹 價格趨勢折線圖")
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=list(range(1, len(df)+1)), y=df["價格"],
            mode="lines+markers", name="商品價格",
            line=dict(color=COLOR_PRIMARY, width=2),
            marker=dict(size=4, color=COLOR_PRIMARY),
            fill="tozeroy", fillcolor="rgba(233,69,96,0.08)",
        ))
        sel_df_line = df.loc[df.index.isin(st.session_state.selected_items)]
        if not sel_df_line.empty:
            fig_line.add_trace(go.Scatter(
                x=[i+1 for i in sel_df_line.index], y=sel_df_line["價格"],
                mode="markers", name="⭐ 自選商品",
                marker=dict(color=COLOR_SECONDARY, size=12, symbol="star",
                            line=dict(color="white", width=1)),
            ))
        avg = analysis["平均價格"]
        fig_line.add_hline(
            y=avg, line_dash="dash", line_color=COLOR_SECONDARY,
            annotation_text=f"平均 ${avg:,.0f}",
            annotation_font_color=COLOR_SECONDARY,
            annotation_position="top right",
        )
        apply_chart_style(fig_line, f"《{keyword}》商品價格趨勢", height=420)
        fig_line.update_xaxes(title_text="商品序號")
        fig_line.update_yaxes(title_text="價格 (NT$)")
        st.plotly_chart(fig_line, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if show_bar_chart:
        brand_counts = (
            df.groupby("品牌")["價格"]
            .agg(數量="count", 平均價格="mean")
            .reset_index().sort_values("數量", ascending=False)
        )
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("### 🏷️ 品牌商品數量排行")
        fig_bar2 = px.bar(
            brand_counts, x="品牌", y="數量", color="平均價格",
            color_continuous_scale=[[0, COLOR_PRIMARY],[1, COLOR_SECONDARY]],
            text="數量",
        )
        fig_bar2.update_traces(textposition="outside", textfont_color="white")
        apply_chart_style(fig_bar2, f"《{keyword}》品牌商品數量", height=420)
        st.plotly_chart(fig_bar2, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if show_pie_chart or show_sunburst:
        cols = st.columns(2) if (show_pie_chart and show_sunburst) else [st.container()]
        if show_pie_chart:
            with (cols[0] if len(cols)==2 else cols[0]):
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown("### 🥧 價格區間分布")
                pc_data = df["價格區間"].value_counts()
                fig_pie = px.pie(values=pc_data.values, names=pc_data.index,
                                 color_discrete_sequence=COLOR_PALETTE, hole=0.38)
                fig_pie.update_traces(textposition="inside",
                                      textinfo="percent+label", textfont_size=11)
                apply_chart_style(fig_pie, f"《{keyword}》價格區間", height=440)
                st.plotly_chart(fig_pie, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
        if show_sunburst:
            with (cols[1] if len(cols)==2 else cols[0]):
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown("### ☀️ 品牌 × 價格區間旭日圖")
                sb = df.groupby(["品牌","價格區間"]).size().reset_index(name="數量")
                fig_sb = px.sunburst(sb, path=["品牌","價格區間"], values="數量",
                                     color_discrete_sequence=COLOR_PALETTE)
                apply_chart_style(fig_sb, f"《{keyword}》品牌分布", height=440)
                st.plotly_chart(fig_sb, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

    if show_box_plot:
        top_brands = df["品牌"].value_counts().head(8).index.tolist()
        df_box     = df[df["品牌"].isin(top_brands)]
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("### 📦 品牌價格箱型圖（Top 8）")
        fig_box = px.box(df_box, x="品牌", y="價格", color="品牌",
                         color_discrete_sequence=COLOR_PALETTE, points="outliers")
        apply_chart_style(fig_box, f"《{keyword}》品牌價格箱型圖", height=440)
        fig_box.update_yaxes(title_text="價格 (NT$)")
        st.plotly_chart(fig_box, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if show_scatter:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("### 🔵 商品價格散佈圖")
        fig_sc2 = px.scatter(
            df, x=df.index, y="價格", color="品牌",
            hover_data=["品名","價格","品牌","價格區間"],
            color_discrete_sequence=COLOR_PALETTE,
        )
        sel_sc = df.loc[df.index.isin(st.session_state.selected_items)]
        if not sel_sc.empty:
            fig_sc2.add_trace(go.Scatter(
                x=sel_sc.index.tolist(), y=sel_sc["價格"],
                mode="markers", name="⭐ 自選商品",
                marker=dict(color=COLOR_SECONDARY, size=14, symbol="star",
                            line=dict(color="white", width=1.5)),
                hovertemplate="<b>%{customdata}</b><br>$%{y:,}<extra></extra>",
                customdata=sel_sc["品名"].str[:20],
            ))
        avg = analysis["平均價格"]
        fig_sc2.add_hline(y=avg, line_dash="dot", line_color=COLOR_SECONDARY,
                          annotation_text=f"平均 ${avg:,.0f}",
                          annotation_font_color=COLOR_SECONDARY)
        apply_chart_style(fig_sc2, f"《{keyword}》散佈圖", height=440)
        fig_sc2.update_xaxes(title_text="商品序號")
        fig_sc2.update_yaxes(title_text="價格 (NT$)")
        st.plotly_chart(fig_sc2, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── 深度分析 ──────────────────────────────────────────
    st.markdown("---")
    st.markdown("## 🔍 深度分析")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### 🏷️ 品牌統計")
        bt = (df.groupby("品牌")["價格"]
              .agg(商品數量="count", 平均價格="mean", 最低="min", 最高="max")
              .round(0).sort_values("商品數量", ascending=False))
        st.dataframe(bt, use_container_width=True)
    with col_b:
        st.markdown("### 💰 價格區間統計")
        rt = (df.groupby("價格區間")["價格"]
              .agg(商品數量="count", 平均價格="mean")
              .round(0).sort_values("商品數量", ascending=False))
        st.dataframe(rt, use_container_width=True)

    st.markdown("### 📊 價格分布直方圖")
    fig_hist = px.histogram(df, x="價格", nbins=35,
                            color_discrete_sequence=[COLOR_PRIMARY])
    fig_hist.update_traces(marker_line_color="rgba(255,255,255,0.2)",
                           marker_line_width=0.5)
    apply_chart_style(fig_hist, f"《{keyword}》價格分布", height=380)
    fig_hist.update_xaxes(title_text="價格 (NT$)")
    fig_hist.update_yaxes(title_text="商品數量")
    st.plotly_chart(fig_hist, use_container_width=True)

# ── 初始空狀態 ────────────────────────────────────────────────
else:
    if not st.session_state.df_result.empty:
        df = st.session_state.df_result
        render_item_selector(df, st.session_state.last_keyword)
        render_compare_panel(df)
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="icon">🛒</div>
            <p>在左側選擇類別或輸入關鍵字，點擊「開始搜尋」即可查看分析結果</p>
            <br>
            <p style="font-size:0.85rem;color:rgba(255,255,255,0.25);">
                支援：耳機 · 筆電 · 滑鼠 · 鍵盤 · 手機 · 平板 · 相機…
            </p>
        </div>""", unsafe_allow_html=True)

# ── 頁尾 ──────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:rgba(255,255,255,0.25);
            font-size:0.78rem;padding:0.5rem 0 1rem;">
    📦 資料來源：MOMO 購物網站 &nbsp;|&nbsp;
    ⏱ 快取 5 分鐘 &nbsp;|&nbsp;
    🛠 Built with Streamlit + Plotly
</div>""", unsafe_allow_html=True)
