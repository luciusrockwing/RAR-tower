from enum import Enum, auto

class EventType(Enum):
    """Types of events that can occur in the game"""
    FESTIVAL = auto()
    EMERGENCY_DRILL = auto()
    KAIJU_ATTACK = auto()
    INSPECTION = auto()
    VIP_VISIT = auto()
    RENOVATION = auto()
    WEATHER_EVENT = auto()
    CELEBRITY_VISIT = auto()

class BuildingType(Enum):
    """Types of buildings that can be constructed"""
    HOTEL = auto()
    RESTAURANT = auto()
    SHOP = auto()
    CINEMA = auto()
    OFFICE = auto()
    APARTMENT = auto()
    MOVIE_THEATER = auto()
    ARCADE = auto()
    OBSERVATION_DECK = auto()

class Config:
    # Window settings
    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 720
    FPS = 60
    
    # Game settings
    TILE_SIZE = 32
    MAX_FLOORS = 100
    STARTING_MONEY = 1000000
    
    # Business settings
    BUSINESS_TYPES = {
        'hotel': {
            'cost': 100000,
            'maintenance': 1000,
            'revenue_per_customer': 200,
            'size': (3, 2)  # width, height in tiles
        },
        'restaurant': {
            'cost': 50000,
            'maintenance': 500,
            'revenue_per_customer': 50,
            'size': (2, 1)
        },
        'shop': {
            'cost': 75000,
            'maintenance': 750,
            'revenue_per_customer': 100,
            'size': (2, 1)
        },
        'cinema': {
            'cost': 200000,
            'maintenance': 2000,
            'revenue_per_customer': 150,
            'size': (4, 2)
        },
        'office': {
            'cost': 150000,
            'maintenance': 1500,
            'revenue_per_customer': 0,
            'size': (3, 1)
        }
    }
    
    # Colors
    COLORS = {
        'black': (0, 0, 0),
        'white': (255, 255, 255),
        'gray': (128, 128, 128),
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255)
    }
    
    # Time settings
    TIME_SCALE = 1000  # 1 game day = 1000 real milliseconds
    OPENING_HOUR = 6
    CLOSING_HOUR = 22
    TIME_SPEEDS = {
        'pause': 0,
        'normal': 1,
        'fast': 2,
        'ultra': 4
    }
    MINUTES_PER_UPDATE = 1  # How many game minutes pass per update
    RUSH_HOURS = {
        'morning': (8, 10),   # 8 AM - 10 AM
        'lunch': (12, 14),    # 12 PM - 2 PM
        'evening': (17, 19)   # 5 PM - 7 PM
    }
    
    # Weather settings
    WEATHER_CHANGE_CHANCE = 0.1  # 10% chance per hour
    WEATHER_TYPES = ['sunny', 'rainy', 'cloudy']
    
    # Event settings
    EVENT_TYPES = {
        'maintenance': {
            'interval': 24,     # Hours between maintenance
            'duration': 120,    # Minutes
            'cost': 5000       # Cost per maintenance
        },
        'vip_visit': {
            'min_interval': 48,  # Minimum hours between VIP visits
            'duration': 180,     # Minutes
            'reward': 10000      # Reward for satisfying VIP
        },
        'sale_period': {
            'duration': 360,     # 6 hours in minutes
            'discount': 0.2      # 20% discount
        },
        'power_outage': {
            'chance_per_day': 0.05,  # 5% chance per day
            'duration': 60           # 1 hour in minutes
        },
        'festival': {
            'chance_per_week': 0.3,  # 30% chance per week
            'duration': 720,         # 12 hours in minutes
            'customer_boost': 2.0,   # Double customers
            'satisfaction_boost': 1.5 # 50% more satisfaction
        },
        'competition': {
            'chance_per_month': 0.5, # 50% chance per month
            'duration': 2880,        # 2 days in minutes
            'price_reduction': 0.3   # Competitors reduce prices by 30%
        },
        'celebrity_visit': {
            'chance_per_month': 0.2, # 20% chance per month
            'duration': 240,         # 4 hours in minutes
            'revenue_boost': 2.0,    # Double revenue
            'customer_boost': 3.0    # Triple customers
        },
        'health_inspection': {
            'interval': 720,         # Every 30 days
            'duration': 180,         # 3 hours
            'penalty': 10000         # Penalty for failing
        },
        'renovation': {
            'duration': 480,         # 8 hours
            'cost_per_floor': 2000,  # Cost per floor
            'satisfaction_boost': 2.0 # Double satisfaction after
        },
        'festival': {
            'duration': 480,  # 8 hours in minutes
            'satisfaction_boost': 2.0,  # Multiplier for customer satisfaction
            'revenue_boost': 1.5  # Multiplier for revenue
        },
        'inspection': {
            'notice_period': 24,  # Hours before inspection
            'duration': 120,  # 2 hours in minutes
            'required_cleanliness': 4.0,  # Minimum cleanliness rating
            'required_maintenance': 4.0  # Minimum maintenance rating
        },
        'emergency_drill': {
            'duration': 60,  # 1 hour in minutes
            'satisfaction_penalty': -1.0,  # Reduction in customer satisfaction
            'safety_boost': 1.5  # Multiplier for safety rating
        }
    }
    
    # Event Effects
    EVENT_EFFECTS = {
        'weather': {
            'sunny': {
                'customer_multiplier': 1.2,
                'satisfaction_bonus': 1
            },
            'rainy': {
                'customer_multiplier': 0.7,
                'satisfaction_penalty': -1
            },
            'cloudy': {
                'customer_multiplier': 1.0,
                'satisfaction_bonus': 0
            }
        },
        'rush_hour': {
            'morning': {
                'customer_multiplier': 2.0,
                'business_types': ['coffee_shop', 'restaurant']
            },
            'lunch': {
                'customer_multiplier': 1.8,
                'business_types': ['restaurant', 'shop']
            },
            'evening': {
                'customer_multiplier': 1.5,
                'business_types': ['restaurant', 'cinema', 'hotel']
            }
        }
    }
    
    # VIP Types and their requirements
    VIP_TYPES = {
        'food_critic': {
            'requirements': ['restaurant'],
            'min_rating': 4.0,
            'reward_multiplier': 1.5
        },
        'hotel_inspector': {
            'requirements': ['hotel'],
            'min_rating': 4.5,
            'reward_multiplier': 2.0
        },
        'business_tycoon': {
            'requirements': ['office', 'hotel'],
            'min_rating': 3.5,
            'reward_multiplier': 3.0
        },
        'movie_star': {
            'requirements': ['hotel', 'cinema'],
            'min_rating': 4.0,
            'reward_multiplier': 2.5
        }
    }
    
    # Map settings
    MAPS_DIRECTORY = "src/maps"
    DEFAULT_MAP = "tokyo_tower"
    
    # Event settings
    EVENT_PROBABILITIES = {
        EventType.FESTIVAL: 0.05,        # 5% chance per day
        EventType.EMERGENCY_DRILL: 0.02,  # 2% chance per day
        EventType.KAIJU_ATTACK: 0.001,   # 0.1% chance per day
        EventType.INSPECTION: 0.03,       # 3% chance per day
        EventType.VIP_VISIT: 0.02,       # 2% chance per day
        EventType.RENOVATION: 0.01,       # 1% chance per day
        EventType.WEATHER_EVENT: 0.04,    # 4% chance per day
        EventType.CELEBRITY_VISIT: 0.01   # 1% chance per day
    }
    
    EVENT_EFFECTS = {
        EventType.FESTIVAL: {
            'visitor_multiplier': 2.0,
            'revenue_multiplier': 1.5,
            'duration_days': 3
        },
        EventType.EMERGENCY_DRILL: {
            'visitor_multiplier': 0.5,
            'revenue_multiplier': 0.7,
            'duration_days': 1
        },
        EventType.KAIJU_ATTACK: {
            'visitor_multiplier': 0.1,
            'revenue_multiplier': 0.1,
            'damage_chance': 0.3,
            'duration_days': 2
        }
        # More event effects can be added here
    }
    
    # Theme settings
    AVAILABLE_THEMES = {
        'tokyo': {
            'background_music': 'tokyo_theme.mp3',
            'color_scheme': {
                'primary': (255, 0, 0),
                'secondary': (255, 255, 255),
                'accent': (0, 0, 0)
            },
            'special_buildings': ['pagoda', 'zen_garden']
        }
        # More themes can be added here
    }
