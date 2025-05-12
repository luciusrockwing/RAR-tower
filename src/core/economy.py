from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class RevenueStream:
    """Represents a source of income"""
    name: str
    amount: float
    recurring: bool = False
    source_type: str = "business"  # business, mini_game, special_event
    timestamp: datetime = None

@dataclass
class ExpenseItem:
    """Represents an expense"""
    name: str
    amount: float
    category: str  # maintenance, utilities, staff, upgrades
    recurring: bool = False
    timestamp: datetime = None

class Economy:
    """Manages the game's economy, including revenue, expenses, and upgrades."""
    def __init__(self):
        self.balance = 1000  # Starting balance
        self.revenue_streams: Dict[str, float] = {
            'businesses': 0,
            'mini_games': 0,
            'events': 0
        }
        self.expenses: Dict[str, float] = {
            'maintenance': 0,
            'salaries': 0
        }
        self.upgrades: List[Dict] = []  # List of active upgrades

    def calculate_daily_revenue(self) -> float:
        """Calculate total daily revenue."""
        return sum(self.revenue_streams.values())

    def calculate_daily_expenses(self) -> float:
        """Calculate total daily expenses."""
        return sum(self.expenses.values())

    def update_balance(self) -> None:
        """Update the balance based on revenue and expenses."""
        daily_revenue = self.calculate_daily_revenue()
        daily_expenses = self.calculate_daily_expenses()
        self.balance += daily_revenue - daily_expenses

    def add_revenue(self, source: str, amount: float) -> None:
        """Add revenue to a specific source."""
        if source in self.revenue_streams:
            self.revenue_streams[source] += amount

    def add_expense(self, category: str, amount: float) -> None:
        """Add an expense to a specific category."""
        if category in self.expenses:
            self.expenses[category] += amount

    def apply_upgrade(self, upgrade: Dict) -> None:
        """Apply an upgrade to the economy system."""
        self.upgrades.append(upgrade)
        if 'revenue_multiplier' in upgrade:
            for source in self.revenue_streams:
                self.revenue_streams[source] *= upgrade['revenue_multiplier']
        if 'expense_reduction' in upgrade:
            for category in self.expenses:
                self.expenses[category] *= (1 - upgrade['expense_reduction'])

    def reset_daily_values(self) -> None:
        """Reset daily revenue and expenses for a new day."""
        for key in self.revenue_streams:
            self.revenue_streams[key] = 0
        for key in self.expenses:
            self.expenses[key] = 0
