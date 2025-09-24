"""
Centralized configuration management for the Financial Analyst App.
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """Base configuration class."""
    
    # Flask settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG: bool = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    
    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    FMP_API_KEY: str = os.getenv("FMP_API_KEY", "")
    NEWSAPI_KEY: str = os.getenv("NEWSAPI_KEY", "")
    FINNHUB_API_KEY: str = os.getenv("FINNHUB_API_KEY", "")
    
    # Slack configuration
    SLACK_BOT_TOKEN: str = os.getenv("SLACK_BOT_TOKEN", "")
    SLACK_CHANNEL: str = os.getenv("SLACK_CHANNEL", "#trading")
    
    # Analysis settings
    PRICE_LOOKBACK_DAYS: int = int(os.getenv("PRICE_LOOKBACK_DAYS", "730"))
    DEFAULT_UPDATE_INTERVAL: int = int(os.getenv("DEFAULT_UPDATE_INTERVAL", "15"))
    
    # Application settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    MAX_WORKERS: int = int(os.getenv("MAX_WORKERS", "2"))
    
    @property
    def have_fmp(self) -> bool:
        """Check if FMP API key is available."""
        return bool(self.FMP_API_KEY)
    
    @property
    def have_slack(self) -> bool:
        """Check if Slack configuration is available."""
        return bool(self.SLACK_BOT_TOKEN)
    
    def validate(self) -> list[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        if not self.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is required")
        
        if not self.have_fmp:
            errors.append("Warning: FMP_API_KEY not set, using Yahoo Finance only")
        
        return errors


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    LOG_LEVEL = "INFO"


class TestingConfig(Config):
    """Testing environment configuration."""
    TESTING = True
    DEBUG = True
    LOG_LEVEL = "DEBUG"


# Configuration mapping
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env_name: str = None) -> Config:
    """Get configuration based on environment name."""
    if env_name is None:
        env_name = os.getenv('FLASK_ENV', 'default')
    
    return config_by_name.get(env_name, DevelopmentConfig)()
