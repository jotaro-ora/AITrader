class NewsHistoryDB:
    def __init__(self):
        self.news = []
    
    def add_news(self, news):
        self.news.append(news)
    
    def get_recent_news(self, n=10):
        return self.news[-n:]
