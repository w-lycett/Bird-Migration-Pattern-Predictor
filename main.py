

# SET UP PIP INSTALL

# subprocess + sys = required to pip install within code
import subprocess
import sys
# Function to pip install packages
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
# Pip install the relevant modules
install("pandas")
install("selenium")
install("numpy")
install("scipy")
install("scikit-learn")
install("matplotlib")

# IMPORT LIBRARIES

# Tkinter = required for GUI generation
import tkinter as tk
from tkinter import Menu, TclError, font, PhotoImage, Toplevel
# Path + sqlite3 = required for database access + creation
from pathlib import Path
import sqlite3
# pandas = required to translate .csv files to database
import pandas as pd
# selenium + webdriver + time = required for web scraping
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
# numpy + scipy + sklearn = required for data analysis
import numpy as np
import scipy
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Ridge
from sklearn.preprocessing import PolynomialFeatures
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score
# matplotlib = required for data visualisation
import matplotlib.pyplot as plt
# webbrowser = required for links in the GUI
import webbrowser


# INITIALISE VARIABLES / DATA STRUCTURES

Path("bird_migration_data.db").touch()  # Create database if it doesn't exist
b_conn = sqlite3.connect('bird_migration_data.db')  # Connect to database using b_conn
bird_migration_data = b_conn.cursor(
)  # Create cursor for database called bird_migration_data

Path("weather_data.db").touch()  # Create database if it doesn't exist
w_conn = sqlite3.connect('weather_data.db')  # Connect to database using w_conn
weather_data = w_conn.cursor(
)  # Create cursor for database called weather_data

# List of all windows in the program; used during GUI generation
windows_to_do = ["Home", "Past Bird Data", "Past Weather Data", "Predict", "Bird Data View", "Weather Data View", "Help", "Credits"]
# List of codes for each location
all_codes = ["EGNX", "EGOV", "EGPH", "EGAC"]

# Constant for the year predictions will be made for
global CURRENT_YEAR
CURRENT_YEAR = 2025
# For maintenance, to update this program for a new year, change this constant to the next year, then add to the .CSV files with the bird data for the year before (present year).

global all_years
all_years = []
next_year = CURRENT_YEAR + 1
# Gets an array of all years from 2000 to the current year
for year_count in range(2000, (next_year)):
  all_years.append(year_count)

# Constants for colours during GUI generation
LIGHT_GREEN = "#90EE90"
GREY_GREEN = "#739C85"
OCEAN_GREEN = "#7DCEA0"
MID_GREEN = "#4FC96F"
BLUE_GREEN = "#9FAF90"


# FUNCTIONS

# Function to scrape the weather data from the website
def startup(weather_data, codes_to_scrape):
  # Declare variables to be used
  weather_url = ""
  w_year = 0
  w_month = 0
  w_day = 0

  # Extract the most recent date to be scraped from the relevant text file
  w_date_file = open("last_scraped_date.txt", "r")
  content = w_date_file.read()
  w_date = content.split("\n")[0]
  week_count = int(content.split("\n")[1])
  w_date_file.close()
  # Store the day, month and year in the respective variables
  w_year = int(w_date.split("-")[0])
  w_month = int(w_date.split("-")[1])
  w_day = int(w_date.split("-")[2])

  # Extract locations from text file and create tables for each one
  locations = open("locations.txt", "r")
  for line in locations:
    place = line.replace(" ", "_")
    weather_data.execute(
        f"CREATE TABLE IF NOT EXISTS {place} (year INTEGER, week INTEGER, temperature FLOAT, wind_speed FLOAT)"
    )
  locations.close()

  # Define the options of chromedriver, allowing it to run in headless mode + avoid images
  if w_year < CURRENT_YEAR:
    w_options = Options()
    w_options.add_argument('--no-sandbox')
    w_options.add_argument('--disable-dev-shm-usage')
    w_options.add_argument('--headless')
    w_options.add_experimental_option(
      "prefs", {
          "profile.managed_default_content_settings.images": 2,
      })
    w_driver = webdriver.Chrome(options=w_options)
  
  # Iterate until the previous year (2023) has been scraped
  while w_year < CURRENT_YEAR:
    # Iterates through each location
    for code in codes_to_scrape:
      w_city_code = code
      # Puts the date together and inserts it into the URL
      w_date = str(w_year) + "-" + str(w_month) + "-" + str(w_day)
      weather_url = f"https://www.wunderground.com/history/weekly/{w_city_code}/date/{w_date}"
      # Get the page's HTML
      w_driver.get(weather_url)
      time.sleep(5)
      # Store the data held in the summary table of WeatherUnderground
      w_text = w_driver.find_element(By.CLASS_NAME, "summary-table").text

      w_temp = 0.0
      w_wind = 0.0
      for line in w_text.splitlines():
        if "Avg Temperature" in line:
          # Store the temperature in the variable
          w_temp = float(line.split(" ")[3])
        elif "Wind" in line and "(mph)" not in line and "Gust" not in line:
          # Store the wind speed in the variable
          w_wind = float(line.split(" ")[2])

      w_location = interpret_code(w_city_code)
      # Insert the data into the respective table in the database
      weather_data.execute(
          f"INSERT INTO {w_location} (year, week, temperature, wind_speed) VALUES ({w_year}, {week_count}, {w_temp}, {w_wind})"
      )
      w_conn.commit()

    # Increment the date by 7 days, making sure changes between months / years are accounted for
    if w_month == 12 and w_day > 24:      # If the end of the year has been reached...
      w_year += 1
      w_month = 1
      w_day = (w_day + 7) - 31
      week_count = 1
    elif (w_month == 9 or w_month == 4 or w_month == 6
          or w_month == 11) and w_day > 23:      # If the end of a month with 30 days has been reached...
      w_month += 1
      w_day = (w_day + 7) - 30
      week_count += 1
    elif (w_month != 9 and w_month != 4 and w_month != 6
          and w_month != 11 and w_month != 2) and w_day > 24:      # If the end of a month with 31 days has been reached...
      w_month += 1
      w_day = (w_day + 7) - 31
      week_count += 1
    elif w_month == 2 and w_day > 22 and (w_year % 4) == 0:      # If the end of Febraury has been reached and the year is a leap year...
      w_month += 1
      w_day = (w_day + 7) - 29
      week_count += 1
    elif w_month == 2 and w_day > 21 and (w_year % 4) != 0:      # If the end of Febraury has been reached and the year is not a leap year...
      w_month += 1
      w_day = (w_day + 7) - 28
      week_count += 1
    else:      # If the end of a month has not been reached...
      w_day += 7
      week_count += 1
      
    # Add the new date to the text file
    w_date = str(w_year) + "-" + str(w_month) + "-" + str(w_day)
    w_date_file = open("last_scraped_date.txt", "w")
    w_date_file.write(str(w_date))
    w_date_file.write("\n" + str(week_count))
    w_date_file.close()

  # Close the driver
  if w_year < CURRENT_YEAR:
    w_driver.quit()

  store_bird_data()

