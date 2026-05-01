# Bird-Migration-Pattern-Predictor
My first main Python project, created for my A-Level Computer Science NEA. The program can output past bird and weather data from 2000 to 2024, and predict numbers for the following year. It also includes a full GUI and web scraping functionality.

## Overview
This was my first ever major Python project, where I taught myself how to web scrape, interact with databases and create GUIs during the implementation phase of the project. Some alterations have been made to the web scraper and GUI since it was submitted for my A-Level project to fix errors preventing execution, but otherwise the program has been left untouched. The project adds all bird data (derived from BirdTrack) from the CSV files to its database, then web scrapes the weather data (derived from Weather Underground), before launching the main GUI. Users can create predictions for the 8 species included and 4 areas of the UK, as well as view historical data with the same constraints. Data is outputted visually using graphs. I aspire to improve further on what is undeniably an inefficient but ambitious project, and my preserving it on GitHub can hopefully show how much I've already improved. Nevertheless, I have stopped maintaining the project, and as such the algorithm predicts data for 2025, using historical data from 2000-2024. While this may seem disadvantageous, it does allow comparison with 2025 data to evaluate the project's accuracy.

## Features
- Web scraping functionality to ensure weather data is up-to-date.
- Create predictions for 8 bird species in 4 UK areas for 2025.
- View historical bird & weather data for 2000-2024.
- View results in visual formats.

## Requirements
- Python 3.10+
- (Optional) Virtual environment tool
- OS: Windows (preferred)

## Installation
1. Clone the repository:
```
git clone https://github.com/w-lycett/Bird-Migration-Pattern-Predictor.git
cd Bird-Migration-Pattern-Predictor
```
2. (Recommended) Create a virtual environment:
```
python -m venv venv
```
3. Activate the virtual environment (Windows):
```
venv\Scripts\activate
```
4. Run the project root:
```
python -m main
```
The first panel of the GUI should appear with instructions.

## Contributing
As this is an archive for my NEA project, I will disable pull requests as the project should remain in its current state.
