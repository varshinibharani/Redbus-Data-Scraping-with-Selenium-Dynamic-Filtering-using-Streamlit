# importing libraries

import pandas as pd
import psycopg2
import streamlit as st
from streamlit_option_menu import option_menu

# Setting up Streamlit page layout
st.set_page_config(layout = 'wide')

# Sidebar for navigation
with st.sidebar:
    web = option_menu(
        menu_title = '🚐 Redbus',
        options = ['Home', 'States and Routes'],
        icons = ['house', 'info-circle']
        )
    
# Content for the 'Home' page
if web == 'Home':
    st.title('Redbus Data Scraping with Selenium & Dynamic Filtering using Streamlit')

    st.subheader(':blue[Domain:] RedBus Transportation')

    st.markdown('#### :blue[Objective:]')
    st.markdown('''The 'Redbus Data Scraping and Dynamic Filtering with Streamlit Application' aims to revolutionize the transportation industry by providing a comprehensive solution for collecting, analyzing, and visualizing bus travel data.''')

    st.markdown('''###### :blue[Selenium:] Selenium is a tool for automating web browsers used for web scraping. It simulates human interactions with web pages to extract data.''')

    st.markdown('''###### :blue[Pandas:] Pandas helps transform datasets from CSV format into structured dataframes for manipulation, cleaning, and preprocessing.''')

    st.markdown('''###### :blue[MySQL:] MySQL is used to establish a connection to a SQL database, integrating and storing transformed data efficiently.''')

    st.markdown('''###### :blue[Streamlit:] Streamlit is used to develop an interactive web application for data visualization and analysis.''')

    st.markdown('#### :blue[Skill Takeaways:]')
    st.markdown('''Selenium, Python, Pandas, psycopg2, Streamlit.''')

    st.markdown('''#### :blue[Developed By:] Jayavarshini''')
    
elif web == 'States and Routes':
    
    client = psycopg2.connect(host="localhost",
                          user="postgres",
                          password="varsha",
                          database="redbus",
                          port="5432")
    
    cursor = client.cursor()

    # Function to format TIME datatype values in the table
    def format_timedelta(td):
        if pd.notnull(td):
            total_seconds = int(td.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            return f"{hours:02}:{minutes:02}"
        return ''

    # Function to fetch distinct states from the table
    def get_states():
        query = "SELECT DISTINCT State_name FROM redbus"
        cursor.execute(query)
        result = cursor.fetchall() # Fetch all rows
        states = [row[0] for row in result]  # Extract state names
        return states

    # Function to fetch routes based on the selected state
    def get_routes_by_state(state):
        query = "SELECT DISTINCT Route_name FROM redbus WHERE State_name = %s"
        cursor.execute(query, (state,))
        result = cursor.fetchall() # Fetch all rows
        routes = [row[0] for row in result]  # Extract route names
        return routes

    # Function to fetch price range based on the selected route
    def get_price_range(route):
        query = "SELECT MIN(Price), MAX(Price) FROM redbus WHERE Route_name = %s"
        cursor.execute(query, (route,))
        result = cursor.fetchone()
        return result  # Returns a tuple (min_price, max_price)
    
    # Function to build and execute the query based on selected filters
    def get_filtered_data(selected_state, selected_route, selected_bus_types, selected_price_ranges, selected_ratings):
        query = "SELECT * FROM redbus WHERE State_name = %s AND Route_name = %s"
        params = [selected_state, selected_route]

        
         # Adding bus type filter
        if selected_bus_types:
            bus_type_conditions = []
            for bus_type in selected_bus_types:
                if bus_type == 'Sleeper':
                    bus_type_conditions.append("Bus_type LIKE '%Sleeper%'")
                elif bus_type == 'Semi-Sleeper':
                    bus_type_conditions.append("Bus_type LIKE '%A/c Semi Sleeper %'")
                else:
                    bus_type_conditions.append("Bus_type NOT LIKE '%Sleeper%' AND Bus_type NOT LIKE '%Semi-Sleeper%'")
            query += " AND (" + " OR ".join(bus_type_conditions) + ")"
        
        # Adding price range filter
        if selected_price_ranges:
            price_conditions = []
            for price_range in selected_price_ranges:
                if price_range == 'Below 500':
                    price_conditions.append("Price < 500")
                elif price_range == '500-1000':
                    price_conditions.append("Price BETWEEN 500 AND 1000")
                elif price_range == 'Above 1000':
                    price_conditions.append("Price > 1000")
            query += " AND (" + " OR ".join(price_conditions) + ")"

        # Adding rating filter
        if selected_ratings:
            rating_conditions = []
            for rating in selected_ratings:
                if rating == 'Below 3 Stars':
                    rating_conditions.append("Ratings < 3")
                elif rating == '3 to 4 Stars':
                    rating_conditions.append("Ratings BETWEEN 3 AND 4")
                elif rating == 'Above 4 Stars':
                    rating_conditions.append("Ratings > 4")
            query += " AND (" + " OR ".join(rating_conditions) + ")"
        
        cursor.execute(query, tuple(params))

        result = cursor.fetchall()
        
        # Convert result to Pandas DataFrame
        columns = [desc[0] for desc in cursor.description]  # Get column names
        df = pd.DataFrame(result, columns = columns)

        # Format Departure and Arrival times
        if 'Departure' in df.columns and 'Arrival' in df.columns:
            df['Departure'] = df['Departure'].apply(format_timedelta)
            df['Arrival'] = df['Arrival'].apply(format_timedelta)

        return df
        
    st.title('Filter Bus Routes by State')

    # Dropdown for selecting a state
    states = get_states()
    selected_state = st.selectbox("Select a State", states)

    # If a state is selected, populate the routes dropdown
    if selected_state:
        routes = get_routes_by_state(selected_state)
        selected_route = st.selectbox("Select a Route", routes)

        # If a route is selected, fetch available price range and provide predefined options
        if selected_route:
            # Hardcoded options for Bus Types, Prices, and Ratings
            bus_type_options = ['Sleeper', 'Seater', 'Others']
            price_options = ['Below 500', '500-1000', 'Above 1000']
            rating_options = ['Below 3 Stars', '3 to 4 Stars', 'Above 4 Stars']
            
            # Create three columns
            col1, col2, col3 = st.columns(3)

            # Column 1: Bus Type Checkboxes
            with col1:
                st.write("Select Bus Types:")
                selected_bus_types = []
                for bus_type in bus_type_options:
                    if st.checkbox(bus_type, key=f"bus_type_{bus_type}"):
                        selected_bus_types.append(bus_type)

            
            # Column 2: Price Range Checkboxes
            with col2:
                st.write("Select Price Ranges:")
                selected_price_ranges = []
                for price_option in price_options:
                    if st.checkbox(price_option):
                        selected_price_ranges.append(price_option)

            # Column 3: Ratings Checkboxes
            with col3:
                st.write("Select Ratings:")
                selected_ratings = []
                for rating in rating_options:
                    if st.checkbox(rating):
                        selected_ratings.append(rating)

            # Fetch the filtered data
            if selected_bus_types or selected_price_ranges or selected_ratings:
                filtered_data = get_filtered_data(selected_state, selected_route, selected_bus_types, selected_price_ranges, selected_ratings)
    
                num_results = len(filtered_data)
                st.write(f"Filtered Results: {num_results} buses available")
                st.dataframe(filtered_data)
                