# Function to convert the city code into the location name
def interpret_code(code):
  location = ""
  if code == "EGNX":
    location = "England"
  elif code == "EGOV":
    location = "Wales"
  elif code == "EGPH":
    location = "Scotland"
  elif code == "EGAC":
    location = "Northern_Ireland"
  return location

# Function to transfer the bird data from the .csv files to the database
def store_bird_data():
  # Extract the bird species that data needs to be stored for
  bird_tables = open("bird_tables.txt", "r")
  bird_names = []
  # Iterate through each species
  for line in bird_tables:
    name = str(line.split())[2:-2]
    bird_names.append(name)
    # Create a table for each bird species
    bird_migration_data.execute(
        f"CREATE TABLE IF NOT EXISTS {name} (year INTEGER, location STRING, peak_population INTEGER, peak_pop_week INTEGER, arrival_week INTEGER, departure_week INTEGER, reporting_rate FLOAT)"
    )
    # Store the path to the relevant .csv file
    data_file_path = f"Bird_Data_Files/{name}_data.csv"
    # Check the file exists and has data in it
    if Path(data_file_path).is_file() and Path(
        data_file_path).stat().st_size > 0:
      # Read the .csv file into a pandas dataframe
      data = pd.read_csv(data_file_path)
      if len(data) > 0:
        # Transfers the data from the dataframe to the database
        data.to_sql(name, b_conn, if_exists="replace", index=False)
        b_conn.commit()
      data.iloc[0:0]
  bird_tables.close()

# Function to remove all widgets from a window's 'content' frame
def clear_window():
  for widget in content.winfo_children():
    widget.destroy()

# Function to create the home page
def home_page(content):
  # Clear the window
  clear_window()
  # Create a text label to greet the user
  home_label_1 = tk.Label(content, text="""Welcome to the Bird Migration Pattern Predictor!

  Here, you can view historical data for 8 migrating bird species to the UK 
  since the year 2000. You can also see weather data for the same time period. 
  Thirdly, you can create a prediction for how those species will behave next 
  year, based on trends in both forms of past data.
  """, font=main_font, bg=LIGHT_GREEN)
  home_label_1.pack()
  # Add the image 'swallows.png' to the window
  home_label_2 = tk.Label(content, image=HOME_PHOTO, width=300, height=210)
  home_label_2.pack()
  # Create a text label to encourage the user to continue
  home_label_3 = tk.Label(content, text="""
  Choose an option from the bar above to get started!

  If you need further assistance, go to the help page for a detailed breakdown 
  of each pages' function.
  """, font=main_font, bg=LIGHT_GREEN)
  home_label_3.pack()

# Function to create the inital predict page
def predict_page(content):
  # Clear the window
  clear_window()
  # Create a text label to direct the user
  predict_label_1 = tk.Label(content, text="Please fill in the fields below to make your prediction:", font=main_font, bg=LIGHT_GREEN)
  predict_label_1.pack()
  # Create the drop-down / check boxes for the user to input their choices
  predict_label_2 = tk.Label(content, text="\nSpecies Name:", font=main_font, bg=LIGHT_GREEN)
  predict_label_2.pack()
  user_species_name = tk.StringVar()
  species_options = ["Arctic Tern", "Cuckoo", "Fieldfare", "House Martin", "Redwing", "Sand Martin", "Swallow", "Swift"]
  predict_entry_1 = tk.OptionMenu(content, user_species_name, *species_options)
  predict_entry_1.pack()
  
  predict_label_3 = tk.Label(content, text="\nLocation Name:", font=main_font, bg=LIGHT_GREEN)
  predict_label_3.pack()
  user_location_name = tk.StringVar()
  location_options = ["England", "Wales", "Scotland", "Northern Ireland"]
  predict_entry_2 = tk.OptionMenu(content, user_location_name, *location_options)
  predict_entry_2.pack()

  predict_label_4 = tk.Label(content, text="\nWeather Type:", font=main_font, bg=LIGHT_GREEN)
  predict_label_4.pack()
  use_temp = tk.BooleanVar()
  predict_choice_1 = tk.Checkbutton(content, text="Temperature", font=(str(main_font), 10), variable=use_temp, bg = LIGHT_GREEN)
  predict_choice_1.pack()
  use_wind = tk.BooleanVar()
  predict_choice_2 = tk.Checkbutton(content, text="Wind Speed", font=(str(main_font), 10), variable=use_wind, bg = LIGHT_GREEN)
  predict_choice_2.pack()

  predict_label_5 = tk.Label(content, text="\nPercentage Weather Change (Optional):", font=main_font, bg=LIGHT_GREEN)
  predict_label_5.pack()
  user_weather_change = tk.DoubleVar()
  predict_entry_3 = tk.Entry(content, textvariable=user_weather_change)
  predict_entry_3.pack()

  # Create a button to submit the user's inputs
  predict_button = tk.Button(content, text="Submit", font=main_font, bg=MID_GREEN, activebackground=OCEAN_GREEN, command=lambda: check_prediction_variables(user_species_name, user_location_name, use_temp, use_wind, user_weather_change, content, predict_label_1))
  predict_button.pack(pady=15)

  # Create a button that gives the user some help if they're unsure
  tip_text = """This is the page for making predictions.
  You can enter the species and location you want to examine, then 
  temperature, wind speed or both. The program will check the 
  relationship between past weather data and bird migration data, 
  then forecast how they will behave next year. You also have the 
  option to increase / decrease the weather strength for next year 
  by a percentage between -40 and 40."""
  help_button = tk.Button(content, text="Help", font=main_font, bg=BLUE_GREEN, activebackground=OCEAN_GREEN, command=lambda: tip_box(content, tip_text))
  help_button.pack()

