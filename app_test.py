# ===================================================
# streamlit  %% app.py
# ===================================================
import os
import pandas as pd
import streamlit as st # 導入 Streamlit 函式庫，用於建構 Web 應用程式介面
from streamlit_folium import st_folium # 導入用於在 Streamlit 中嵌入 Folium 地圖的函式庫
import folium # 導入 Folium 函式庫，用於創建互動式地圖
from sqlalchemy import create_engine
from dotenv import load_dotenv
from rapidfuzz import fuzz, process # 導入 rapidfuzz 函式庫，用於高效的模糊字串匹配 (取代 fuzzywuzzy)
from streamlit.components.v1 import html


class streamlit_run_app:  
    def __init__(self):
        self.databasename = os.getenv('databasename')
        self.DATABASE_URL = os.getenv('DATABASE_URL')
        self.config_ttile = '展覽雷達：雙北展覽空間與文化趨勢地圖_Demo'
        self.SQLQUERY = f'SELECT * from {self.databasename};' # 定義 SQL 查詢 (只選取正在展出的展覽)
        self.GOOGLEMAP = os.getenv('GOOGLE_MAPS_API_KEY')
        self.GOOGLEMAPID = os.getenv('GOOGLEMAPID')

    @st.cache_data(ttl = 600)
    # 使用 Streamlit 的快取機制，避免每次互動都重新查詢資料庫
    # ttl=600 表示每 600 秒 (10 分鐘) 才重新查詢一次資料庫
    def _connectsql_get_data(_self) -> pd.DataFrame:
        if not _self.DATABASE_URL:
            st.error('錯誤：DATABASE_URL 環境變數未設定，無法連線。')
            return pd.DataFrame()
        
        try:
            # 1. 建立 SQLAlchemy 引擎
            engine = create_engine(_self.DATABASE_URL)
            st.info('ℹ️ 資料庫連線引擎建立成功。')

            df = pd.read_sql_query(_self.SQLQUERY, engine) # 使用 Pandas 讀取數據

            return df

        except Exception as e:
            st.error(f'❌ 讀取 Supabase 資料失敗，錯誤訊息: {e}')
            st.caption(f'{e}')
            return pd.DataFrame()
        
    def _display_google_map(self, df: pd.DataFrame, map_height: int = 600) -> None:
            # 為了不中斷應用程式，我們使用 st.map 作為緊急備援
        if not df.empty and 'lat' in df.columns and 'lon' in df.columns:
            df_map_fallback = df.rename(columns={'lat': 'latitude', 'lon': 'longitude'})
            st.map(df_map_fallback)
        return
        
        # 準備數據：選取 lat, lon, title 欄位，並轉換為 JSON 格式
        # 假設您的 DataFrame 包含 'lat', 'lon' 和 'title' 欄位
        if df.empty or 'lat' not in df.columns or 'lon' not in df.columns or 'title' not in df.columns:
            st.warning("數據為空或缺少必要的 'lat', 'lon', 'title' 欄位，無法在地圖上顯示標記。")
            return

        points = df[['lat', 'lon', 'title']].to_dict('records')
        # 將 Python 列表轉換為 JavaScript 陣列字串
        points_json = str(points).replace("'", '"')

        # 計算地圖中心點 (所有點的平均值)
        center_lat = df['lat'].mean()
        center_lon = df['lon'].mean()

        # Google Maps 的 HTML 和 JavaScript 程式碼
        map_html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
            <meta charset="utf-8">
            <style>
                #map {{
                    height: 100%;
                }}
                html, body {{
                    height: 100%;
                    margin: 0;
                    padding: 0;
                }}
            </style>
        </head>
        <body>
            <div id="map"></div>
            <script>
                function initMap() {{
                    const centerPoint = {{ lat: {center_lat}, lng: {center_lon} }};
                    const map = new google.maps.Map(document.getElementById('map'), {{
                        zoom: 15, // 放大層級
                        center: centerPoint,
                        mapId: {self.GOOGLEMAPID}, 
                        tilt : 45
                    }});
                    // 創建資訊視窗 (InfoWindow)
                    const infoWindow = new google.maps.InfoWindow();

                    // 迴圈遍歷所有點位並添加標記
                    exhibitionPoints.forEach(point => {{
                        const marker = new google.maps.Marker({{
                            position: {{ lat: point.lat, lng: point.lon }},
                            map: map,
                            title: point.title
                        }});

                    // 添加點擊事件監聽器，點擊時顯示資訊視窗
                        marker.addListener("click", () => {{
                            // 修正：當 title 可能是 None 時顯示替代文字
                            const content = point.title || '無標題'; 
                            infoWindow.setContent(content);
                            infoWindow.open(map, marker);
                        }});
                    }});
                }}
            </script>
            <script async defer src="https://maps.googleapis.com/maps/api/js?key={self.GOOGLEMAP}&callback=initMap">
            </script>
        </body>
        </html>
        '''
        # 使用 Streamlit HTML 元件嵌入地圖
        html(map_html, height=map_height)
    

    # Streamlit 應用程式主體
    def website_design(self):
        st.set_page_config(layout = 'wide', page_icon = '📊', page_title = self.config_ttile) # 設定 Streamlit 頁面標題和圖示，並設定為寬模式布局
        st.markdown(f'# **測試資料庫讀取**')

        # 🎯 使用 st.spinner 包裹耗時的數據載入步驟
        with st.spinner('⏳ 正在從 Supabase 建立連線並讀取資料，請稍候...'): # 上下文管理器 (Context Manager)，用來在程式碼執行需要較長時間時，在螢幕上顯示一個旋轉的載入動畫（俗稱 Spinner）
            df_exhibitions = self._connectsql_get_data()

        if not df_exhibitions.empty:
            st.success(f'✅ 連線成功！共載入 {len(df_exhibitions)} 筆現正展出中的展覽數據。')
            
            # st.subheader('數據表預覽')
            # # 顯示 Streamlit Dataframe
            # st.dataframe(df_exhibitions, use_container_width = True, hide_index = True)

            # st.subheader('地圖預覽')
            st.markdown('#### 這是地圖區塊!!')
            # 重新命名欄位以符合 st.map 的要求
            st.subheader("📍 Google Maps 嵌入 (動態數據)")
            # df_map = df_exhibitions.rename(columns={'lat': 'latitude', 'lon': 'longitude'})
            # st.map(df_map)
            self._display_google_map(df = df_exhibitions)
            # --- 數據表預覽 ---
            st.subheader('數據表預覽')
            st.dataframe(df_exhibitions, use_container_width = True, hide_index = True)


        else:
            st.warning('資料庫連線失敗或沒有找到正在展出的展覽資料。請檢查錯誤訊息和連線字串。')

if __name__ == '__main__':
    load_dotenv() 
    app = streamlit_run_app()
    app.website_design()