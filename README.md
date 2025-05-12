# RARTower - Tower Management Simulation Game

A Python-based business tower management simulation game inspired by Yoot Tower. Build and manage your own tower with multiple businesses including entertainment, movies, shopping, hotels, restaurants, and more!

## Features

- Multiple business types:
  - Entertainment venues
  - Movie theaters
  - Shopping centers
  - Hotels
  - Restaurants
  - Police department
  - Hospital
  - Security offices
  - Various other businesses

- Advanced simulation systems:
  - Economic simulation
  - Customer AI and pathfinding
  - Time and weather system
  - Emergency events
  - Business relationships
  - Staff management

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/RAR-tower.git
cd RAR-tower
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Development

Project structure:
```
src/
├── core/           # Core game mechanics
├── entities/       # Game entities (businesses, people, etc.)
├── ui/            # User interface components
├── utils/         # Utility functions
├── assets/        # Game assets (images, sounds, etc.)
└── config/        # Configuration files

tests/             # Unit tests
```

## Running the Game

```bash
python src/main.py
```

## Testing

```bash
python -m pytest tests/
```

## License

[MIT License](LICENSE)