# Function to briefly explain the function of a window to the user
def tip_box(content, tip_text):
  # Create an alert box window
  tip = Toplevel()
  tip.title("Help")
  # Create a label that tells the user what they can do
  tip_label = tk.Label(tip, text=tip_text)
  tip_label.pack(pady=5)
  # Create a button that navigates to Help
  tip_button_1 = tk.Button(tip, text="Need More Help?", command=lambda: help_page(content=content))
  tip_button_1.pack(pady=5)
  # Create a button that closes the alert window
  tip_button_2 = tk.Button(tip, text="OK", command=tip.destroy)
  tip_button_2.pack(pady=5)

# Function to check the user's inputs and make sure they are valid
def check_prediction_variables(species, location, use_temp, use_wind, weather_change, content, predict_label_1):
  # Gets all values of required variables
  placeholder = (species.get()).lower()
  species = placeholder.replace(" ", "_")
  location = (location.get()).lower()
  use_temp = use_temp.get()
  use_wind = use_wind.get()
  # Validates user inputs
  try:
    raw_value = weather_change.get()
    weather_change = float(raw_value)
  except TclError:
    validate_inputs(species, location, use_temp, use_wind, weather_change, content, predict_label_1)
    return
  if (species != "") and (location != "") and (use_temp or use_wind) and (weather_change <= 40 and weather_change >= -40):
    # Sets weather type depending on values in use_temp and use_wind
    if use_temp and use_wind:
      weather_type = "both"
    elif use_temp and not use_wind:
      weather_type = "temperature"
    elif not use_temp and use_wind:
      weather_type = "wind_speed"
    # Uses the appropriate form for species / location
    species = species.capitalize()
    location = "Northern_Ireland" if location == "northern ireland" else location.capitalize()
    # Copy the image so it can be displayed in a different page
    with open(f"Location_Maps/{location.lower()}.png", "rb") as f_input:
      temp = f_input.read()
    with open("location.png", "wb") as f_output:
      if len(str(temp)) > 0:
        f_output.write(temp)
    # Starts the prediction calculation
    make_prediction(species, location, weather_type, weather_change, content)
  else:
    validate_inputs(species, location, use_temp, use_wind, weather_change, predict_label_1)
    return

# Function to find what is wrong with the user's erroneous inputs
def validate_inputs(species, location, use_temp, use_wind, weather_change, error_label):
  # Create a list to hold the errors
  error_list = []
  error_message = ""
  # Checks the species entered is valid
  if len(species) == 0:
    error_list.append("No Species Entered")
  # Checks the location entered is valid
  if len(location) == 0:
    error_list.append("No Location Entered")
  # Checks if no weather types have been selected
  if not use_temp and not use_wind:
    error_list.append("No Weather Type(s) Selected")
  # Checks data type of percentage change value
  if type(weather_change) != float:
    error_list.append("% Change Must Be Numerical")
  # Checks percentage change is within acceptable boundaries
  if weather_change > 40.0 or weather_change < -40.0:
    error_list.append("% Change Must Be Less Than 40% / More Than -40%")
  # Split the list up for readability
  if len(error_list) >= 3:
      error_list.insert(2,"\n")
  # Create an error message string
  for error in error_list:
      if (error == "\n") or (error == error_list[-1]):
          error_message += error
      else:
          error_message += error + ", "
  # Change the first label on the prediction screen to the error message
  error_label.config(text=error_message, fg="red")
  error_label.pack()

# Function to carry out the prediction for each category of bird data + call the graph creation function for each
def make_prediction(species, location, weather_type, weather_change, content):
  # Predict the peak population
  data_category = "peak_population"
  theoretical_peak_population = get_prediction_value(data_category, species, location, weather_type, weather_change)
  # Set all values to 0 if peak population is <= 0
  if theoretical_peak_population <= 0:
      create_prediction_graph(data_category, species, location, 0, weather_change)
      data_category = "arrival_week"
      create_prediction_graph(data_category, species, location, 0, weather_change)
      data_category = "departure_week"
      create_prediction_graph(data_category, species, location, 0, weather_change)
      data_category = "peak_pop_week"
      create_prediction_graph(data_category, species, location, 0, weather_change)
      data_category = "reporting_rate"
      create_prediction_graph(data_category, species, location, 0.00, weather_change)
  else:
      create_prediction_graph(data_category, species, location, theoretical_peak_population, weather_change)
      # Predict the arrival week
      data_category = "arrival_week"
      theoretical_arrival_week = get_prediction_value(data_category, species, location, weather_type, weather_change)
      create_prediction_graph(data_category, species, location, theoretical_arrival_week, weather_change)
      # Predict the departure week
      data_category = "departure_week"
      theoretical_departure_week = get_prediction_value(data_category, species, location, weather_type, weather_change)
      create_prediction_graph(data_category, species, location, theoretical_departure_week, weather_change)
      # Predict the week of peak population
      data_category = "peak_pop_week"
      theoretical_peak_pop_week = get_prediction_value(data_category, species, location, weather_type, weather_change)
      create_prediction_graph(data_category, species, location, theoretical_peak_pop_week, weather_change)
      # Predict the reporting rate
      data_category = "reporting_rate"
      theoretical_reporting_rate = get_prediction_value(data_category, species, location, weather_type, weather_change)
      create_prediction_graph(data_category, species, location, theoretical_reporting_rate, weather_change)
  
  # Inform the user of the outcome
  notify_user(content, "bird")

# Function to tell the user that their graphs have been created and what to do next
def notify_user(content, type):
  # Create an alert box window
  notify = Toplevel()
  notify.title("Next Stage")
  # Create a label that tells the user what to do
  if type == "bird":
    notify_label = tk.Label(notify, text="Your results have been successfully generated!\nClick on the 'Bird Data View' page to see them.")
  else:
    notify_label = tk.Label(notify, text="Your result has been successfully generated!\nClick on the 'Weather Data View' page to see it.")
  notify_label.pack(pady=5)
  # Create a button that navigates to Data View
  if type == "bird":
    notify_button_1 = tk.Button(notify, text="Take Me There", command=lambda: bird_data_view_page(content))
  else:
    notify_button_1 = tk.Button(notify, text="Take Me There", command=lambda: weather_data_view_page(content))
  notify_button_1.pack(pady=5)
  # Create a button that closes the alert window
  notify_button_2 = tk.Button(notify, text="Close", command=notify.destroy)
  notify_button_2.pack(pady=5)

