"""
Configuration loader - handles YAML config and environment variables
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration manager for the flight bot"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self._validate_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        config_file = Path(self.config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}\n"
                f"Please copy config.example.yaml to config.yaml and edit it."
            )
        
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Override with environment variables if present
        config = self._apply_env_overrides(config)
        
        return config
    
    def _apply_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Override config with environment variables"""
        
        # Email settings
        if os.getenv('EMAIL_RECIPIENT'):
            config['email']['recipient'] = os.getenv('EMAIL_RECIPIENT')
        if os.getenv('GMAIL_SENDER'):
            config['email']['sender_gmail'] = os.getenv('GMAIL_SENDER')
        if os.getenv('GMAIL_PASSWORD'):
            config['email']['smtp_password'] = os.getenv('GMAIL_PASSWORD')
        
        # API credentials
        if os.getenv('AMADEUS_API_KEY'):
            config['api']['amadeus_api_key'] = os.getenv('AMADEUS_API_KEY')
        if os.getenv('AMADEUS_API_SECRET'):
            config['api']['amadeus_api_secret'] = os.getenv('AMADEUS_API_SECRET')
        
        # Advanced settings
        if os.getenv('CHECK_FREQUENCY_HOURS'):
            config['advanced']['check_frequency_hours'] = int(os.getenv('CHECK_FREQUENCY_HOURS'))
        if os.getenv('LOG_LEVEL'):
            config['advanced']['log_level'] = os.getenv('LOG_LEVEL')
        
        return config
    
    def _validate_config(self):
        """Validate required configuration fields"""
        required_fields = {
            'email': ['recipient', 'sender_gmail', 'smtp_password'],
            'api': ['amadeus_api_key', 'amadeus_api_secret'],
            'routes': ['origin', 'destinations'],
        }
        
        for section, fields in required_fields.items():
            if section not in self.config:
                raise ValueError(f"Missing required config section: {section}")
            
            for field in fields:
                if field not in self.config[section]:
                    raise ValueError(f"Missing required field: {section}.{field}")
                
                # Check for placeholder values
                value = str(self.config[section][field])
                if value.startswith('YOUR_') or value.startswith('your.'):
                    raise ValueError(
                        f"Please update {section}.{field} in config.yaml\n"
                        f"Current value appears to be a placeholder: {value}"
                    )
    
    # Convenience properties
    @property
    def email_recipient(self) -> str:
        return self.config['email']['recipient']
    
    @property
    def gmail_sender(self) -> str:
        return self.config['email']['sender_gmail']
    
    @property
    def gmail_password(self) -> str:
        return self.config['email']['smtp_password']
    
    @property
    def amadeus_api_key(self) -> str:
        return self.config['api']['amadeus_api_key']
    
    @property
    def amadeus_api_secret(self) -> str:
        return self.config['api']['amadeus_api_secret']
    
    @property
    def origin(self) -> str:
        return self.config['routes']['origin']
    
    @property
    def destinations(self) -> List[str]:
        return self.config['routes']['destinations']
    
    @property
    def trip_length_min(self) -> int:
        return self.config['dates']['trip_length']['minimum_days']
    
    @property
    def trip_length_max(self) -> int:
        return self.config['dates']['trip_length']['maximum_days']
    
    @property
    def trip_length_flexible(self) -> bool:
        return self.config['dates']['trip_length']['flexible_duration']
    
    @property
    def max_stops(self) -> int:
        return self.config['connections']['max_stops']
    
    @property
    def preferred_hubs(self) -> List[str]:
        return self.config['connections'].get('preferred_hubs', [])
    
    @property
    def different_return_airport(self) -> bool:
        return self.config['airport_flexibility']['different_return_airport']
    
    @property
    def separate_tickets_enabled(self) -> bool:
        return self.config['separate_tickets']['enabled']
    
    @property
    def risk_tolerance(self) -> str:
        return self.config['separate_tickets']['risk_tolerance']
    
    @property
    def amazing_deal_price(self) -> float:
        return self.config['price_alerts']['thresholds']['amazing_deal']
    
    @property
    def great_deal_price(self) -> float:
        return self.config['price_alerts']['thresholds']['great_deal']
    
    @property
    def major_deal_threshold_percent(self) -> float:
        return self.config['email']['major_deal_threshold_percent']
    
    @property
    def check_frequency_hours(self) -> int:
        return self.config['advanced']['check_frequency_hours']
    
    @property
    def log_level(self) -> str:
        return self.config['advanced']['log_level']
    
    @property
    def database_path(self) -> str:
        return self.config['advanced'].get('database_path', 'data/flights.db')
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get nested config value using dot notation"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value if value is not None else default


# Singleton instance
_config_instance: Optional[Config] = None


def get_config(config_path: str = "config.yaml") -> Config:
    """Get or create configuration instance"""
    global _config_instance
    
    if _config_instance is None:
        _config_instance = Config(config_path)
    
    return _config_instance
