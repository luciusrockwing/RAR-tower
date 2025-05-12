import pygame
from entities.customer import Customer
from typing import Dict, List
from enum import Enum

class BusinessType(Enum):
    RESTAURANT = "restaurant"
    HOTEL = "hotel"
    OFFICE = "office"
    RETAIL = "retail"
    GYM = "gym"
    CINEMA = "cinema"
    ARCADE = "arcade"
    SPA = "spa"
    CONFERENCE = "conference"
    OBSERVATION = "observation"
    BAR = "bar"
    PARKING = "parking"

class BusinessCategory(Enum):
    ENTERTAINMENT = "entertainment"
    SERVICE = "service"
    HOSPITALITY = "hospitality"
    OFFICE = "office"
    RETAIL = "retail"

class BusinessEvent:
    """Events that can occur in businesses"""
    SPECIAL_PROMOTION = "special_promotion"
    CELEBRITY_VISIT = "celebrity_visit"
    STAFF_SHORTAGE = "staff_shortage"
    EQUIPMENT_FAILURE = "equipment_failure"
    HEALTH_INSPECTION = "health_inspection"
    RENOVATION = "renovation"

class BusinessInteraction:
    """Defines interactions between businesses"""
    
    # Synergy mappings between business types (positive effects)
    SYNERGIES = {
        BusinessType.HOTEL: {
            BusinessType.RESTAURANT: 0.25,  # Hotels boost restaurant income significantly
            BusinessType.SPA: 0.2,         # Hotel guests love spas
            BusinessType.BAR: 0.15,        # Evening entertainment
            BusinessType.RETAIL: 0.1,      # Shopping convenience
            BusinessType.CONFERENCE: 0.15   # Business travelers
        },
        BusinessType.RESTAURANT: {
            BusinessType.BAR: 0.15,        # Dinner and drinks
            BusinessType.HOTEL: 0.1,       # Room service potential
            BusinessType.CINEMA: 0.15,     # Dinner and movie
            BusinessType.RETAIL: 0.1       # Shopping center dining
        },
        BusinessType.OFFICE: {
            BusinessType.RESTAURANT: 0.3,  # Lunch crowds
            BusinessType.CONFERENCE: 0.25,  # Business meetings
            BusinessType.GYM: 0.15,        # After work fitness
            BusinessType.BAR: 0.2,         # After work drinks
            BusinessType.RETAIL: 0.15      # Lunch break shopping
        },
        BusinessType.RETAIL: {
            BusinessType.RESTAURANT: 0.15,  # Shopping break meals
            BusinessType.CINEMA: 0.15,      # Entertainment complex
            BusinessType.ARCADE: 0.1,       # Family entertainment
            BusinessType.HOTEL: 0.1        # Tourist shopping
        },
        BusinessType.CINEMA: {
            BusinessType.RESTAURANT: 0.2,   # Dinner and movie
            BusinessType.ARCADE: 0.2,       # Entertainment center
            BusinessType.BAR: 0.15,         # Evening entertainment
            BusinessType.RETAIL: 0.1        # Movie merchandise
        },
        BusinessType.GYM: {
            BusinessType.SPA: 0.25,         # Wellness combo
            BusinessType.RESTAURANT: 0.15,  # Healthy eating
            BusinessType.RETAIL: 0.1        # Sports equipment
        },
        BusinessType.ARCADE: {
            BusinessType.CINEMA: 0.2,       # Entertainment synergy
            BusinessType.RESTAURANT: 0.15,  # Gaming snacks
            BusinessType.RETAIL: 0.1        # Gaming merchandise
        },
        BusinessType.CONFERENCE: {
            BusinessType.HOTEL: 0.2,        # Business accommodation
            BusinessType.RESTAURANT: 0.15,  # Business lunches
            BusinessType.OFFICE: 0.15       # Business services
        },
        BusinessType.SPA: {
            BusinessType.HOTEL: 0.2,        # Luxury amenity
            BusinessType.GYM: 0.2,          # Wellness center
            BusinessType.RESTAURANT: 0.1    # Healthy dining
        }
    }
    
    # Competition effects (negative impacts)
    COMPETITION = {
        BusinessType.RESTAURANT: {
            BusinessType.RESTAURANT: -0.15  # Competing restaurants reduce each other's income
        },
        BusinessType.RETAIL: {
            BusinessType.RETAIL: -0.1      # Competing shops impact sales
        },
        BusinessType.BAR: {
            BusinessType.BAR: -0.2         # Direct competition for evening crowd
        },
        BusinessType.CINEMA: {
            BusinessType.CINEMA: -0.25     # Strong competition for viewers
        }
    }
    
    # Special combinations that create unique effects
    SPECIAL_COMBOS = {
        frozenset([BusinessType.HOTEL, BusinessType.SPA, BusinessType.RESTAURANT]): {
            'name': 'Luxury Resort Package',
            'bonus': 0.3,  # 30% bonus to all participating businesses
            'reputation_bonus': 5
        },
        frozenset([BusinessType.CINEMA, BusinessType.ARCADE, BusinessType.RESTAURANT]): {
            'name': 'Entertainment Complex',
            'bonus': 0.25,
            'reputation_bonus': 3
        },
        frozenset([BusinessType.GYM, BusinessType.SPA, BusinessType.RESTAURANT]): {
            'name': 'Wellness Center',
            'bonus': 0.25,
            'reputation_bonus': 4
        },
        frozenset([BusinessType.OFFICE, BusinessType.CONFERENCE, BusinessType.RESTAURANT]): {
            'name': 'Business Hub',
            'bonus': 0.2,
            'reputation_bonus': 3
        }
    }
    
    @staticmethod
    def calculate_interactions(business_type: BusinessType, nearby: List['Business'], floor_distance: int) -> tuple:
        """Calculate all interaction effects for a business"""
        synergy_bonus = 0.0
        competition_penalty = 0.0
        special_bonus = 0.0
        active_combos = set()
        
        # Calculate distance modifier (closer businesses have stronger effects)
        distance_modifier = max(0, (5 - floor_distance) / 5)
        
        # Calculate synergies and competition
        for nearby_business in nearby:
            # Synergy effects
            synergy = BusinessInteraction.SYNERGIES.get(business_type, {}).get(nearby_business.type, 0.0)
            synergy_bonus += synergy * distance_modifier
            
            # Competition effects
            competition = BusinessInteraction.COMPETITION.get(business_type, {}).get(nearby_business.type, 0.0)
            competition_penalty += competition * distance_modifier
        
        # Check for special combinations
        nearby_types = {b.type for b in nearby} | {business_type}
        for combo_types, combo_info in BusinessInteraction.SPECIAL_COMBOS.items():
            if nearby_types.issuperset(combo_types):
                special_bonus = max(special_bonus, combo_info['bonus'])
                active_combos.add(combo_info['name'])
        
        return synergy_bonus, competition_penalty, special_bonus, active_combos
    
    @staticmethod
    def get_synergy_bonus(business_type: BusinessType, nearby_type: BusinessType) -> float:
        """Get the synergy bonus between two business types"""
        return BusinessSynergy.SYNERGIES.get(business_type, {}).get(nearby_type, 0.0)