# Function to calculate the theoretical bird data values
def get_prediction_value(category, species, location, weather_type, weather_change):
  y_data = []
  x_data_1 = []
  x_data_2 = []
  # Iterate through each year
  for year in range(2000,CURRENT_YEAR):
    # Find the data for that category pertaining to that species + add it to the array 'x_data'
    b_query = bird_migration_data.execute(f"SELECT {category} FROM {species} WHERE location = '{location}' AND year = {year}")
    b_data = b_query.fetchall()
    if category == "reporting_rate":
      retrieved_value = float(b_data[0][0])
    else:
      retrieved_value = int(b_data[0][0])
    y_data.append(retrieved_value)
  # Iterate through each year
  year_count = 2000
  for value in y_data:
    # Deal with years with no reported birds at all
    if value == 0:
      x_data_1.append(0)
      if weather_type == "both":
        x_data_2.append(0)
      year_count += 1
    else:
      # Handle a category that isn't measured in weeks
      if category == "peak_population" or category == "reporting_rate":
        # Get the week for that population value / reporting rate
        extra_query = bird_migration_data.execute(f"SELECT peak_pop_week FROM {species} WHERE location = '{location}' AND {category} = {value} AND year = {year_count}")
        extra_data = extra_query.fetchall()
        retrieved_value = int(extra_data[0][0])
        value = retrieved_value
      # Get the weather data for that week
      if weather_type != "both":
        w_query = weather_data.execute(f"SELECT {weather_type} FROM '{location}' WHERE week = {value} AND year = {year_count}")
        w_data = w_query.fetchall()
        retrieved_value = float(w_data[0][0])
        x_data_1.append(retrieved_value)
        year_count += 1
      else:
        w_query = weather_data.execute(f"SELECT temperature FROM '{location}' WHERE week = {value} AND year = {year_count}")
        w_data = w_query.fetchall()
        retrieved_value = float(w_data[0][0])
        x_data_1.append(retrieved_value)
        w_query = weather_data.execute(f"SELECT wind_speed FROM '{location}' WHERE week = {value} AND year = {year_count}")
        w_data = w_query.fetchall()
        retrieved_value = float(w_data[0][0])
        x_data_2.append(retrieved_value)
        year_count += 1
  y_data = np.array(y_data)
  x_data_1 = np.array(x_data_1)
  if len(x_data_2) > 0:
    x_data_2 = np.array(x_data_2)
    # Independant variables (features)
    X = np.column_stack((x_data_1, x_data_2))
  else:
    X = x_data_1
    X = X.reshape(-1, 1)
  # Dependant variable (target)
  Y = y_data
  # Create polynomial features
  poly = PolynomialFeatures(degree = 2)
  X_poly = poly.fit_transform(X)
  # Create + train the polynomial regression model
  model = LinearRegression()
  model.fit(X_poly, Y)
  # Change the last value of x_data_1 by the user's percentage change (if applicable)
  if weather_change > 0:
    last_x_value_1 = x_data_1[-1] * (1 + (weather_change / 100))
  elif weather_change < 0:
    last_x_value_1 = x_data_1[-1] * (1 - (-(weather_change) / 100))
  else:
    last_x_value_1 = x_data_1[-1]
  # Retrieve the last value of the weather array(s)
  if len(x_data_2) > 0:
    # Change the last value of x_data_2 by the user's percentage change (if applicable)
    if weather_change > 0:
      last_x_value_2 = x_data_2[-1] * (1 + (weather_change / 100))
    elif weather_change < 0:
      last_x_value_2 = x_data_2[-1] * (1 - (-(weather_change) / 100))
    else:
      last_x_value_2 = x_data_2[-1]
    next_input = np.array([[last_x_value_1, last_x_value_2]])
  else:
    next_input = np.array([[last_x_value_1]])
  # Predict the next bird data value
  next_input_poly = poly.transform(next_input)
  predicted_value = model.predict(next_input_poly)
  # Cap the week to 52 (53 in leap years) and the reporting rate to 100%
  if (predicted_value > 52) and (category in ["arrival_week", "departure_week", "peak_pop_week"]):
    if (CURRENT_YEAR % 4) == 0:
        predicted_value = 53
    else:
        predicted_value = 52
  elif (predicted_value > 100.00) and (category == "reporting_rate"):
    predicted_value = 100.00
  # Return the final predicted value
  if category == "reporting_rate":
    return(round(predicted_value[0], 2))
  else:
    return(round(predicted_value[0]))

