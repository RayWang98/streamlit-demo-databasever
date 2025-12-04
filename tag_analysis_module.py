from google import genai          # Gemini API
from google.genai import types    # Gemini 結構化輸出 Schema
from google.genai.errors import APIError # 處理 Gemini API 錯誤
from typing import Optional, List, Dict, Any # 資料格式定義
from dataclasses import dataclass, field
import os                         # 讀取環境變數
import time                       # 執行延遲
from dotenv import load_dotenv    # 環境變數
from datetime import datetime     # 處理日期與時間
import pandas as pd               # 資料處理轉換
import numpy as np                # 資料處理轉換
import json
import random as rd


@dataclass
class ExhibitionKeyword: # 修正名稱以區別單個項目
    title : str = ''
    keywords : List[str] = field(default_factory = list) 

@dataclass
class KeywordsAnalysisResult:
    analysis_results: List[ExhibitionKeyword] = field(default_factory = list)

class EmptyResponseError(Exception):
    '''自定義錯誤：當 API 回傳空的文字內容時拋出。'''
    pass

class geniai:
    def __init__(self):
        self.GEMINI_KEY = os.getenv('GEMINI_API_KEY') # AI APIKEY
        self.INITIAL_DELAY = 5
        self.BATCHSIZE = 15

        # 初始化外部服務
        # ======================== Gemini ========================
        if self.GEMINI_KEY:
            self.client = genai.Client(api_key = self.GEMINI_KEY)
            print('Gemini 初始化成功')
        else:
            self.client = None
            print('Gemini 初始化失敗')

    def _extract_with_gemini(self, input_df : pd.DataFrame) -> List[ExhibitionKeyword]: # 用來跑google gemeni的
        
        exhibition_keyword_schema = types.Schema(
            type = types.Type.OBJECT, # 使用 OBJECT 作為單一活動的容器
            properties = {
                'title': types.Schema(type = types.Type.STRING, 
                                      description = '展覽的確切標題。'),
                'keywords': types.Schema(type = types.Type.ARRAY, 
                                     items = types.Schema(type = types.Type.STRING, description = '關鍵字。'),
                                     description = '由3-5個字組成的10到50個關鍵字列表。')
            },
        required = ['title', 'keywords'] # 必要欄位
        )

        final_schema = types.Schema(
            type = types.Type.OBJECT,
            properties={
                'analysis_results': types.Schema(type = types.Type.ARRAY, 
                                                 items = exhibition_keyword_schema,
                                                 description = '包含所有展覽關鍵字分析結果的列表。')
            }
        )

        # 提示詞工程
        base_prompt = r'''
        你是一個專業的文化分析師，專門從展覽描述中提取核心主題關鍵字。
        請根據提供的所有展覽內容，提取並返回一個 JSON 列表，每個展覽都是列表中的一個物件。

        **提取規則：**
        1.  每個展覽的關鍵字列表總共有 **10 到 50 個詞**。
        2.  每個關鍵詞的長度必須在 **3 到 5 個中文字** 之間。
        
        **以下是待分析的活動內容：**
        '''

        # 遍歷 DataFrame 創建輸入內容
        for _, row in input_df.iterrows():
            # 確保 'overview' 欄位不是 List，而是單一字串
            overview_text = ''.join(row['overview']) if isinstance(row['overview'], list) else row['overview']
            base_prompt += f"\n\n== 展覽標題: {row['title']} ==\n"
            base_prompt += f"   描述: {overview_text}"

        # 文本分析迴圈 (使用 self.client, self.MAX_RETRIES, self.INITIAL_DELAY)
        try:
            response = self.client.models.generate_content( # 一個包著 List[ExhibitionKeyword] 結構的 JSON 格式，是一個API的嚮應物件
                model = 'gemini-2.5-flash', 
                contents = base_prompt, 
                config = types.GenerateContentConfig( # 設定模型如何回應，包括輸出格式、限制和創造性程度等
                    response_mime_type = 'application/json', # 返回json格式資料
                    response_schema = final_schema, # 回應的格式按照前面定義的輸出
                    max_output_tokens = 4096, # 限制回傳的token數量，約3-4個英文字母或半個中文字等於1個token
                    temperature = 0.4 # 愈低的值代表模型的回答更具決定性、準確和可預測，適合需要嚴格數據提取和遵循格式的任務。較高的值則適用於寫作、創意或頭腦風暴。
                )
            )

            # 增加一項檢查：確保 response.text 是個字串
            if response is None or response.text is None:
                raise EmptyResponseError(f'Error : API 返回了空的文字內容。')
            
            # 如果成功，跳出重試循環 ==================================================== 到這步代表有抓到資料
            extracted_json = json.loads(response.text)  # dtype dict 解析產出的資料
            results_list = extracted_json.get('analysis_results', []) # results_list 現在是一個 Python 字典列表 (List[dict])
            output_data = []
            
            for item_dict in results_list:
                output_data.append(
                    ExhibitionKeyword( # 創建 ExhibitionKeyword 實例
                    title = item_dict.get('title', '無標題'), 
                    keywords = item_dict.get('keywords', [])
                    )
                )

            print(f'Successed : 批量提取完成。共處理 {len(output_data)} 筆展覽。')
            return output_data

        except APIError as e:
            print(f'API Error: 與 Gemini 通訊時發生錯誤: {e}')
            return []
        
        except Exception as e:
            print(f'General Error: 提取或解析時發生錯誤: {e}')
            return []
        
    # -----------------------------------------------------------------
    # 新增一個執行主線函式來模擬調用
    # -----------------------------------------------------------------
    def run_ai_analysis(self, df_raw: pd.DataFrame) -> List[ExhibitionKeyword]:

        if df_raw.empty:
            print("無展覽數據可供分析。")
            return []
        
        print(f"總共 {len(df_raw)} 筆展覽等待 AI 分析...")

        all_keywords : List[ExhibitionKeyword] = []
        num_batches = (len(df_raw) + self.BATCHSIZE - 1) // self.BATCHSIZE
        print(f'總共 {len(df_raw)} 筆展覽，將分 {num_batches} 批次進行 AI 分析...')
        
        

        for i in range(num_batches):
            strt_loc = i * self.BATCHSIZE
            end_index = (i + 1) * self.BATCHSIZE
            df_batch = df_raw.iloc[strt_loc : end_index, :]

            batch_keywords : List[ExhibitionKeyword] = self._extract_with_gemini(df_batch) # 創建一個ExhibitionKeyword的DataClass出來
            all_keywords.extend(batch_keywords)  # 將回傳的ExhibitionKeyword的DataClass放進去，因為類型相同，可以直接extend
        
        return all_keywords # 返回的是 List[ExhibitionKeyword]