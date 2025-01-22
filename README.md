# Liao-EC530-HW1
# GPS Closest Point Matcher

This Python project calculates the closest GPS location in one array of coordinates to each point in another array, using the **Haversine formula** to compute great-circle distances between two points on the Earth.

## Features
- User-friendly interface with input prompts for entering GPS coordinates.
- Validation for latitude and longitude to ensure proper range:
  - Latitude: `-90` to `90`
  - Longitude: `-180` to `180`
- Calculates and outputs:
  - Each point from the first array.
  - The closest point in the second array.
  - The distance between the two points in kilometers.

## Getting Started

### Prerequisites
- Python 3.x installed on your system.
- Basic familiarity with running Python scripts.

### Installation
1. Clone this repository to your local machine:
   ```bash
   git clone https://github.com/ryanliao296/Liao-EC530-HW1.git
   cd Liao-EC530-HW1