# Function to create the page that displays the data in graph / map form for birds
def bird_data_view_page(content):
  # Clears all widgets so the window can be reused
  clear_window()

  # Create a label that explains the function of the page
  view_label = tk.Label(content, text="Choose the category you want to view:", font=main_font, bg=LIGHT_GREEN)
  view_label.pack()

  # Create a frame for the buttons to make them appear side by side
  button_frame = tk.Frame(content, bg=LIGHT_GREEN)
  button_frame.pack()
  # Create the buttons that determine what graph / map is shown
  b_view_button_1 = tk.Button(button_frame, text="Arrival\nWeek", font=(main_font, 10), bg=MID_GREEN, activebackground=OCEAN_GREEN, command=lambda: set_data_image(view_image, "arrival_week.png"))
  b_view_button_1.pack(side=tk.LEFT, padx=5)
  b_view_button_2 = tk.Button(button_frame, text="Departure\nWeek", font=(main_font, 10), bg=MID_GREEN, activebackground=OCEAN_GREEN, command=lambda: set_data_image(view_image, "departure_week.png"))
  b_view_button_2.pack(side=tk.LEFT, padx=5)
  b_view_button_3 = tk.Button(button_frame, text="Peak\nPopulation", font=(main_font, 10), bg=MID_GREEN, activebackground=OCEAN_GREEN, command=lambda: set_data_image(view_image, "peak_population.png"))
  b_view_button_3.pack(side=tk.LEFT, padx=5)
  b_view_button_4 = tk.Button(button_frame, text="Week of\nPeak Population", font=(main_font, 10), bg=MID_GREEN, activebackground=OCEAN_GREEN, command=lambda: set_data_image(view_image, "peak_pop_week.png"))
  b_view_button_4.pack(side=tk.LEFT, padx=5)
  b_view_button_5 = tk.Button(button_frame, text="Reporting\nRate", font=(main_font, 10), bg=MID_GREEN, activebackground=OCEAN_GREEN, command=lambda: set_data_image(view_image, "reporting_rate.png"))
  b_view_button_5.pack(side=tk.LEFT, padx=5)
  b_view_button_6 = tk.Button(button_frame, text="Location\nMap", font=(main_font, 10), bg=MID_GREEN, activebackground=OCEAN_GREEN, command=lambda: set_data_image(view_image, "location.png"))
  b_view_button_6.pack(side=tk.LEFT, padx=5)

  # Create a label that shows the a default map of the UK with England marked
  data_image = PhotoImage(file="Location_Maps/england.png")
  data_image = data_image.subsample(9,9)
  view_image = tk.Label(content, image=data_image, width=210, height=260)
  view_image.pack(pady=15)
  view_image.image = data_image
  # Save it as a seperate file
  with open("Location_Maps/england.png", "rb") as f_input:
    temp = f_input.read()
  with open("recent_img.png", "wb") as f_output:
    if len(str(temp)) > 0:
      f_output.write(temp)

  # Create a button to open an alert box with a larger image
  view_button_7 = tk.Button(content, text="Enlarge", font=(main_font, 10), bg=MID_GREEN, activebackground=OCEAN_GREEN, command=lambda: enlarge_image("recent_img.png"))
  view_button_7.pack()

  # Create a button that gives the user some help if they're unsure
  tip_text = """This is the page for viewing graphs of bird data.
  You can choose between 5 categories of data and the location above, 
  which will display the related graph / map. If you carried out a 
  prediction, the predicted value will appear as a red dot. If you 
  wish, you can press enlarge on multiple graphs to see them side by 
  side."""
  help_button = tk.Button(content, text="Help", font=main_font, bg=BLUE_GREEN, activebackground=OCEAN_GREEN, command=lambda: tip_box(content, tip_text))
  help_button.pack(pady = 10)

# Function to create the page that displays the data in graph / map form for weather
def weather_data_view_page(content):
  # Clears all widgets so the window can be reused
  clear_window()

  # Create a label that explains the function of the page
  view_label = tk.Label(content, text="Choose the category you want to view:", font=main_font, bg=LIGHT_GREEN)
  view_label.pack()

  # Create a frame for the buttons to make them appear side by side
  button_frame = tk.Frame(content, bg=LIGHT_GREEN)
  button_frame.pack()
  # Create the buttons that determine what graph / map is shown
  w_view_button_1 = tk.Button(button_frame, text="Temperature\n", font=(main_font, 10), bg=MID_GREEN, activebackground=OCEAN_GREEN, command=lambda: set_data_image(view_image, "temperature.png"))
  w_view_button_1.pack(side=tk.LEFT, padx=5)
  w_view_button_2 = tk.Button(button_frame, text="Wind\nSpeed", font=(main_font, 10), bg=MID_GREEN, activebackground=OCEAN_GREEN, command=lambda: set_data_image(view_image, "wind_speed.png"))
  w_view_button_2.pack(side=tk.LEFT, padx=5)
  w_view_button_3 = tk.Button(button_frame, text="Location\nMap", font=(main_font, 10), bg=MID_GREEN, activebackground=OCEAN_GREEN, command=lambda: set_data_image(view_image, "location.png"))
  w_view_button_3.pack(side=tk.LEFT, padx=5)

  # Create a label that shows the a default map of the UK with England marked
  data_image = PhotoImage(file="Location_Maps/england.png")
  data_image = data_image.subsample(9,9)
  view_image = tk.Label(content, image=data_image, width=210, height=260)
  view_image.pack(pady=15)
  view_image.image = data_image
  # Save it as a seperate file
  with open("Location_Maps/england.png", "rb") as f_input:
    temp = f_input.read()
  with open("recent_img.png", "wb") as f_output:
    if len(str(temp)) > 0:
      f_output.write(temp)

  # Create a button to open an alert box with a larger image
  view_button_7 = tk.Button(content, text="Enlarge", font=(main_font, 10), bg=MID_GREEN, activebackground=OCEAN_GREEN, command=lambda: enlarge_image("recent_img.png"))
  view_button_7.pack()

  # Create a button that gives the user some help if they're unsure
  tip_text = """This is the page for viewing graphs of weather data.
  You can choose between 2 categories of data and the location above, 
  which will display the related graph / map. Bear in mind that 
  temperature and wind speed graphs are created one at a time. If you 
  wish, you can press enlarge on multiple graphs to see them side by 
  side."""
  help_button = tk.Button(content, text="Help", font=main_font, bg=BLUE_GREEN, activebackground=OCEAN_GREEN, command=lambda: tip_box(content, tip_text))
  help_button.pack(pady = 10)

# Function to change image on the page that displays data
def set_data_image(view_image, file_path):
  # Create a label that shows the form of data presentation the user wants
  data_image = PhotoImage(file=file_path)
  # Resize the image depending on its shape
  if file_path == "location.png":
    data_image = data_image.subsample(9,9)
    view_image.config(image=data_image, width=210, height=260)
  else:
    data_image = data_image.subsample(2,2)
    view_image.config(image=data_image, width=320, height=240)
  view_image.image = data_image
  # Save the current image as a seperate file
  with open(file_path, "rb") as f_input:
    temp = f_input.read()
  with open("recent_img.png", "wb") as f_output:
    if len(str(temp)) > 0:
      f_output.write(temp)

