#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Based on: https://www.kaggle.com/datasets/arbazmohammad/world-airports-and-airlines-datasets
Sample input: --AIRLINES="airlines.yaml" --AIRPORTS="airports.yaml" --ROUTES="routes.yaml" --QUESTION="q1" --GRAPH_TYPE="bar"
"""
import sys
import os
import yaml
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt

# Define a constant variable to store graph labels and titles
GRAPH_LABELS_TITLES: dict = {
    "q1": {
        "x_label": "Country",
        "y_label": "Number of Routes",
        "title": "Top 20 Airlines to Canada"
    },
    "q2": {
        "x_label": "Country",
        "y_label": "Number of Routes",
        "title": "Top 30 Least Popular Countries to Travel to"
    },
    "q3": {
        "x_label": "Airports",
        "y_label": "Number of Flights",
        "title": "Top 10 Destination Airports"
    },
    "q4": {
        "x_label": "City",
        "y_label": "Number of Flights",
        "title": "Top 15 Destination Cities"
    },
    "q5": {
        "x_label": "From Airline Code - To Airline Code",
        "y_label": "Number of Flights",
        "title": "Top 10 Domestic Canadian Routes"
    }
}

def get_args() -> list:
    """Extracts the values of the command line arguments passed to the script.
        
    Parameters: None   

    Returns: A list of strings, each string being the value of a command line argument.
    """
    # Splitting each argument string by the '=' character and returning the second half
    return [string.split('=')[1] for string in sys.argv[1:]]


def get_DataFrame(file: str) -> pd.DataFrame:
    """Reads a YAML file and converts it to a Pandas DataFrame.

    Parameters: file - The name of the YAML file to read.

    Returns: A Pandas DataFrame containing the data from the YAML file.
    """
    try:
        # Open the file for reading
        with open(file, 'r') as f:
                
            # Load the YAML data into a Python dict
            data: dict = yaml.safe_load(f)

    except FileNotFoundError:
        # If unable to open the file, raise an error
        print("Unable to read the input file: " + file)
        sys.exit(1)

    # Extract the name of the YAML file without the extension
    name: str = file.split('/')[-1].rsplit('.', 1)[0]

    # Convert the data to a Pandas DataFrame and return it
    return pd.DataFrame(data[name])


def get_func(question: str):
    """Returns the function to call for the specified question.

    Parameters: question (str) - The name of the question.

    Returns: func - The function to call for the specified question.
    """
    func_map = {
        'q1': q1,
        'q2': q2,
        'q3': q3,
        'q4': q4,
        'q5': q5,
    }

    func = func_map.get(question)

    # If function is not found, exit the program
    if func is None:
        print(f"Invalid question: {question}")
        sys.exit(1)

    return func


def q1(airlines_df: pd.DataFrame, airports_df: pd.DataFrame, routes_df: pd.DataFrame) -> pd.DataFrame:
    """Returns the top 20 airlines that offer the greatest number of routes with destination country as Canada.

    Parameters: airlines_df (pd.DataFrame) - DataFrame containing information about airlines
                airports_df (pd.DataFrame) - DataFrame containing information about airports
                routes_df (pd.DataFrame) - DataFrame containing information about routes

    Returns:pd.DataFrame - A dataFrame containing the answer
    """
    # Select necessary columns from the tables
    airlines_df = airlines_df[['airline_id', 'airline_name', 'airline_icao_unique_code']]
    airports_df = airports_df[['airport_id', 'airport_country']]
    routes_df = routes_df[['route_airline_id', 'route_to_airport_id']]

    # Merge the tables to get a combined DataFrame of airlines, routes, and airports
    merged_df = pd.merge(airlines_df, routes_df, left_on='airline_id', right_on='route_airline_id')
    merged_all = pd.merge(merged_df, airports_df, left_on='route_to_airport_id', right_on='airport_id')

    # Filter the merged DataFrame to only include rows with destination country as Canada
    canada_df = merged_all[merged_all['airport_country'] == 'Canada']

    # Group the data by airline name and ICAO code, count the number of rows for each group, and sort the groups by count and airline name
    df = canada_df.groupby(['airline_name', 'airline_icao_unique_code'], as_index=False).size().sort_values(by=['size', 'airline_name'], ascending=[False, True]).head(20)

    # Add a new column that combines the airline name and code
    df['subject'] = df['airline_name'].str.strip() + ' (' + df['airline_icao_unique_code'].str.strip() + ')'

    # Return a formatted dataFrame with the answer
    return format_table(df)


def q2(airlines_df: pd.DataFrame, airports_df: pd.DataFrame, routes_df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a formatted dataFrame showing the top 30 countries with the least appearances as a destination country on the routes data.

    Parameters: airlines_df (pd.DataFrame) - DataFrame containing information about airlines
                airports_df (pd.DataFrame) - DataFrame containing information about airports
                routes_df (pd.DataFrame) - DataFrame containing information about routes

    Returns: pd.DataFrame - A dataFrame containing the answer
    """
    # Select necessary columns form the tables
    airports_df = airports_df[['airport_id', 'airport_country']]
    routes_df = routes_df[['route_to_airport_id']]

    # Merge the tables to get a combined DataFrame of airports and routes
    merged_df = pd.merge(airports_df, routes_df, left_on='airport_id', right_on='route_to_airport_id')
    merged_df = merged_df[['airport_country']]

    # Add a new column that contains the country name
    merged_df['subject'] = merged_df['airport_country'].str.strip()
    merged_df = merged_df[['subject']]

    # Group the data by country name, count the number of rows for each group, and sort the groups by count and country name
    df = merged_df.groupby(['subject'], as_index=False).size().sort_values(by=['size', 'subject'], ascending=[True, True]).head(30)

    # Return a formatted dataFrame with the answer
    return format_table(df)
    

