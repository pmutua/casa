import sqlite3
import json

try:
    # Establish connection to the SQLite database
    conn = sqlite3.connect('property_listings.db')
    cursor = conn.cursor()

    # Read property data from JSON file
    with open('default_property_listings.json', 'r') as file:
        property_data = json.load(file)

    # Create a property table if it doesn't exist
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS properties (
                       id INTEGER PRIMARY KEY,
                       location TEXT,
                       bedrooms INTEGER,
                       bathrooms INTEGER,
                       price REAL
                   )
    """)
    
    
    # Create a viewings table if it doesn't exist
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS viewings (
                       id INTEGER PRIMARY KEY,
                       location TEXT,
                       viewing_date TEXT
                   )
    """)

    # Insert the property data into the database
    for prop in property_data:
        location = prop['location']
        bedrooms = prop['bedrooms']
        bathrooms = prop['bathrooms']
        price = prop['price']

        cursor.execute("INSERT INTO properties (location, bedrooms, bathrooms, price) VALUES (?,?,?,?)", (location, bedrooms, bathrooms, price))

    # Commit the changes
    conn.commit()

except sqlite3.Error as e:
    print("SQLite error:", e)

except json.JSONDecodeError as e:
    print("JSON decode error:", e)

finally:
    # Close the connection in a finally block
    if conn:
        conn.close()