# Function to create a graph including the new value produced in get_prediction_value
def create_prediction_graph(category, species, location, new_value, percentage):
  x_points = np.array(all_years)
  # Extracts the correct data from the database
  y_points_data = []
  y_points_query = bird_migration_data.execute(f"SELECT {category} FROM {species} WHERE location = '{location}'")
  y_points_data = y_points_query.fetchall()
  # Adds the newly predicted value
  y_points_data.append((new_value,))
  y_points = np.array(y_points_data)
  # Plots a graph using the two arrays
  plt.plot(x_points, y_points, marker = "o", linestyle = "-", color = "blue")
  # Changes the colour of the last point to red
  plt.plot(x_points[-1], y_points[-1], marker = "o", color = "red", markersize = 10)
  # Names the axis and title
  plt.xlabel("Year")
  if category == "peak_population":
    plt.ylabel("Count")
  elif category == "reporting_rate":
    plt.ylabel("Percentage")
  else:
    plt.ylabel("Week")
  # Change the parts of the title derived from variables to be more readable (e.g., no underscores)
  if category == "peak_pop_week":
    graph_category = "week of peak population"
  else:
    graph_category = category.replace("_", " ")
  graph_species = (species.replace("_", " "))
  graph_location = (location.replace("_", " "))
  if percentage < 0.0:
    plt.title(f"Plotting the {graph_category} for {graph_species.title()} in {graph_location.title()} \nwith a {str(percentage)}% decrease in weather magnitude")
  elif percentage > 0.0:
    plt.title(f"Plotting the {graph_category} for {graph_species.title()} in {graph_location.title()} \nwith a {str(percentage)}% increase in weather magnitude")
  else:
    plt.title(f"Plotting the {graph_category} for {graph_species.title()} in \n{graph_location.title()}")
  # Saves the graph
  plt.savefig(f"{category}.png")
  plt.close()

# Function to show a full screen image in an alert box
def enlarge_image(file_path):
  # Create an alert box window
  full = Toplevel()
  full.title("Enlarged Image")
  # Load the image the user is currently viewing
  enl_image = PhotoImage(file=file_path)
  # Resize image if it is too large to display properly
  if enl_image.width() > 640:
    scale_factor = enl_image.width() // 600
    enl_image = enl_image.subsample(scale_factor, scale_factor)
  # Create a label to display the image
  img_label = tk.Label(full, image=enl_image)
  img_label.image = enl_image
  img_label.pack()
  # Create a button that closes the window
  close_button = tk.Button(full, text="Close", command=full.destroy)
  close_button.pack(pady=10)

# Function to create the page used to view historical bird data
def historical_bird_page(content):
  # Clears all widgets so the window can be reused
  clear_window()

  # Create a text label to direct the user
  bird_label_1 = tk.Label(content, text="Please fill in the fields below to display historical bird data:", font=main_font, bg=LIGHT_GREEN)
  bird_label_1.pack()

  # Create the drop-down / check boxes for the user to input their choices
  bird_label_2 = tk.Label(content, text="\nSpecies Name:", font=main_font, bg=LIGHT_GREEN)
  bird_label_2.pack()
  user_species_name = tk.StringVar()
  species_options = ["Arctic Tern", "Cuckoo", "Fieldfare", "House Martin", "Redwing", "Sand Martin", "Swallow", "Swift"]
  bird_entry_1 = tk.OptionMenu(content, user_species_name, *species_options)
  bird_entry_1.pack()
  
  bird_label_3 = tk.Label(content, text="\nLocation Name:", font=main_font, bg=LIGHT_GREEN)
  bird_label_3.pack()
  user_location_name = tk.StringVar()
  location_options = ["England", "Wales", "Scotland", "Northern Ireland"]
  bird_entry_2 = tk.OptionMenu(content, user_location_name, *location_options)
  bird_entry_2.pack()

  bird_label_4 = tk.Label(content, text="\nFirst Year:", font=main_font, bg=LIGHT_GREEN)
  bird_label_4.pack()
  user_first_year = tk.IntVar()
  bird_entry_3 = tk.OptionMenu(content, user_first_year, *all_years[:-1])
  bird_entry_3.pack()

  bird_label_5 = tk.Label(content, text="\nLast Year:", font=main_font, bg=LIGHT_GREEN)
  bird_label_5.pack()
  user_last_year = tk.IntVar()
  bird_entry_4 = tk.OptionMenu(content, user_last_year, *all_years[:-1])
  bird_entry_4.pack()

  # Create a button to submit the user's inputs
  bird_button = tk.Button(content, text="Submit", font=main_font, bg=MID_GREEN, activebackground=OCEAN_GREEN, command=lambda: call_bird_graph(user_species_name, user_location_name, user_first_year, user_last_year, content, bird_label_1))
  bird_button.pack(pady=15)

# Function to create the graphs for historical bird data
def create_bird_graph(category, species, location, f_year, l_year):
  x_points_data = []
  while f_year <= l_year:
    x_points_data.append(f_year)
    f_year += 1
  x_points = np.array(x_points_data)
  # Extracts the correct data from the database
  y_points_data = []
  for i in x_points_data:
    y_points_query = bird_migration_data.execute(f"SELECT {category} FROM {species} WHERE location = '{location}' AND year = {i}")
    y_points_data.append(y_points_query.fetchone())
  y_points = np.array(y_points_data)
  # Plots a graph using the two arrays
  plt.plot(x_points, y_points, marker = "o", linestyle = "-", color = "blue")
  # Names the axis and title
  plt.xlabel("Year")
  if category == "peak_population":
    plt.ylabel("Count")
  elif category == "reporting_rate":
    plt.ylabel("Percentage")
  else:
    plt.ylabel("Week")
  # Change the parts of the title derived from variables to be more readable (e.g., no underscores)
  if category == "peak_pop_week":
    graph_category = "week of peak population"
  else:
    graph_category = category.replace("_", " ")
  graph_species = (species.replace("_", " ")).capitalize()
  graph_location = (location.replace("_", " ")).capitalize()
  plt.title(f"Plotting the {graph_category} for {graph_species} \nin {graph_location} between {str(x_points_data[0])} and {l_year}")
  # Saves the graph
  plt.savefig(f"{category}.png")
  plt.close()

