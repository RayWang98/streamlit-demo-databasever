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
from rapidfuzz import fuzz, process # 導入 rapidfuzz 函式庫，用於高效的模糊字串匹配
from streamlit.components.v1 import html
import datetime as dt
import json
from rapidfuzz import fuzz, process # 導入 rapidfuzz 函式庫，用於高效的模糊字串匹配
from typing import Dict, List, Tuple # 資料格式定義
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from matplotlib import font_manager


class streamlit_run_app:  
    def __init__(self):
        self.databasename = os.getenv('databasename')
        self.databasename_tag = os.getenv('databasename_tag')
        self.DATABASE_URL = os.getenv('DATABASE_URL')
        self.SQLQUERY = f'select * from {self.databasename}'
        self.SQLQUERY_TAG = f'select * from {self.databasename_tag}'
        self.config_ttile = '展覽雷達：雙北展覽空間與文化趨勢地圖_Demo'
        self.GOOGLEMAP = os.getenv('GOOGLE_MAPS_API_KEY')
        self.GOOGLEMAPID = os.getenv('GOOGLEMAPID')
        self.sideprojectbrief = '''**:orange[「展覽雷達：雙北展覽空間與文化趨勢地圖」是一個結合數據工程、爬蟲與 GIS 視覺化的專案。]**  
            本專案透過自動化資料整合與自然語言分析，將分散的展覽資訊轉換為互動式文化地圖。  
            藉由地理、主題與時間的多維度觀察，讓數據成為理解城市文化生態的窗口，展現雙北豐富的創意與文化能量。'''
        self.topic = r'展覽雷達：雙北展覽空間與文化趨勢地圖'
        self.venue_image_urls = {
            '松山文創園區': 'https://www-ws.gov.taipei/001/Upload/686/relpic/45246/119026/a521ecda-6ee6-4b86-8d6e-5572f432df5a.jpg', # 替換為實際圖片URL
            '國立師大美術館': 'https://www.artmuse.ntnu.edu.tw/wp-content/uploads/2023/04/%E5%B8%AB%E5%A4%A7%E7%BE%8E%E8%A1%93%E9%A4%A8-03-1024x681.jpg',
            '台北當代藝術館': 'https://grace-520.com/wp-content/uploads/2025/03/%E5%8F%B0%E5%8C%97%E5%AE%A4%E5%85%A7%E6%99%AF%E9%BB%9E-%E5%8F%B0%E5%8C%97%E7%95%B6%E4%BB%A3%E7%BE%8E%E8%A1%93%E9%A4%A8-1.jpg',
            '華山1914文化創意園區': 'https://upload.wikimedia.org/wikipedia/commons/5/55/Huashan_1914%2C_Syntrend_and_Jinshan_e01_20150701.jpg',
            '國立故宮博物院': 'https://www.travel.taipei/content/images/attractions/221739/1920x1080_attractions-image-hrvtkvaowueb7-w8--qy9g.jpg',
            '富邦美術館': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Fubon_Art_Museum_20241127.jpg/1200px-Fubon_Art_Museum_20241127.jpg',
            '臺北市立美術館' : 'https://upload.wikimedia.org/wikipedia/commons/a/a4/Taipei_Fine_Arts_Museum_and_China_Eastern_aircraft_20120628.jpg',
            }
        self.venue_introduction = {
            '松山文創園區': '''松山文創園區自 2011 年開放，定位為「臺北市原創基地」，以培育原創人才與提升城市文創軟實力為目標。  
            園區透過跨界實驗、共好平台、創意學院等策略，支持創作者從設計發想、實驗製作到品牌建立與國際連結，打造台灣重要的創意樞紐，民眾可在此體驗藝術與原創精神。''',
            '國立師大美術館': '''師大美術館透過典藏研究與系列專題展覽，重現臺灣藝術發展史；辦理教育推廣與衍生活動，鼓勵創新教育與跨世代參與；  
            結合學術資源，連結國際姊妹校，推動跨國合作，打造面向世界的藝術樞紐。''',
            '台北當代藝術館': '''台北當代藝術館位於原臺北市政府舊廈，前身為日治時期建成小學。1996 年依古蹟再利用政策整建為當代藝術館，2001 年開館，採公辦民營模式經營，結合建成國中新校，成為國內首座以推廣當代藝術為宗旨的美術館。  
            館內展覽促進國際對話、提升民眾文化視野，亦帶動大同區再發展，成為臺北市重要的當代藝術與文化樞紐。''',
            '華山1914文化創意園區': '''華山1914文化創意產業園區位於臺北市中正區，前身為台北酒廠，為市定古蹟。  
            自1999年改建為藝文展演園區，提供藝術展覽、音樂表演及文化活動場地，成為臺北西區重要的文化聚落。園區內亦設有餐廳、咖啡館、藝廊及展廳等商業設施，兼具文化與休閒功能。''',
            '國立故宮博物院': '''國立故宮博物院，位於臺北士林，另設南部院區，是臺灣最具規模的博物館與漢學研究機構。  
            前身為北京故宮博物院，1948 年遷臺，1965 年於現址復院。館藏近 70 萬件文物，涵蓋新石器時代至今，包含青銅器、名家書畫、古籍與官窯瓷器。  
            展廳按文物類別編年展示，定期更換展品，並致力文化創意與數位博物館發展。''',
            '富邦美術館': '''富邦美術館位於臺北信義區，由富邦藝術基金會於 2015 年規劃設立，館址在富邦信義 A25 總部大樓下方。全館五層、佔地 3,000 坪，擁有「水景展廳」、「日光展廳」及「星光展廳」三個展覽空間，運用自然光設計及多媒體展覽。  
            開館首展與國際美術館合作，展出羅丹、常玉、朱沅芷及梵谷作品，並設有兒童工作坊與藝術商店，結合藝術展示與教育功能。''',
            '臺北市立美術館' : '''臺北市立美術館（北美館）位於中山區花博公園美術園區，成立於 1983 年，是臺灣首座公立與當代美術館。  
            自開館以來，北美館肩負保存、研究及推廣臺灣現當代藝術的使命，關注藝術發展並扶植人才，推動藝術教育與文化普及，提升全民審美、創造力與思辨能力，致力建構兼具全球視野與區域脈絡的當代藝術生態。''',
            }
        self.venue_hashtags = {
            '松山文創園區': '#文創基地 #設計展覽 #市集活動',
            '國立師大美術館': '#校園藝廊 #美術教育 #當代學術',
            '台北當代藝術館': '#MOCA #當代藝術 #議題探討',
            '華山1914文化創意園區': '#紅磚建築 #文化聚落 #展演空間',
            '國立故宮博物院': '#中華文物 #國寶級 #歷史典藏',
            '富邦美術館': '#企業收藏 #現代藝術 #信義區新館',
            '臺北市立美術館' : '#當代思辨 #經典建築'
            }
        if 'page_mode' not in st.session_state:
            st.session_state['page_mode'] = 'home' # 預設為首頁
        if 'selected' not in st.session_state:
            st.session_state['selected'] = 'None'

        # 讀取資料
        # 使用 st.spinner 包裹耗時的數據載入步驟
        with st.spinner('⏳ 正在建立連線並讀取資料，請稍候...'): # 上下文管理器 (Context Manager)，用來在程式碼執行需要較長時間時，在螢幕上顯示一個旋轉的載入動畫（俗稱 Spinner）
            df_exhibitions, df_tags = self._connectsql_get_data()
            df_exhibitions = self._translate_date(df_exhibitions)

            self.df_exhibitions = df_exhibitions
            self.df_tags = df_tags


    @st.cache_data(ttl = 600)
    # 使用 Streamlit 的快取機制，避免每次互動都重新查詢資料庫
    # ttl=600 表示每 600 秒 (10 分鐘) 才重新查詢一次資料庫
    def _connectsql_get_data(_self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        if not _self.DATABASE_URL:
            # st.error('錯誤：DATABASE_URL 環境變數未設定，無法連線。')
            return pd.DataFrame(), pd.DataFrame()
        
        try:
            # 1. 建立 SQLAlchemy 引擎
            engine = create_engine(_self.DATABASE_URL)
            # st.info('ℹ️ 資料庫連線引擎建立成功。')

            df = pd.read_sql_query(_self.SQLQUERY, engine) # 使用 Pandas 讀取數據
            # 確保坐標是 float 類型並移除 NaN 
            if 'lat' in df.columns and 'lon' in df.columns:
                df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
                df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
                df = df.dropna(subset=['lat', 'lon']) 
            
            df_tag = pd.read_sql_query(_self.SQLQUERY_TAG, engine)
            df_tag['update_flg'] = pd.to_datetime(df_tag['update_flg'])
            # df_tag['keywords'] = df_tag['keywords']


            return df, df_tag

        except Exception as e:
            # st.error(f'❌ 讀取 Supabase 資料失敗，錯誤訊息: {e}')
            st.caption(f'{e}')
            return pd.DataFrame(), pd.DataFrame()
        

    def _display_google_map(self, df: pd.DataFrame, venue_name : str, exhibition_name : str, map_height: int = 700) -> None:
        df_v = df[(df['展館名稱'] == venue_name) & (df['展覽名稱'] == exhibition_name)]
        if df_v.empty:
            st.warning(f'數據庫中找不到屬於 **{df_v}** 的展覽點位。無法顯示地圖。')
            return 
        
        
        # 準備數據：選取 lat, lon, title 欄位，並轉換為 JSON 格式
        point = df_v[['緯度', '經度', '展覽名稱', '圖片連結', '展覽地點']].to_dict('records')
        point_json = json.dumps(point) # 將 Python 列表轉換為 JavaScript 陣列字串

        # 計算地圖中心點 (所有點的平均值)
        center_lat = df_v['緯度'].mean()
        center_lon = df_v['經度'].mean()

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
                <div id="map"></div> // 後面的 JavaScript 中的 document.getElementById('map') 會引用這個 ID。

                <script> // 嵌入 JavaScript 代碼開始。

                    // 傳遞 Python 數據到 JavaScript
                    const exhibitionPoints = {point_json}; // 創建java物件

                    function initMap() {{ // 地圖初始化函式定義。 這是 Google Maps API 載入完成後會調用的入口函式。
                        // 設定地圖中心點。 使用 Python 傳入的中心經緯度。
                        const centerPoint = {{ lat: {center_lat}, lng: {center_lon} }}; 

                        // 1. 引用 google.maps.Map (API 載入)。 
                        // 2. 引用 document.getElementById('map') (HTML 容器)。 
                        // 3. 創建的 map 變數會被後續的 marker 和 infoWindow 引用。
                        const map = new google.maps.Map(document.getElementById('map'), {{ // 創建地圖主物件。
                            zoom: 18, // 放大層級
                            center: centerPoint,
                            mapId: "{self.GOOGLEMAPID}", 
                            tilt : 45
                        }});

                        // 創建資訊視窗物件 (InfoWindow)。 這是點擊標記時彈出的視窗物件。
                        const infoWindow = new google.maps.InfoWindow(); // 引用 google.maps.InfoWindow (API 載入)。創建的 infoWindow 變數會被後續的點擊監聽器引用。

                        // 迴圈遍歷所有點位並添加標記
                        // 遍歷所有展覽點位。 針對 exhibitionPoints 陣列中的每一個 point 執行內部函式。 引用 exhibitionPoints (Python 傳來的數據)。
                        exhibitionPoints.forEach(point => {{ 
                            const marker = new google.maps.Marker({{ // 引用 google.maps.Marker (API 載入)。創建的 marker 變數會被後續的點擊監聽器引用。
                                position: {{ lat: point.緯度, lng: point.經度}},
                                map: map, // 將標記添加到哪個地圖物件上。引用 map 變數 (第 141 列定義)。
                                title: point.展覽名稱 // 引用當前循環的 point 數據中的 title 屬性。
                            }});

                        // 添加點擊事件監聽器，點擊時顯示資訊視窗
                        // JavaScript 語法，為 DOM 或 Maps 物件添加事件監聽器 (click 事件)。
                        // 為當前這個 marker (地圖上的展覽點) 註冊一個事件。當使用者用滑鼠點擊它時，就會執行後面的函式。
                            marker.addListener("click", () => {{ 
                                
                                // 設定標題跟內容
                                const image_url = point['圖片連結']; // 圖片網址
                                const title = point['展覽名稱'] || '無標題'; // 展覽標題
                                const space = point['展覽地點'] || '無地點資訊'; // 展覽地點

                                let image_html;
                                if (image_url) {{
                                    image_html = '<img src="' + image_url + '" style="width: 100%; height: auto; border-radius: 4px; margin-bottom: 8px;" alt="展覽圖片">';
                                    }} else {{
                                        image_html = '<p style="font-style: italic; color: #999;">無圖片預覽</p>';
                                        }}
                                
                                // 這裡使用已經準備好的 HTML 變數
                                const content = `
                                <div style="max-width: 280px; font-family: sans-serif;">
                                    <h5 style="margin-top: 0; color: #4CAF50;">${{title}}</h5>

                                    ${{image_html}} 

                                    <p style="font-size: 13px; margin: 0;">地點： ${{space}}</p>
                                    
                                    </div>
                                    `;
                                
                                // 將上一步準備好的文字內容 (content) 設置到事先定義好的資訊視窗物件 (infoWindow) 中。
                                // Google Maps API InfoWindow 物件的方法，用於設定 HTML 或文字內容。
                                infoWindow.setContent(content); 
                                
                                // 顯示這個資訊視窗。它告訴 Google Maps 函式庫：在地圖物件 (map) 上，將這個視窗錨定在剛才被點擊的標記 (marker) 上。Google Maps API InfoWindow 物件的方法，用於在指定的地圖和錨點上顯示視窗。
                                infoWindow.open(map, marker);
                            }});
                        }});
                    }}
                </script>

                // 1. 引用 Python 端的 self.GOOGLEMAP (API Key)。 
                // 2. 引用 initMap (當 API 載入完成後，自動呼叫 initMap)。
                <script async defer src="https://maps.googleapis.com/maps/api/js?key={self.GOOGLEMAP}&callback=initMap">
                </script>
            </body>
        </html>
        '''
        # 使用 Streamlit HTML 元件嵌入地圖
        html(map_html, height = map_height)    
        
    def _display_google_map_mult(self, df: pd.DataFrame, venue_name : str, map_height: int = 700) -> None:
        df_v = df[(df['展館名稱'] == venue_name)]
        if df_v.empty:
            st.warning(f'數據庫中找不到屬於 **{df_v}** 的展覽點位。無法顯示地圖。')
            return 
        
        
        # 準備數據：選取 lat, lon, title 欄位，並轉換為 JSON 格式
        points = df_v[['緯度', '經度', '展覽名稱', '圖片連結', '展覽地點']].to_dict('records')
        points_json = json.dumps(points) # 將 Python 列表轉換為 JavaScript 陣列字串

        # 計算地圖中心點 (所有點的平均值)
        center_lat = df_v['緯度'].mean()
        center_lon = df_v['經度'].mean()

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
                <div id="map"></div> // 後面的 JavaScript 中的 document.getElementById('map') 會引用這個 ID。

                <script> // 嵌入 JavaScript 代碼開始。

                    // 傳遞 Python 數據到 JavaScript
                    const exhibitionPoints = {points_json}; // 創建java物件

                    function initMap() {{ // 地圖初始化函式定義。 這是 Google Maps API 載入完成後會調用的入口函式。
                        // 設定地圖中心點。 使用 Python 傳入的中心經緯度。
                        const centerPoint = {{ lat: {center_lat}, lng: {center_lon} }}; 

                        // 1. 引用 google.maps.Map (API 載入)。 
                        // 2. 引用 document.getElementById('map') (HTML 容器)。 
                        // 3. 創建的 map 變數會被後續的 marker 和 infoWindow 引用。
                        const map = new google.maps.Map(document.getElementById('map'), {{ // 創建地圖主物件。
                            zoom: 15, // 放大層級
                            center: centerPoint,
                            mapId: "{self.GOOGLEMAPID}", 
                            tilt : 45
                        }});

                        // 創建資訊視窗物件 (InfoWindow)。 這是點擊標記時彈出的視窗物件。
                        const infoWindow = new google.maps.InfoWindow(); // 引用 google.maps.InfoWindow (API 載入)。創建的 infoWindow 變數會被後續的點擊監聽器引用。

                        // 迴圈遍歷所有點位並添加標記
                        // 遍歷所有展覽點位。 針對 exhibitionPoints 陣列中的每一個 point 執行內部函式。 引用 exhibitionPoints (Python 傳來的數據)。
                        exhibitionPoints.forEach(point => {{ 
                            const marker = new google.maps.Marker({{ // 引用 google.maps.Marker (API 載入)。創建的 marker 變數會被後續的點擊監聽器引用。
                                position: {{ lat: point.緯度, lng: point.經度}},
                                map: map, // 將標記添加到哪個地圖物件上。引用 map 變數 (第 141 列定義)。
                                title: point.展覽名稱 // 引用當前循環的 point 數據中的 title 屬性。
                            }});

                        // 添加點擊事件監聽器，點擊時顯示資訊視窗
                        // JavaScript 語法，為 DOM 或 Maps 物件添加事件監聽器 (click 事件)。
                        // 為當前這個 marker (地圖上的展覽點) 註冊一個事件。當使用者用滑鼠點擊它時，就會執行後面的函式。
                            marker.addListener("click", () => {{ 
                                
                                // 設定標題跟內容
                                const image_url = point['圖片連結']; // 圖片網址
                                const title = point['展覽名稱'] || '無標題'; // 展覽標題
                                const space = point['展覽地點'] || '無地點資訊'; // 展覽地點

                                let image_html;
                                if (image_url) {{
                                    image_html = '<img src="' + image_url + '" style="width: 100%; height: auto; border-radius: 4px; margin-bottom: 8px;" alt="展覽圖片">';
                                    }} else {{
                                        image_html = '<p style="font-style: italic; color: #999;">無圖片預覽</p>';
                                        }}
                                
                                // 這裡使用已經準備好的 HTML 變數
                                const content = `
                                <div style="max-width: 280px; font-family: sans-serif;">
                                    <h5 style="margin-top: 0; color: #4CAF50;">${{title}}</h5>

                                    ${{image_html}} 

                                    <p style="font-size: 13px; margin: 0;">地點： ${{space}}</p>
                                    
                                    </div>
                                    `;
                                
                                // 將上一步準備好的文字內容 (content) 設置到事先定義好的資訊視窗物件 (infoWindow) 中。
                                // Google Maps API InfoWindow 物件的方法，用於設定 HTML 或文字內容。
                                infoWindow.setContent(content); 
                                
                                // 顯示這個資訊視窗。它告訴 Google Maps 函式庫：在地圖物件 (map) 上，將這個視窗錨定在剛才被點擊的標記 (marker) 上。Google Maps API InfoWindow 物件的方法，用於在指定的地圖和錨點上顯示視窗。
                                infoWindow.open(map, marker);
                            }});
                        }});
                    }}
                </script>

                // 1. 引用 Python 端的 self.GOOGLEMAP (API Key)。 
                // 2. 引用 initMap (當 API 載入完成後，自動呼叫 initMap)。
                <script async defer src="https://maps.googleapis.com/maps/api/js?key={self.GOOGLEMAP}&callback=initMap">
                </script>
            </body>
        </html>
        '''
        # 使用 Streamlit HTML 元件嵌入地圖
        html(map_html, height = map_height)
    



    # 🎯 新增函式：使用 st.columns 顯示場館網格列表
    def _display_venue_grid(self, info : pd.DataFrame | dict):
        # 定義每行顯示 4 個欄位 (在寬螢幕下)
        columns = st.columns(4) 

        # 建立容器
        all_venues = [] # 展館名稱 或 展覽名稱
        image_url_dict = dict() # 圖片連結
        hashtags_dict = dict() # 標籤
        clicktext = ''
        page_mode = ''

        # 所有要呈現的列表
        if type(info) == pd.DataFrame:
            src_dict = info[['展覽名稱', '圖片連結', '展覽介紹']].to_dict('records')
            for ids in src_dict:
                all_venues.append(ids.get('展覽名稱'))
                image_url_dict[ids.get('展覽名稱')] = ids.get('圖片連結')
                hashtags_dict[ids.get('展覽名稱')] = ids.get('展覽介紹')[:100] + '...'
                clicktext = r':ghost: 查看展覽說明'
                page_mode = 'exhibition_view'
        else:
            all_venues = list(info.keys()) # 首頁用的 home
            image_url_dict = self.venue_image_urls
            hashtags_dict = self.venue_hashtags
            clicktext = r'📍 查看展館中的展覽'
            page_mode = 'map_view'
        
        
        
        for i, venue_name in enumerate(all_venues):
            with columns[i % 4]:
                image_url = image_url_dict.get(venue_name)
                hashtags = hashtags_dict.get(venue_name, '')
                
                # 使用 Streamlit 內建的元件來顯示內容
                styled_caption = f"""
                <div style="
                    font-size: 18px; 
                    color: #f4a460; 
                    font-weight: bold; 
                    text-align: left; /* 讓標題置中 */
                    margin-top: 8px; 
                ">
                    {venue_name}
                </div>
                """
                # 1. 顯示場館圖片
                st.image(
                    image = image_url, 
                    # caption = f'**{venue_name}**',
                    use_container_width = True, # 讓圖片填滿欄位寬度
                    output_format = 'auto'
                )

                # 2. 顯示 展館名稱
                st.markdown(styled_caption, unsafe_allow_html = True)

                # 3. 顯示 Hashtag
                st.markdown(
                    f'<div style="font-size: 12px; color: #888888; margin-top: -1px;">{hashtags}</div>', 
                    unsafe_allow_html = True
                )
                
                # 4. 點擊按鈕，實現互動
                # 使用唯一的 key 來區分每個按鈕
                button_key = f'select_{venue_name}'
                
                # 如果點擊按鈕，則將場館名稱儲存到 Session State
                if st.button(f'**{clicktext}**', key = button_key, use_container_width = True):
                    st.session_state['selected'] = venue_name
                    st.session_state['page_mode'] = page_mode # 設置頁面模式為地圖視圖
                    # st.toast(f'已選擇 **{venue_name}**，頁面將切換到地圖視圖。')
                    st.rerun() 
                    # Button State Lag 或 One-Click Delay ===============================================================================
                    # 第一次點擊，Python 腳本從頭到尾執行了一次。變更session_state 為 **venue_name**
                    # 第二次點擊，Streamlit 偵測到 Session State 變化，觸發第二次重新執行。
                    # 按鈕邏輯執行完畢並成功更新了 Session State 時，手動強制 Streamlit 立即重新執行(st.rerun())，而不等待 Streamlit 自動處理狀態變化。
                    # ===================================================================================================================

        # 確保 selected 狀態存在
        if 'selected' not in st.session_state:
            st.session_state['selected'] = 'None'
    
    def _translate_date(self, df : pd.DataFrame) -> pd.DataFrame:
        df['update_flg'] = pd.to_datetime(df['update_flg']) + pd.Timedelta(hours = 8)
        df['start_date'] = pd.to_datetime(df['start_date']).dt.strftime('%Y-%m-%d')
        df['end_date'] = pd.to_datetime(df['end_date']).dt.strftime('%Y-%m-%d')
        df.columns = ['展館名稱', '展覽地點', '展覽名稱', '開始日期', '結束日期', '參觀時間', '票價', '緯度', '經度', '網頁連結', '圖片連結', '展覽介紹', '更新時間']
        return df
    
    # 展館、展覽搜尋功能 =====================================================================
    def _search_fuzzy_wildcard(self, usr_input : str, searchlist : list) -> List[str]:
        choices = [i.lower() for i in searchlist] # 要比對的清單
        
        best_match = process.extract(usr_input.lower(), choices, limit = 3) # 模糊比對，選前三名出來；choices是用戶可選的場館列表
        # 回傳 Tuple：("最佳匹配字串", 分數, 在清單中的 index)

        score_threshold = 45 # 設定分數門檻
        filtered_match_name = [i[0] for i in best_match if i[1] >= score_threshold] # 挑出符合門檻的，其他丟掉

        if filtered_match_name:
            return filtered_match_name
        else:
            return []


    # 數據統計品質功能 =======================================================================
    def _generate_wordcloud_plot(self, keyword_series : pd.DataFrame) -> None:
        # 1. 轉換為頻率字典 {詞彙: 頻率}
        word_freq_dict = pd.Series(
            keyword_series['出現次數'].values, 
            index = keyword_series['Tag']
        ).to_dict()

        # 2. 定義中文停用詞
        custom_stopwords = set([
            '的', '是', '在', '與', '和', '展', '覽', '藝術', '作品', '設計', '活動',
            '透過', '觀眾', '系列', '個', '由', '於', '為', '將', '年', '代', '日', '{', '}', ','
        ])
            
        try:
            # 4. 初始化 WordCloud 物件
            font_path = 'fonts/NotoSansTC-Regular.ttf' # src/fonts/NotoSansTC-Regular.ttf
            wordcloud = WordCloud(
                font_path = font_path,
                width = 2000, 
                height = 600,
                background_color = None,
                mode = 'RGBA', # 設置為 RGBA 模式以支援透明度
                max_words = 50,
                # stopwords = custom_stopwords,
                collocations = False,
                prefer_horizontal = 0.9,
                colormap = 'Paired'
            ).generate_from_frequencies(word_freq_dict) # 注意：這裡使用 generate_from_frequencies

            # 5. 使用 Matplotlib 繪圖
            fig, ax = plt.subplots(figsize = (20, 15), facecolor = 'none') # facecolor='none' 透明

            # 設定 Matplotlib 圖表和軸的背景為透明 (透明度 alpha = 0)
            fig.patch.set_alpha(0)  # 圖表外框
            ax.patch.set_alpha(0)   # 圖表繪製區塊

            ax.imshow(wordcloud, interpolation ='bilinear')
            ax.axis('off')
            # ax.set_title('展覽熱門關鍵字趨勢 (AI Tagging)', fontsize=16)

            # 6. 使用 Streamlit 顯示 Matplotlib 圖表
            st.pyplot(fig)
            plt.close(fig) # 關閉 Matplotlib 圖形，釋放記憶體

        except Exception as e:
            st.error(f'❌ 產生文字雲失敗: {e}')


    # 1. 資料缺失率 - 每個欄位缺少的數量、哪個展館通常不顯示資訊(是否跟展館性質有關係)等
    # 2. 資料更新頻率統計 - 每次更新時間、每次更新數量
    # 3. 新增展覽數、性質、位置等
    # 4. 消失展覽數、性質、位置等
    # 5. 展覽內容共同出現的詞彙數量，做成詞雲圖? 一眼看出當前熱門展覽主題
    # 6. 如果會員功能有做出來，看**主題**蒐藏數量、男性vs女性、所在地點等分布狀況



    # 7. 增加展館數量，提升資料數量


    # 各session的頁面內容 ======================================================================
    # Session home
    def _home_session(self) -> None:
        # 頁面基礎資訊
        st.set_page_config(layout = 'wide', page_icon = '📊', page_title = self.config_ttile) # 設定 Streamlit 頁面標題和圖示，並設定為寬模式布局
        st.markdown(f'# **:orange[{self.topic}]**')    
        
        
        st.markdown('---')
        
        col_title, col_ai = st.columns([3, 2]) # 讓搜尋欄位不佔滿整行
        with col_title:
            # with row_h, row_t = st.rows([3, 1])
            st.markdown(f'> 目前日期 &ensp; {dt.datetime.today().strftime('%Y-%m-%d')}')
            st.markdown(f'{self.sideprojectbrief}')

            # 用戶搜尋窗格
            st.markdown('##### **:red[想去哪裡看展?&emsp;&emsp;直接輸入找更快喔!]**')
            usr_input = st.text_input('搜尋展館', label_visibility = 'collapsed')
            filtered_venue_names = self._search_fuzzy_wildcard(usr_input, list(self.venue_image_urls.keys())) #
            
            # 整理 - 展覽的熱門關鍵字
            world_feq = []
            world_cloud_select = self.df_tags['hallname'].isin(filtered_venue_names) if filtered_venue_names else self.df_tags['hallname'].isin(list(self.venue_image_urls.keys()))
            df_tags_keywords = self.df_tags[world_cloud_select].copy(deep = True)
            df_tags_keywords['keywords'] = df_tags_keywords['keywords'].str.replace(r'[{}]', '', regex = True).str.split(',')
            for i in df_tags_keywords['keywords']:
                world_feq.extend(i)
            keyword_counts_series = pd.Series(world_feq, name = 'Tag').value_counts().reset_index(name = '出現次數').sort_values(by = '出現次數', ascending = False)
        
        with col_ai:
            st.markdown('### **:yellow[🔥 展覽關鍵字熱門趨勢(AI Tagging)]**')
            if not keyword_counts_series.empty:
                self._generate_wordcloud_plot(keyword_counts_series)
            else:
                st.caption('（尚無關鍵字資料可供分析）')
        st.markdown('---')
        

            
            
        if usr_input and filtered_venue_names != []:
            st.markdown('## 🏛️ 您可能要找的展館')
            st.info(f'**:yellow[🔥 全館前10大覽熱門關鍵字：]** {', '.join(keyword_counts_series['Tag'][:10].values)}')
            filtered_venue_info = {
                name : self.venue_image_urls[name] 
                for name in filtered_venue_names 
                if name in self.venue_image_urls
            } # 轉換成dict，為了要傳入版面呈現的函數中
            self._display_venue_grid(filtered_venue_info)
        else:
            if usr_input:
                st.markdown('### 找不到輸入的展覽館耶...請重新輸入，或是從下面圖片中找找看~')
                self._display_venue_grid(self.venue_image_urls)
            else:
                st.markdown('## 🏛️ 展覽場館一覽')
                st.info(f'**:yellow[🔥 雙北展覽前10大熱門關鍵字：]** {', '.join(keyword_counts_series['Tag'][:10].values)}')
                self._display_venue_grid(self.venue_image_urls)
                
        
        st.markdown('---')
               
    
    # Session map_view
    def _map_view_session(self) -> None:
        # 返回按鈕
        if st.button('◀ 返回場館列表'):
            st.session_state['page_mode'] = 'home' # 切換回首頁
            st.rerun() # 重新執行應用程式以立即切換頁面
        # 頁面內容
        df_current_venue = self.df_exhibitions[self.df_exhibitions['展館名稱'] == st.session_state['selected']]
        st.set_page_config(layout = 'wide', page_icon = '📊', page_title = st.session_state['selected']) # 設定 Streamlit 頁面標題和圖示，並設定為寬模式布局
        st.markdown(f'# **:orange[{st.session_state['selected']}]**')
        st.markdown(f'> 目前日期 &ensp; {dt.datetime.today().strftime('%Y-%m-%d')}')
        st.markdown(f'**{self.venue_introduction.get(st.session_state['selected'])}**')
        
        st.markdown('---')

        col_search, col_tag = st.columns([2, 3]) # 讓搜尋欄位不佔滿整行

        with col_search:
            st.markdown('##### **:red[有沒有要搜尋的展覽?&emsp;&emsp;直接輸入找更快喔!]**')
            usr_input = st.text_input('')
            checklist = self.df_exhibitions[self.df_exhibitions['展館名稱'] == st.session_state['selected']]['展覽名稱'].unique().tolist()
        st.markdown('---')


        filtered_exhibition_names = self._search_fuzzy_wildcard(usr_input, checklist) # 用戶可能再找的展覽清單
        # 整理 - 展覽的熱門關鍵字
        world_feq = []
        world_cloud_select = self.df_tags['title'].isin(filtered_exhibition_names) if filtered_exhibition_names else self.df_tags['title'].isin(checklist)
        df_tags_keywords = self.df_tags[world_cloud_select].copy(deep = True)
        df_tags_keywords['keywords'] = df_tags_keywords['keywords'].str.replace(r'[{}]', '', regex = True).str.split(',')
        for i in df_tags_keywords['keywords']:
            world_feq.extend(i)
        keyword_counts_series = pd.Series(world_feq, name = 'Tag').value_counts().reset_index(name = '出現次數').sort_values(by = '出現次數', ascending = False)
        hashtaglist = "`" + "` `".join(keyword_counts_series['Tag'].values) + "`"
        
        if usr_input and filtered_exhibition_names != []:
            df_display = df_current_venue[df_current_venue['展覽名稱'].isin(filtered_exhibition_names)]
            st.markdown(f' **:yellow[🔥 展覽關鍵字：]** ***{hashtaglist}***')
            self._display_venue_grid(df_display)
        else:
            if usr_input:
                st.markdown('### 找不到輸入的展覽館耶...請重新輸入，或是從下面圖片中找找看~')
                self._display_venue_grid(df_current_venue)
            else:
                st.markdown(f' **:yellow[🔥 展覽關鍵字：]** ***{hashtaglist}***')
                self._display_venue_grid(df_current_venue)
                


    # Session exhibition_view
    def _exhibition_view_session(self) -> None:
        select_ven = st.session_state['selected'] # 展覽資訊
        st.markdown(f'### 🗺️ **{select_ven}** 資訊')
        
        
        st.markdown(f'{self.df_exhibitions[self.df_exhibitions['展覽名稱'] == select_ven]['網頁連結'].values[0]}')
        if st.button('◀ 返回展覽列表'):
            st.session_state['page_mode'] = 'map_view' # 切換回展覽清單
            st.session_state['selected'] = self.df_exhibitions[self.df_exhibitions['展覽名稱'] == select_ven]['展館名稱'].unique().tolist()[0]
            st.rerun() # 重新執行應用程式以立即切換頁面

        # st.info(f'**:yellow[🔥 雙北展覽前10大熱門關鍵字：]** {', '.join(keyword_counts_series['Tag'][:10].values)}')
        if not self.df_exhibitions.empty:
            select_df = self.df_exhibitions[self.df_exhibitions['展覽名稱'] == select_ven] # 篩出
            img_src = select_df['圖片連結'].values[0]
            st.markdown('---')
            # 整理 - 展覽的熱門關鍵字
            world_feq = []
            world_cloud_select = self.df_tags['title'].isin([select_ven])
            df_tags_keywords = self.df_tags[world_cloud_select].copy(deep = True)
            df_tags_keywords['keywords'] = df_tags_keywords['keywords'].str.replace(r'[{}]', '', regex = True).str.split(',')
            for i in df_tags_keywords['keywords']:
                world_feq.extend(i)
            keyword_counts_series = pd.Series(world_feq, name = 'Tag').value_counts().reset_index(name = '出現次數').sort_values(by = '出現次數', ascending = False)
            hashtaglist = "`" + "` `".join(keyword_counts_series['Tag'].values) + "`"
            st.markdown(f' **:yellow[🔥 展覽關鍵字：]** ***{hashtaglist}***')

            col_map, col_list = st.columns([2, 3]) # 3/5 寬度給地圖, 2/5 寬度給清單

            with col_map:
                
                infotext = []
                
                for loc in ['展覽地點', '展覽名稱', '開始日期', '結束日期', '參觀時間', '票價', '展覽介紹']:
                    infotext.append(f'**:yellow[{loc}]** : {select_df[loc].values[0]}')
                
                st.markdown('\n\n'.join(infotext))
                st.image(image = img_src, caption = f'**{select_df['展覽名稱'].values[0]}**')

            with col_list:
                
                st.markdown(f'### 周邊展覽地圖')
                self._display_google_map(self.df_exhibitions, venue_name = select_df['展館名稱'].values[0], exhibition_name = select_ven ,map_height = 600)
    # 各session的頁面內容 ======================================================================            

   
    # Streamlit 應用程式主體 ====================================================================================
    def website_main(self):

        # 🎯 注入 CSS 以固定圖片高度
        st.markdown('''
            <style>
                /* 調整圖片大小 */
                .stImage img {
                    height: 250px !important; /* 設置您希望的固定高度，並使用 !important 提高權重 */
                    width: 100% !important; /* 確保寬度佔滿容器 */
                    object-fit: cover !important; /* 確保圖片不變形，會裁剪多餘部分，並使用 !important */
                    border-radius: 8px; /* 美化邊角 */
                }
                /* 為了美觀，可以讓圖片上方的容器 margin 消除一些 */
                div[data-testid="stImage"] {
                    margin-bottom: 0px; 
                }
                
            </style>
        ''', unsafe_allow_html = True)    

        if st.session_state['page_mode'] == 'home':
            self._home_session()
            
        elif st.session_state['page_mode'] == 'map_view':
            self._map_view_session()
            
        elif st.session_state['page_mode'] == 'exhibition_view':    
            self._exhibition_view_session()

        else:
            st.warning('資料庫連線失敗或沒有找到正在展出的展覽資料。請檢查錯誤訊息和連線字串。')

if __name__ == '__main__':
    load_dotenv() 
    app = streamlit_run_app()
    app.website_main()