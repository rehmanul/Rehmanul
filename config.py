"""Configuration module"""
class Config:
    def __init__(self):
        self.config_data = {
            "USER_AGENT": "Mozilla/5.0 (compatible; WebStrykerPython/1.0)",
            "MAX_RETRIES": 3,
            "TIMEOUT_SECONDS": 30,
        }
    
    def get(self, key: str, default=None):
        """Get config value"""
        return self.config_data.get(key, default)

config = Config()