# Function to call the graph creation subroutine
def call_bird_graph(species, location, first_year, last_year, content, error_label):
  # Get the values of the variable inputted
  f_year = first_year.get()
  l_year = last_year.get()
  species = ((species.get()).replace(" ", "_")).lower()
  location = (location.get()).replace(" ", "_")
  # Check all values have been entered
  if len(str(f_year)) == 0 or len(str(l_year)) == 0 or len(species) == 0 or len(location) == 0:
    # Change the first label on the bird data page to the error message
    error_label.config(text="All Inputs Must Be Given", fg="red")
    error_label.pack()
  else:
    # Swap the year variables if the first is greater than the last
    if f_year > l_year:
      f_year, l_year = l_year, f_year
    # Ensure the first and last years are different
    elif f_year == l_year:
      l_year = f_year + 1
    # Plot the graphs for each data category
    fields = ["arrival_week", "departure_week", "peak_population", "peak_pop_week", "reporting_rate"]
    for category in fields:
      create_bird_graph(category, species, location, f_year, l_year)
    # Select the right graph for the location
    location = "Northern_Ireland" if location == "northern ireland" else location.capitalize()
    # Copy the image so it can be displayed in a different page
    with open(f"Location_Maps/{location.lower()}.png", "rb") as f_input:
      temp = f_input.read()
    with open("location.png", "wb") as f_output:
      if len(str(temp)) > 0:
        f_output.write(temp)
    # Alert the user the graphs have been made
    notify_user(content, "bird")

# Function to create the page used to view historical weather data
def historical_weather_page(content):
  # Clears all widgets so the window can be reused
  clear_window()

  # Create a text label to direct the user
  weather_label_1 = tk.Label(content, text="Please fill in the fields below to display historical weather data:", font=main_font, bg=LIGHT_GREEN)
  weather_label_1.pack()

  # Create the drop-down / check boxes for the user to input their choices
  weather_label_2 = tk.Label(content, text="\nWeather Type:", font=main_font, bg=LIGHT_GREEN)
  weather_label_2.pack()
  user_weather_type = tk.StringVar()
  weather_options = ["Temperature", "Wind Speed"]
  weather_entry_1 = tk.OptionMenu(content, user_weather_type, *weather_options)
  weather_entry_1.pack()
  
  weather_label_3 = tk.Label(content, text="\nLocation Name:", font=main_font, bg=LIGHT_GREEN)
  weather_label_3.pack()
  user_location_name = tk.StringVar()
  location_options = ["England", "Wales", "Scotland", "Northern Ireland"]
  weather_entry_2 = tk.OptionMenu(content, user_location_name, *location_options)
  weather_entry_2.pack()

  weather_label_4 = tk.Label(content, text="\nFirst Year:", font=main_font, bg=LIGHT_GREEN)
  weather_label_4.pack()
  user_first_year = tk.IntVar()
  weather_entry_3 = tk.OptionMenu(content, user_first_year, *all_years[:-1])
  weather_entry_3.pack()

  weather_label_5 = tk.Label(content, text="\nLast Year:", font=main_font, bg=LIGHT_GREEN)
  weather_label_5.pack()
  user_last_year = tk.IntVar()
  weather_entry_4 = tk.OptionMenu(content, user_last_year, *all_years[:-1])
  weather_entry_4.pack()

  # Create a button to submit the user's inputs
  weather_button = tk.Button(content, text="Submit", font=main_font, bg=MID_GREEN, activebackground=OCEAN_GREEN, command=lambda: call_weather_graph(user_weather_type, user_location_name, user_first_year, user_last_year, content, weather_label_1))
  weather_button.pack(pady=15)

# Function to create the graphs for historical weather data
def create_weather_graph(weather_type, location, f_year, l_year):
  x_points_data = []
  while f_year <= l_year:
    x_points_data.append(f_year)
    f_year += 1
  x_points = np.array(x_points_data)
  # Extracts the correct data from the database
  y_points_data = []
  for i in x_points_data:
    # Finds the mean for each year
    temp_list = []
    y_points_query = weather_data.execute(f"SELECT {weather_type} FROM {location} WHERE year = {i}")
    temp_list.append(y_points_query.fetchall())
    # Validate temp_list
    if len(temp_list) == 0:
      temp_mean = 0.0
    else:
      temp_mean = np.mean(temp_list)
    y_points_data.append(temp_mean)
  y_points = np.array(y_points_data)
  # Plots a graph using the two arrays
  plt.plot(x_points, y_points, marker = "o", linestyle = "-", color = "blue")
  # Names the axis and title
  plt.xlabel("Year")
  if weather_type == "temperature":
    plt.ylabel("Degrees Farenheit")
  else:
    plt.ylabel("Miles Per Hour")
  # Change the parts of the title derived from variables to be more readable (e.g., no underscores)
  graph_type = (weather_type.replace("_", " ")).lower()
  graph_location = (location.replace("_", " ")).capitalize()
  plt.title(f"Plotting the average {graph_type} in {graph_location} \nbetween {str(x_points_data[0])} and {l_year}")
  # Saves the graph
  plt.savefig(f"{weather_type}.png")
  plt.close()

# Function to call the graph creation subroutine
def call_weather_graph(weather_type, location, first_year, last_year, content, error_label):
  # Get the values of the variable inputted
  f_year = first_year.get()
  l_year = last_year.get()
  weather_type = ((weather_type.get()).replace(" ", "_")).lower()
  location = (location.get()).replace(" ", "_")
  # Check all values have been entered
  if len(str(f_year)) == 0 or len(str(l_year)) == 0 or len(weather_type) == 0 or len(location) == 0:
    # Change the first label on the bird data page to the error message
    error_label.config(text="All Inputs Must Be Given", fg="red")
    error_label.pack()
  else:
    # Swap the year variables if the first is greater than the last
    if f_year > l_year:
      f_year, l_year = l_year, f_year
    # Ensure the first and last years are different
    elif f_year == l_year:
      l_year = f_year + 1
    # Create graph using the user's inputs
    create_weather_graph(weather_type, location, f_year, l_year)
    # Select the right graph for the location
    location = "Northern_Ireland" if location == "northern ireland" else location.capitalize()
    # Copy the image so it can be displayed in a different page
    with open(f"Location_Maps/{location.lower()}.png", "rb") as f_input:
      temp = f_input.read()
    with open("location.png", "wb") as f_output:
      if len(str(temp)) > 0:
        f_output.write(temp)
    # Alert the user the graphs have been made
    notify_user(content, "weather")

