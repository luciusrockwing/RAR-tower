import random

class Customer:
    def __init__(self, config):
        self.config = config
        self.satisfaction = 100
        self.money = random.randint(50, 1000)
        self.time_in_business = 0
        self.max_time = random.randint(10, 60)  # Minutes to spend in business
        
    def update(self):
        """Update customer state"""
        self.time_in_business += 1
        
        # Random satisfaction changes
        self.satisfaction += random.randint(-1, 1)
        self.satisfaction = max(0, min(100, self.satisfaction))
    
    def is_finished(self):
        """Check if customer is done with their visit"""
        return self.time_in_business >= self.max_time
    
    def get_preferred_businesses(self):
        """Return a list of business types this customer is interested in"""
        # For now, return random selection of businesses
        return random.sample(list(self.config.BUSINESS_TYPES.keys()), 
                           random.randint(1, len(self.config.BUSINESS_TYPES)))
