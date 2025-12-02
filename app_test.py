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
import datetime as dt
import json


class streamlit_run_app:  
    def __init__(self):
        self.databasename = os.getenv('databasename')
        self.DATABASE_URL = os.getenv('DATABASE_URL')
        self.SQLQUERY = f'select * from {self.databasename}'
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
            '松山文創園區': '''松山文創園區定位為「臺北市原創基地」，自2011年對外開放以來，肩負帶動城市原創力與軟實力的使命。園區前身為松山菸廠，保留了歷史建築，並規劃了「跨界實驗」、「創意學院」等五大創新策略。這裡作為國際級的文創聚落，致力於扶植原創人才，鼓勵創新與實驗性創作。園區提供從創業育成到品牌建立，從核心創作到商業運用的全流程支持，實現設計發想、測試製作到國際鏈結。松山文創園區已成為台灣重要的創意樞紐，民眾可在此平台參與藝術與原創，體驗無限的創意與活力。''',
            '國立師大美術館': '''師大美術館承載自1947年以來國立臺灣師範大學師生與校友的美術創作實踐，典藏超過4000件藝術作品，是臺灣近代美術史的重要見證者。美術館以「典藏研究轉譯」、「美術當代策展」、「跨域參與共學」等為核心，旨在擁抱校園與社區，垂直連接不同世代與族群，並積極與國際交流藝術思維。標誌設計上，以獨特的建築形體為靈感，不對稱的三角形展現創新與突破，虛實相映的佈局則反映其訊息整合與開放性。美術館以書法墨色為基底的代表色彩，蘊含著東方文化的儒雅與師大綿延的人文素養，致力於傳承在地文化並與全球接軌。''',
            '台北當代藝術館': '''台北當代藝術館館舍建築落成於1921年，原為日治時期的「建成尋常小學校」，後曾作為近五十年的台北市政府辦公廳舍，是驅動市政的神經中樞。1996年舊廈登錄為市定古蹟，並在古蹟再利用政策下，於2001年轉型為國內唯一的「台北當代藝術館」，與建成國中結合，創造了美術館與學校共用建物的先例。當代館位於歷史文化軸線的延展上，象徵帶動大同區再發展的新契機。作為台灣當代藝術的重要窗口，當代館自我期許推動多元風貌的藝術創作與展覽，激發民眾的新觀點和新思維，並為城市發展提供源源不絕的創意與活力。''',
            '華山1914文化創意園區': '''華山1914文化創意園區前身是歷史悠久的酒廠。自2002年行政院將其納入「創意文化園區」計畫後，經歷整修，拆除圍牆，並修復古蹟與歷史建築。2007年由臺灣文創發展股份有限公司入主經營，正式以「華山1914文化創意園區」重新營運。園區秉持「一本大書、一個舞台、一種風景、一所學校」的理念，旨在將華山轉型為台灣文創旗艦基地。華山走過百年風華，積極接軌國際，透過結合文化資產活化與再生的概念，導入文化、創意、藝術與設計等元素，提供民眾一個集展覽、表演、休閒於一體的多元文化體驗空間。''',
            '國立故宮博物院': '''國立故宮博物院典藏了匯集北平、熱河、瀋陽三處清宮的珍稀文物，是亞洲文物菁華與人類文化史上的瑰寶。故宮文物因緣際會來到臺灣，成為臺灣多元文化源流中極為重要的部分，肩負著承繼數千年中華文化之責。故宮致力於「深耕在地，邁向國際」的願景，施政原則聚焦在公共化、在地化、專業化、多元化、國際化及年輕化。近年來，故宮積極推動新故宮計畫，優化北部院區和南院空間設施，並以「參觀者本位之原則」提升整體服務品質，期盼強化其作為國際矚目博物館的專業與高度。''',
            '富邦美術館': '''富邦美術館經歷近10年籌備，於2024年5月在台北市信義區開啟嶄新場域。美術館以「藝術每一天 Art Every Day」為本質，旨在傳遞藝術帶來的幸福與喜悅。美術館積極關注台灣與世界各地的藝術家，抱持開放、積極的態度推動藝術對話與交流。其展覽聚焦現當代藝術，以激發觀者想像為目標，為信義區這片商業核心地帶注入了重要的文化與創意元素。美術館以綠意環繞的設計，為市民提供了一個全新的、充滿熱情與想像力的藝術空間。''',
            '臺北市立美術館' : '''本館肩負推動臺灣現當代藝術的保存、研究、發展與普及之使命，掌握全球趨勢、建立多元交流管道，提升普羅大眾對現當代藝術的認知與參與，促使臺灣現當代藝術發展臻至蓬勃，全民藝術涵養更加豐沛，以期形成具有美感修為及文化思辨力的當代社會。''',
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
            st.session_state['page_mode'] = "home" # 預設為首頁
        if 'selected' not in st.session_state:
            st.session_state['selected'] = "None"

    @st.cache_data(ttl = 600)
    # 使用 Streamlit 的快取機制，避免每次互動都重新查詢資料庫
    # ttl=600 表示每 600 秒 (10 分鐘) 才重新查詢一次資料庫
    def _connectsql_get_data(_self) -> pd.DataFrame:
        if not _self.DATABASE_URL:
            # st.error('錯誤：DATABASE_URL 環境變數未設定，無法連線。')
            return pd.DataFrame()
        
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
            
            return df

        except Exception as e:
            # st.error(f'❌ 讀取 Supabase 資料失敗，錯誤訊息: {e}')
            st.caption(f'{e}')
            return pd.DataFrame()
        

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
            src_dict = info[['title', 'img_url', 'overview']].to_dict('records')
            for ids in src_dict:
                all_venues.append(ids.get('title'))
                image_url_dict[ids.get('title')] = ids.get('img_url')
                hashtags_dict[ids.get('title')] = ids.get('overview')[:100] + '...'
                clicktext = r':ghost: 查看展覽說明'
                page_mode = 'exhibition_view'
        else:
            all_venues = list(self.venue_image_urls.keys()) # 首頁用的 home
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
        













        
    # Streamlit 應用程式主體
    def website_main(self):
        # 🎯 使用 st.spinner 包裹耗時的數據載入步驟
        with st.spinner('⏳ 正在從 Supabase 建立連線並讀取資料，請稍候...'): # 上下文管理器 (Context Manager)，用來在程式碼執行需要較長時間時，在螢幕上顯示一個旋轉的載入動畫（俗稱 Spinner）
            df_exhibitions = self._connectsql_get_data()
                    

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
            st.set_page_config(layout = 'wide', page_icon = '📊', page_title = self.config_ttile) # 設定 Streamlit 頁面標題和圖示，並設定為寬模式布局
            st.markdown(f'# **:orange[{self.topic}]**')
            st.markdown(f'> 目前日期 &ensp; {dt.datetime.today().strftime('%Y-%m-%d')}')
            st.markdown(f'{self.sideprojectbrief}')
            st.markdown('---')
            
            # ----------------------------------------------------
            # A. 首頁視圖 (Home View)
            # ----------------------------------------------------
            st.markdown('## 🏛️ 展覽場館一覽')
            self._display_venue_grid(self.venue_image_urls)
            
            st.markdown('---')
            
        elif st.session_state['page_mode'] == 'map_view':
            if st.button('◀ 返回場館列表'):
                st.session_state['page_mode'] = 'home' # 切換回首頁
                st.rerun() # 重新執行應用程式以立即切換頁面
            st.set_page_config(layout = 'wide', page_icon = '📊', page_title = st.session_state['selected']) # 設定 Streamlit 頁面標題和圖示，並設定為寬模式布局
            st.markdown(f'# **:orange[{st.session_state['selected']}]**')
            st.markdown(f'> 目前日期 &ensp; {dt.datetime.today().strftime('%Y-%m-%d')}')
            st.markdown(f'**{self.venue_introduction.get(st.session_state['selected'])}**')
            st.markdown('---')

            df_exhibitions = df_exhibitions[df_exhibitions['hallname'] == st.session_state['selected']]
            self._display_venue_grid(df_exhibitions)
            df_exhibitions = self._translate_date(df_exhibitions)
            if st.button('◀ 返回場館列表'):
                st.session_state['page_mode'] = 'home' # 切換回首頁
                st.rerun() # 重新執行應用程式以立即切換頁面


        elif st.session_state['page_mode'] == 'exhibition_view':    

            select_ven = st.session_state['selected']
            st.markdown(f'### 🗺️ **{select_ven}** 資訊')
            
            df_exhibitions = self._translate_date(df_exhibitions)
            st.markdown(f'{df_exhibitions[df_exhibitions['展覽名稱'] == select_ven]['網頁連結'].values[0]}')
            if st.button('◀ 返回展覽列表'):
                st.session_state['page_mode'] = 'back' # 切換回展覽清單
                st.session_state['last_page_hallname'] = df_exhibitions[df_exhibitions['展覽名稱'] == select_ven]['展館名稱'].unique().tolist()[0]
                st.rerun() # 重新執行應用程式以立即切換頁面
            if not df_exhibitions.empty:
                select_df = df_exhibitions[df_exhibitions['展覽名稱'] == select_ven] # 篩出
                img_src = select_df['圖片連結'].values[0]
                st.markdown('---')
                
                # 3. 現在展覽名稱
                
                if select_ven != '請選擇您感興趣的展覽 (預設顯示全部)':
                    col_map, col_list = st.columns([2, 3]) # 3/5 寬度給地圖, 2/5 寬度給清單

                    with col_map:
                        
                        infotext = []
                        
                        for loc in ['展覽地點', '展覽名稱', '開始日期', '結束日期', '參觀時間', '票價', '展覽介紹']:
                            infotext.append(f'**:yellow[{loc}]** : {select_df[loc].values[0]}')
                        
                        st.markdown('\n\n'.join(infotext))
                        st.image(image = img_src, caption = f'**{select_df['展覽名稱'].values[0]}**')

                    with col_list:
                        
                        st.markdown(f'### 周邊展覽地圖')
                        self._display_google_map(df_exhibitions, venue_name = df_exhibitions['展館名稱'].values[0], exhibition_name = select_ven ,map_height = 600)
                
            # if st.button('◀ 返回展覽列表'):
            #     st.session_state['page_mode'] = 'back' # 切換回展覽清單
            #     st.session_state['last_page_hallname'] = df_exhibitions[df_exhibitions['展覽名稱'] == select_ven]['展館名稱'].unique().tolist()[0]
            #     st.rerun() # 重新執行應用程式以立即切換頁面



        elif st.session_state['page_mode'] == 'back':   
            if st.button('◀ 返回場館列表'):
                st.session_state['page_mode'] = 'home' # 切換回首頁
                st.rerun() # 重新執行應用程式以立即切換頁面
            st.set_page_config(layout = 'wide', page_icon = '📊', page_title = st.session_state['selected']) # 設定 Streamlit 頁面標題和圖示，並設定為寬模式布局
            st.markdown(f'# **:orange[{st.session_state['last_page_hallname']}]**')
            st.markdown(f'> 目前日期 &ensp; {dt.datetime.today().strftime('%Y-%m-%d')}')
            st.markdown(f'**{self.venue_introduction.get(st.session_state['last_page_hallname'])}**')
            st.markdown('---')

            df_exhibitions = df_exhibitions[df_exhibitions['hallname'] == st.session_state['last_page_hallname']]
            self._display_venue_grid(df_exhibitions)
            df_exhibitions = self._translate_date(df_exhibitions)


        else:
            st.warning('資料庫連線失敗或沒有找到正在展出的展覽資料。請檢查錯誤訊息和連線字串。')

if __name__ == '__main__':
    load_dotenv() 
    app = streamlit_run_app()
    app.website_main()