# Function to create the page used to explain the program's functions to the user
def help_page(content):
  # Clears all widgets so the window can be reused
  clear_window()

  # Create a text label to direct the user
  help_label_1 = tk.Label(content, text="Here you can find a breakdown of the function of each page:\n", font=main_font, bg=LIGHT_GREEN)
  help_label_1.pack()

  # Create the label that displays the help text
  help_text = """PAST BIRD DATA = Allows you to choose a species and location from the drop-down menus, 
  then a timeframe for the data to be displayed. The data presented will be purely historical for the 
  period you selected. 6 graphs will be created for each category of data, and can be viewed using the 
  'bird data view' page. Data will be outputted by weeks / counts / percentages per year.

  PAST WEATHER DATA = Allows you to choose a type of weather and location from the drop-down menus, 
  then a timeframe for the data to be displayed. The data presented will be purely historical for the 
  period you selected. Only one graph will be produced, which can be viewed using the 'weather data view' 
  page. Data will be outputted by year.

  PREDICT = Forecasts the data for the next year for the species and location you choose. You then pick 
  whether to base predictions off temperature, wind speed or both. You can also (but don't have to) specify 
  a percentage between -40 and 40 that will decrease / increase the value for weather magnitude used for 
  the current year. The 6 graphs produced will have a red dot to show the new value, and can be viewed using 
  the 'data view' page.

  BIRD DATA VIEW = Outputs the graphs from 'past bird data' and 'predict'. 6 graphs will be created with 
  each operation, for the week the birds arrive + depart, their peak population and the week that occurs, 
  the reporting rate (the percentage that the bird is on a yearly list of sightings) and the location in 
  the UK.
  
  WEATHER DATA VIEW = Outputs the graphs from 'past weather data'. Graphs will display for temperature 
  or wind speed, depending on your choice. The map of the location in the UK will also be created each time."""
  help_label_2 = tk.Label(content, text=help_text, font=("Arial", 11), bg=LIGHT_GREEN)
  help_label_2.pack()

# Function to create a credits page
def credits_page(content):
  # Clears all widgets so the window can be reused
  clear_window()

  # Create the labels that give credit to the websites that I used
  credits_label_1 = tk.Label(content, text="Here are the contributors to this project:\n​", font=main_font, bg=LIGHT_GREEN)
  credits_label_1.pack()
  credits_label_2 = tk.Label(content, text="Code and conception: William Lycett", font=main_font, bg=LIGHT_GREEN)
  credits_label_2.pack()
  credits_label_3 = tk.Label(content, text="Bird migration data: BirdTrack by the BTO", font=main_font, bg=LIGHT_GREEN, cursor="hand2")
  credits_label_3.pack()
  credits_label_3.bind("<Button-1>", bird_link)
  credits_label_4 = tk.Label(content, text="Weather data: Weather Underground", font=main_font, bg=LIGHT_GREEN, cursor="hand2")
  credits_label_4.pack()
  credits_label_4.bind("<Button-1>", weather_link)

  # Create the label for the program's disclaimer
  disclaimer = """
  DISCLAIMER: This program should not be used for any proper scientific experiments 
  or calculations, as the model used in this product is unlikely to have the required 
  relationship or range of data to be used in this context. Such use is beyond the 
  scope of this project."""
  credits_label_5 = tk.Label(content, text=disclaimer, font=main_font, bg=LIGHT_GREEN)
  credits_label_5.pack()

# Function to open the link to BirdTrack
def bird_link(event):
  webbrowser.open("https://app.bto.org/birdtrack/explore/outputs.jsp")

# Function to open the link to Weather Underground
def weather_link(event):
  webbrowser.open("https://www.wunderground.com/history")


# MAIN CODE BEGINS

# Create a Tkinter window to be the first screen the user sees
loading = tk.Tk()
global main_font
main_font = font.Font(family="Arial", size=12)
loading.title("Loading...")
loading.option_add("*Font", main_font)
loading.geometry(f"500x100")
loading.resizable(False, False)
loading.config(bg=LIGHT_GREEN)
loading.iconphoto(False, tk.PhotoImage(file="swallows.png"))
loading_label_1 = tk.Label(
    loading,
    text=
    "The Bird Migration Pattern Predictor is ready to launch!\nThis may take a few minutes while we gather any new data.",
    font=main_font,
    bg=LIGHT_GREEN)
loading_label_1.pack(side="top", anchor="center")
# Create a button to close the window + initiate the web scraper
loading_start = tk.Button(loading, text="Let's go!", font=main_font, bg=MID_GREEN, activebackground=OCEAN_GREEN, command=loading.destroy)
loading_start.pack(side="top", anchor="center")
loading.mainloop()

# Call the function to scrape the weather data
startup(weather_data, all_codes)

# Call the function to define the home window
root = tk.Tk()
root.option_add("*Font", main_font)
root.geometry(f"750x500")
root.config(bg=LIGHT_GREEN)
root.resizable(False, False)
root.title("Bird Migration Pattern Predictor")

# Create a menu object
menubar = Menu(root)
# Change the menu bar's colour
menubar.config(bg=GREY_GREEN)
# Apply the menu bar to the window
root.config(menu=menubar)
# Apply all of the menu bar's options
menubar.add_command(label="Home", font=(str(main_font), 10), command=lambda : home_page(content=content))
menubar.add_command(label="Predict", font=(str(main_font), 10), command=lambda : predict_page(content=content))
menubar.add_command(label="Past Bird Data", font=(str(main_font), 10), command=lambda : historical_bird_page(content=content))
menubar.add_command(label="Past Weather Data", font=(str(main_font), 10), command=lambda : historical_weather_page(content=content))
menubar.add_command(label="Bird Data View", font=(str(main_font), 10), command=lambda : bird_data_view_page(content=content))
menubar.add_command(label="Weather Data View", font=(str(main_font), 10), command=lambda : weather_data_view_page(content=content))
menubar.add_command(label="Help", font=(str(main_font), 10), command=lambda : help_page(content=content))
menubar.add_command(label="Credits", font=(str(main_font), 10), command=lambda : credits_page(content=content))

global HOME_PHOTO
HOME_PHOTO = tk.PhotoImage(file="swallows.png")

# Create the 'content' frame that will hold all widgets
content = tk.Frame(root, bg=LIGHT_GREEN)
content.pack()

home_page(content)
root.mainloop()

# Close the database connections
b_conn.close()
w_conn.close()