def q3(airlines_df: pd.DataFrame, airports_df: pd.DataFrame, routes_df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a formatted table of the top 10 destination airports based on the routes data.

    Parameters: airlines_df (pd.DataFrame) - dataframe containing airline data
                airports_df (pd.DataFrame) - dataframe containing airport data
                routes_df (pd.DataFrame) - dataframe containing routes data

    Returns: pd.DataFrame - A dataFrame containing the answer
    """
    # Select necessary columns from the tables
    airports_df = airports_df[['airport_id', 'airport_name', 'airport_city', 'airport_country', 'airport_icao_unique_code']]
    routes_df = routes_df[['route_to_airport_id']]

    # merge dataframes
    merged_df = pd.merge(airports_df, routes_df, left_on='airport_id', right_on='route_to_airport_id')
    merged_df = merged_df[['airport_name', 'airport_city', 'airport_country', 'airport_icao_unique_code']]

    # group data by airport information and get top 10 destinations
    grouped_df = merged_df.groupby(['airport_name', 'airport_city', 'airport_country', 'airport_icao_unique_code'], as_index=False).size()
    grouped_df = grouped_df.sort_values(by=['size', 'airport_name'], ascending=[False, True]).head(10)

    # format the subject column as a string containing airport information
    grouped_df['subject'] = (grouped_df['airport_name'].str.strip() + ' (' + 
                             grouped_df['airport_icao_unique_code'].str.strip() + '), ' + 
                             grouped_df['airport_city'].str.strip() + ', ' + 
                             grouped_df['airport_country'].str.strip())

    # Return a formatted dataFrame with the answer
    return format_table(grouped_df)

    
def q4(airlines_df: pd.DataFrame, airports_df: pd.DataFrame, routes_df: pd.DataFrame) -> pd.DataFrame:
    """Returns a DataFrame containing the top 15 destination cities by number of routes.
    
    Parameters: airlines_df - A pandas DataFrame containing the airlines data.
                airports_df - A pandas DataFrame containing the airports data.
                routes_df - A pandas DataFrame containing the routes data.
    
    Returns: A pandas DataFrame containing the top 15 destination cities by number of routes, ordered by size in descending order.
    """
    # Select necessary columns from the tables
    airports_df = airports_df[['airport_id', 'airport_city', 'airport_country']]
    routes_df = routes_df[['route_to_airport_id']]

    # Merge airports_df and routes_df on airport_id and route_to_airport_id, respectively
    df = pd.merge(airports_df, routes_df, left_on='airport_id', right_on='route_to_airport_id')#.drop(['airport_id', 'route_to_airport_id'], axis=1)
    df = df[['airport_city', 'airport_country']]

    # Group the DataFrame by airport_city and airport_country and sort by size in descending order
    df = df.groupby(['airport_city', 'airport_country'], as_index=False).size().sort_values(by=['size', 'airport_city'], ascending=[False, True]).head(15)

    # Add a new column 'subject' that combines airport_city and airport_country
    df['subject'] = df['airport_city'].str.strip() + ', ' + df['airport_country'].str.strip()

    # Return a formatted dataFrame with the answer
    return format_table(df)

  
def q5(airlines_df: pd.DataFrame, airports_df: pd.DataFrame, routes_df: pd.DataFrame):
    """Returns a DataFrame containing the top 10 Canadian routes in the format of CYYJ-CYVR (from_code-to_code) with the most difference 
       betwee   # Rename the 'size' column to 'statistic'
    df = df.rename(columns={'size': 'statistic'})n destination and the origin altitude.

    Parameters: airlines_df - A pandas DataFrame containing the airlines data.
                airports_df - A pandas DataFrame containing the airports data.
                routes_df - A pandas DataFrame containning the airports data.

    Returns: A pandas DataFrame containing the top 10 Canadian routes, ordered by size.
    """
    # Select necessary columns from the tables
    routes_df = routes_df[['route_from_aiport_id', 'route_to_airport_id']]
    airports_df = airports_df[['airport_id', 'airport_country', 'airport_icao_unique_code', 'airport_altitude']]
    
    # Get the Canadian airports, and update table
    airports_df = airports_df[airports_df['airport_country'] == "Canada"]
    airports_df = airports_df[['airport_id', 'airport_icao_unique_code', 'airport_altitude']]

    # Get the df with the dest country Canada
    routes_to_canada_df = pd.merge(routes_df, airports_df, left_on="route_to_airport_id", right_on="airport_id")
    routes_to_canada_df = routes_to_canada_df[['route_from_aiport_id', 'route_to_airport_id', 'airport_icao_unique_code', 'airport_altitude']]

    # Get the df with the source counrty Canada
    routes_from_canada_df = pd.merge(routes_df, airports_df, left_on="route_from_aiport_id", right_on="airport_id")
    routes_from_canada_df = routes_from_canada_df[['route_from_aiport_id', 'route_to_airport_id', 'airport_icao_unique_code', 'airport_altitude']]
    
    # Rename the columns so its easier to work with after the merge
    routes_to_canada_df.columns = ['route_from_airport_id_1', 'route_to_airport_id_1', 'airport_icao_unique_code_1', 'to_airport_altitude']
    routes_from_canada_df.columns = ['route_from_airport_id_2', 'route_to_airport_id_2', 'airport_icao_unique_code_2', 'from_airport_altitude']
    
    # Get the domestic canadian flights by merging both both to and from canadian airport flights
    merged_routes_df = pd.merge(routes_to_canada_df, routes_from_canada_df, left_on=["route_from_airport_id_1","route_to_airport_id_1"], \
                                                                            right_on=["route_from_airport_id_2", "route_to_airport_id_2"])
    merged_routes_df = merged_routes_df[['from_airport_altitude', 'to_airport_altitude', 'airport_icao_unique_code_1', 'airport_icao_unique_code_2']]
    
    # Create a new column with the absolute value of the difference in altitudes
    merged_routes_df["statistic"] = abs(merged_routes_df['to_airport_altitude'].astype(float) - merged_routes_df['from_airport_altitude'].astype(float))
    merged_routes_df = merged_routes_df[['statistic', 'airport_icao_unique_code_1', 'airport_icao_unique_code_2']]

    # Sort the dataFrame by the values of the column 'statistic' (the altitude difference) in decending order and keep the top 10
    merged_routes_df = merged_routes_df.sort_values(by="statistic", ascending=False).head(10)

    # create a new column 'subject' with airport codes
    merged_routes_df['subject'] = merged_routes_df['airport_icao_unique_code_2'] + "-" + merged_routes_df['airport_icao_unique_code_1']
   
    # Return a formatted dataFrame with the answer
    return format_table(merged_routes_df)
    

def format_table(df: pd.DataFrame) -> pd.DataFrame:
    """Formats the given DataFrame by renaming the 'size' column to 'statistic' and returning the columns 
    'subject', 'statistic' in that order

    Parameters: df - A DataFrame to be formatted.

    Returns: - A formatted DataFrame.
    """
    # Rename the 'size' column to 'statistic'
    df = df.rename(columns={'size': 'statistic'})

    # Keep the 'subject' and 'statistic' columns and order them as entered
    return df[['subject', 'statistic']]


def output_files(question: str, graph: str, df: pd.DataFrame) -> None:
    """
    Write a given DataFrame to a CSV file named after the provided question.

    If `graph` is "bar", create a bar graph of the data and save it as a PDF file with the same name as the question.

    If `graph` is "pie", create a pie chart of the data and save it as a PDF file with the same name as the question.

    Parameters:question (str) - The name of the question.
                        graph (str) - The type of graph to create. Either "bar" or "pie".
                        df (pd.DataFrame) - The DataFrame to write and graph.

    Returns: None.
    """ 
    # Write the DataFrame to a CSV file with the same name as the question.
    df.to_csv(question + '.csv', index=False)

    # Get the graph labels and titles from the constant variable
    labels_titles = GRAPH_LABELS_TITLES[question]

    if graph == "bar":
        # Create a bar graph and save it as a PDF file with the same name as the question.
        plt.bar(df['subject'], df['statistic'])
        plt.title(labels_titles['title'])
        plt.xlabel(labels_titles['x_label'])
        plt.ylabel(labels_titles['x_label'])
        plt.xticks(rotation=90)
        plt.savefig(question + '.pdf', bbox_inches='tight')
        
    elif graph == "pie":
        # Create a pie chart and save it as a PDF file with the same name as the question.
        fig, ax = plt.subplots(figsize=(20, 20))
        plt.pie(df['statistic'], labels=df['subject'], autopct='%1.1f%%')
        plt.title(labels_titles['title'])
        plt.ylabel(labels_titles['y_label'])
        plt.savefig(question + '.pdf', bbox_inches='tight')


def main() -> None:
    """
    Entry point of the program that solves a problem based on
    command line arguments.
    """
    # Parse command line arguments
    args: list = get_args()
    airlines_input_filename: str = args[0]
    airport_input_filename: str = args[1]
    routes_input_filename: str = args[2]
    question_id: str = args[3]
    type_graph: str = args[4]

    # Load data from input file
    data_dir: str = "Data/"
    airlines_df: pd.DataFrame = get_DataFrame(data_dir + airlines_input_filename)
    airports_df: pd.DataFrame = get_DataFrame(data_dir + airport_input_filename)
    routes_df: pd.DataFrame = get_DataFrame(data_dir + routes_input_filename)

    # Get function based on question ID
    func = get_func(question_id)

    # Call function and get results
    result_df: pd.DataFrame = func(airlines_df, airports_df, routes_df)

    # Write results to output file and generate graph
    output_files(question_id, type_graph, result_df)

    # Exit program
    sys.exit(0)


if __name__ == '__main__':
    main()
