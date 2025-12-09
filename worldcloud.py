數據統計品質功能 =======================================================================

    =======================================================================================
    文字雲功能 - 暫時停止 20251206
    影響速度，放到Liu的Tableau平台上面
    =======================================================================================    
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