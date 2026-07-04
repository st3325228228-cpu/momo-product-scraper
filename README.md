# MOMO Product Scraper

使用 Python 與 Streamlit 建立的 MOMO 商品資料擷取與價格分析儀表板。  
系統可依照商品關鍵字取得 MOMO 商品資料，並進行品牌辨識、價格統計、資料視覺化及自選商品比較。

## 專案功能

- 使用關鍵字搜尋 MOMO 商品
- 提供常用商品類別選單
- 自訂商品資料抓取數量
- 顯示商品名稱與價格
- 自動辨識常見商品品牌
- 商品價格區間分類
- 計算平均價格、最高價格與最低價格
- 計算中位數與價格標準差
- 品牌商品數量分析
- 商品價格分布分析
- 商品篩選與價格排序
- 自選商品比較清單
- 匯出自選商品 CSV
- 使用 Streamlit 建立互動式操作介面

## 資料處理流程

```text
輸入或選擇商品關鍵字
          ↓
呼叫 MOMO 商品搜尋 API
          ↓
取得商品名稱與價格資料
          ↓
使用 pandas 清洗資料
          ↓
辨識品牌與價格區間
          ↓
計算價格統計結果
          ↓
使用 Plotly 建立互動圖表
          ↓
使用 Streamlit 顯示結果
```

## 使用技術

- Python
- Streamlit
- requests
- pandas
- NumPy
- Plotly
- MOMO 商品搜尋 API
- 資料清洗
- 資料視覺化
- CSV 資料匯出

## 視覺化功能

- 商品價格趨勢折線圖
- 品牌商品數長條圖
- 價格區間圓餅圖
- 品牌與價格旭日圖
- 品牌價格箱型圖
- 商品價格散佈圖
- 自選商品橫向長條圖
- 自選商品價格位置比較

## 商品比較功能

使用者可以從搜尋結果中選取感興趣的商品，系統會顯示：

- 已選商品數量
- 最低價格
- 最高價格
- 平均價格
- 商品價格與全體平均價格差異
- 自選商品價格比較圖
- 自選商品資料表
- CSV 檔案下載

## 專案檔案

```text
momo-product-scraper/
├── requirements.txt
├── streamlit_app.py
└── README.md
```

## 執行方式

### 1. 下載專案

```bash
git clone https://github.com/st3325228228-cpu/momo-product-scraper.git
cd momo-product-scraper
```

### 2. 安裝套件

```bash
pip install -r requirements.txt
```

### 3. 啟動程式

```bash
streamlit run streamlit_app.py
```

## 線上展示

線上展示網址整理中。

## 專案目的

本專案用於練習及展示以下能力：

- Python 網路資料存取
- REST API 串接
- JSON 資料解析
- pandas 資料處理
- 商品價格分析
- Plotly 互動式圖表
- Streamlit Web App 開發
- Session State 狀態管理
- CSV 資料匯出
- 資料快取與例外處理

## 注意事項

- 商品資訊與價格應以 MOMO 官方網站顯示內容為準。
- MOMO API 或資料格式變動時，程式可能需要更新。
- 請避免短時間內大量或高頻率發送請求。
- 本專案僅供 Python、資料分析及 Web App 開發學習使用。

## 未來改進方向

- 增加商品歷史價格資料庫
- 加入商品價格變化通知
- 顯示商品網址與圖片
- 加入更多品牌辨識規則
- 支援 MOMO 與其他電商平台比較
- 加入 SQLite 或 PostgreSQL
- 建立定時資料蒐集功能
- 使用 Docker 建立部署環境