class Business:
    """Represents a business in the tower"""
    def __init__(self, type: BusinessType, floor: int):
        self.type = type
        self.floor = floor
        self.name = ""
        self.category = self._get_category()
        self.popularity = 50  # 0-100
        self.income = 0
        self.maintenance_cost = 0
        self.staff = 0
        self.customers = []
        self.size = 1  # Size in floor units
        self.is_open = True
        self.satisfaction = 100  # 0-100
        self.events = []
        self.event_duration = 0
        self.nearby_businesses = []  # List of businesses within 5 floors
        self.synergy_bonus = 0.0
        self.peak_hours = self._get_peak_hours()
        self.customer_types = self._get_customer_types()
        
        # Initialize business-specific attributes
        self._initialize_attributes()
    
    def _get_category(self) -> BusinessCategory:
        """Determine business category based on type"""
        category_map = {
            BusinessType.RESTAURANT: BusinessCategory.HOSPITALITY,
            BusinessType.HOTEL: BusinessCategory.HOSPITALITY,
            BusinessType.OFFICE: BusinessCategory.OFFICE,
            BusinessType.RETAIL: BusinessCategory.RETAIL,
            BusinessType.GYM: BusinessCategory.SERVICE,
            BusinessType.CINEMA: BusinessCategory.ENTERTAINMENT,
            BusinessType.ARCADE: BusinessCategory.ENTERTAINMENT,
            BusinessType.SPA: BusinessCategory.SERVICE,
            BusinessType.CONFERENCE: BusinessCategory.SERVICE,
            BusinessType.OBSERVATION: BusinessCategory.ENTERTAINMENT,
            BusinessType.BAR: BusinessCategory.HOSPITALITY,
            BusinessType.PARKING: BusinessCategory.SERVICE
        }
        return category_map.get(self.type, BusinessCategory.SERVICE)
    
    def _initialize_attributes(self):
        """Initialize business-specific attributes"""
        # Base values for different business types
        type_configs = {
            BusinessType.RESTAURANT: {
                'size': 1,
                'base_income': 1000,
                'maintenance': 200,
                'staff': 8
            },
            BusinessType.HOTEL: {
                'size': 4,
                'base_income': 5000,
                'maintenance': 1000,
                'staff': 20
            },
            BusinessType.OFFICE: {
                'size': 2,
                'base_income': 3000,
                'maintenance': 500,
                'staff': 4
            },
            BusinessType.RETAIL: {
                'size': 1,
                'base_income': 800,
                'maintenance': 150,
                'staff': 4
            },
            BusinessType.GYM: {
                'size': 1,
                'base_income': 600,
                'maintenance': 300,
                'staff': 6
            },
            BusinessType.CINEMA: {
                'size': 2,
                'base_income': 2000,
                'maintenance': 400,
                'staff': 10
            },
            BusinessType.ARCADE: {
                'size': 1,
                'base_income': 1500,
                'maintenance': 300,
                'staff': 4
            },
            BusinessType.SPA: {
                'size': 1,
                'base_income': 1200,
                'maintenance': 250,
                'staff': 8
            },
            BusinessType.CONFERENCE: {
                'size': 2,
                'base_income': 2000,
                'maintenance': 300,
                'staff': 4
            },
            BusinessType.OBSERVATION: {
                'size': 1,
                'base_income': 3000,
                'maintenance': 200,
                'staff': 6
            },
            BusinessType.BAR: {
                'size': 1,
                'base_income': 1500,
                'maintenance': 300,
                'staff': 6
            },
            BusinessType.PARKING: {
                'size': 3,
                'base_income': 500,
                'maintenance': 100,
                'staff': 2
            }
        }
        
        # Set attributes based on business type
        config = type_configs.get(self.type, {})
        self.size = config.get('size', 1)
        self.income = config.get('base_income', 1000)
        self.maintenance_cost = config.get('maintenance', 200)
        self.staff = config.get('staff', 4)
    
    def _get_peak_hours(self) -> List[tuple]:
        """Get peak business hours"""
        peak_hours = {
            BusinessType.RESTAURANT: [(7,10), (12,14), (18,22)],  # Breakfast, Lunch, Dinner
            BusinessType.HOTEL: [(14,20)],  # Check-in times
            BusinessType.OFFICE: [(9,17)],  # Work hours
            BusinessType.RETAIL: [(11,19)],  # Shopping hours
            BusinessType.GYM: [(6,9), (17,21)],  # Before/after work
            BusinessType.CINEMA: [(14,23)],  # Afternoon/Evening
            BusinessType.ARCADE: [(12,22)],  # Afternoon/Evening
            BusinessType.SPA: [(10,20)],  # Day time
            BusinessType.CONFERENCE: [(9,17)],  # Business hours
            BusinessType.OBSERVATION: [(10,20)],  # Day time
            BusinessType.BAR: [(17,2)],  # Evening/Night
            BusinessType.PARKING: [(0,24)]  # All day
        }
        return peak_hours.get(self.type, [(9,17)])
        
    def _get_customer_types(self) -> List[str]:
        """Define target customer types"""
        customer_types = {
            BusinessType.RESTAURANT: ['workers', 'tourists', 'residents'],
            BusinessType.HOTEL: ['tourists', 'business'],
            BusinessType.OFFICE: ['workers', 'business'],
            BusinessType.RETAIL: ['tourists', 'residents', 'workers'],
            BusinessType.GYM: ['residents', 'workers'],
            BusinessType.CINEMA: ['tourists', 'residents', 'youth'],
            BusinessType.ARCADE: ['youth', 'tourists'],
            BusinessType.SPA: ['tourists', 'residents'],
            BusinessType.CONFERENCE: ['business'],
            BusinessType.OBSERVATION: ['tourists'],
            BusinessType.BAR: ['workers', 'tourists', 'residents'],
            BusinessType.PARKING: ['workers', 'visitors']
        }
        return customer_types.get(self.type, ['general'])
        
    def trigger_event(self, event: str) -> None:
        """Trigger a business event"""
        self.events.append(event)
        
        # Apply event effects
        if event == BusinessEvent.SPECIAL_PROMOTION:
            self.popularity += 20
            self.event_duration = 3  # 3 days
        elif event == BusinessEvent.CELEBRITY_VISIT:
            self.popularity += 30
            self.event_duration = 1  # 1 day
        elif event == BusinessEvent.STAFF_SHORTAGE:
            self.satisfaction -= 20
            self.event_duration = 2  # 2 days
        elif event == BusinessEvent.EQUIPMENT_FAILURE:
            self.satisfaction -= 30
            self.maintenance_cost *= 1.5
            self.event_duration = 2
        elif event == BusinessEvent.HEALTH_INSPECTION:
            if self.maintenance_cost > 0:
                self.satisfaction += 10
            else:
                self.satisfaction -= 40
            self.event_duration = 1
        elif event == BusinessEvent.RENOVATION:
            self.is_open = False
            self.satisfaction = 100
            self.event_duration = 5  # 5 days
            
    def update_synergy(self, nearby_businesses: List['Business']) -> None:
        """Update synergy effects from nearby businesses"""
        self.nearby_businesses = nearby_businesses
        total_synergy = 0.0
        total_competition = 0.0
        total_special = 0.0
        self.active_combos = set()
        
        # Group nearby businesses by distance
        distance_groups = {}
        for nearby in nearby_businesses:
            floor_distance = abs(self.floor - nearby.floor)
            if floor_distance <= 5:  # Only consider businesses within 5 floors
                distance_groups.setdefault(floor_distance, []).append(nearby)
        
        # Calculate effects for each distance group
        for distance, businesses in distance_groups.items():
            synergy, competition, special, combos = BusinessInteraction.calculate_interactions(
                self.type, businesses, distance)
            total_synergy += synergy
            total_competition += competition
            total_special = max(total_special, special)  # Take highest special bonus
            self.active_combos.update(combos)
        
        # Calculate final bonus (cap at 75% total bonus)
        self.synergy_bonus = min(0.75, max(0, total_synergy + total_competition + total_special))
        
        # Update business attributes based on interactions
        if self.active_combos:
            self.satisfaction = min(100, self.satisfaction + 0.2)  # Small satisfaction boost
            self.popularity = min(100, self.popularity + 0.1)  # Small popularity boost
        
    def update(self, dt: float, current_hour: float) -> None:
        """Update business state"""
        if not self.is_open:
            return
            
        # Update event duration
        if self.event_duration > 0:
            self.event_duration -= dt
            if self.event_duration <= 0:
                self.events.clear()
                # Reset any temporary effects
                if BusinessEvent.RENOVATION in self.events:
                    self.is_open = True
                
        # Calculate time-based modifiers
        time_modifier = self._calculate_time_modifier(current_hour)
        
        # Calculate actual income with all modifiers
        base_modifier = (self.popularity + self.satisfaction) / 200
        total_modifier = base_modifier * (1 + self.synergy_bonus) * time_modifier
        self.actual_income = self.income * total_modifier
        
        # Update customer count
        max_customers = self.size * 20 * time_modifier
        target_customers = int(max_customers * (self.popularity / 100))
        current_customers = len(self.customers)
        
        # Gradually adjust customer count
        if current_customers < target_customers:
            self.customers.extend([None] * min(5, target_customers - current_customers))
        elif current_customers > target_customers:
            self.customers = self.customers[:-min(5, current_customers - target_customers)]
        
        # Update satisfaction based on maintenance and overcrowding
        crowd_factor = len(self.customers) / (self.size * 20)
        if crowd_factor > 1:
            self.satisfaction = max(0, self.satisfaction - 0.5)
            
        if self.maintenance_cost > 0:
            self.satisfaction = min(100, self.satisfaction + 0.1)
        else:
            self.satisfaction = max(0, self.satisfaction - 0.2)
            
    def _calculate_time_modifier(self, current_hour: float) -> float:
        """Calculate business modifier based on time of day"""
        for start, end in self.peak_hours:
            if start <= current_hour < end:
                return 1.5  # 50% bonus during peak hours
            elif (start-1) <= current_hour < (end+1):
                return 1.2  # 20% bonus during shoulder hours
        return 0.7  # 30% penalty during off-peak hours
    
    def create_placeholder_image(self):
        width = self.size[0] * self.config.TILE_SIZE
        height = self.size[1] * self.config.TILE_SIZE
        image = pygame.Surface((width, height))
        image.fill(self.config.COLORS['blue'])
        return image
    
    def add_customer(self, customer):
        """Add a new customer to the business"""
        if isinstance(customer, Customer):
            self.customers.append(customer)
            return True
        return False
    
    def remove_customer(self, customer):
        """Remove a customer from the business"""
        if customer in self.customers:
            self.customers.remove(customer)
            self.revenue += self.revenue_per_customer
            return True
        return False
    
    def update_satisfaction(self):
        """Update business satisfaction rating"""
        # Basic satisfaction calculation
        # TODO: Implement more complex satisfaction factors
        customer_factor = len(self.customers) / 10  # Arbitrary capacity
        self.satisfaction = max(0, min(100, self.satisfaction - customer_factor))
    
    def get_profit(self):
        """Calculate current profit"""
        return self.revenue - self.expenses
    
    def draw(self, screen, grid_position):
        """Draw the business on the screen"""
        x = grid_position[0] * self.config.TILE_SIZE
        y = grid_position[1] * self.config.TILE_SIZE
        screen.blit(self.image, (x, y))
        
        # Draw customer count (debug)
        font = pygame.font.Font(None, 24)
        text = font.render(str(len(self.customers)), True, self.config.COLORS['white'])
        screen.blit(text, (x + 5, y + 5))
