# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"
import sqlite3
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionSearchProperty(Action):

    def name(self) -> Text:
        return "action_search_property"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        location = tracker.get_slot("location")
        bedrooms = tracker.get_slot("bedrooms")
        bathrooms = tracker.get_slot("bathrooms")
        price = tracker.get_slot("price")
        
        # Establish connection to the sqlite database
        conn = sqlite3.connect("property_listings.db")
        cursor = conn.cursor()
        
        # Build the SQL query based on user criteria
        query = "SELECT * FROM properties WHERE 1=1"
        
        if location:
            query += f" AND location = '{location}'"
            
        if bedrooms:
            query += f" AND bedrooms = '{bedrooms}'"
        if bathrooms:
            query += f" AND bathrooms = '{bathrooms}'"
        if price:
            query += f" AND price <= '{price}'"
            
        # Execute the query and fetch results
        cursor.execute(query)
        results = cursor.fetchall()
        
        # Close the database connection
        conn.close()
        
        if not results:
            dispatcher.utter_message(
                template = "utter_no_properties_found"
            )
        else:
            # Format and send property listings to the user
            property_listings = "\n".join([f"Property ID: {row[0]}, Location: {row[1]}, Bedrooms: {row[2]}, Bathrooms: {row[3]}, Price: ${row[0]}" for row in results])
            
            dispatcher.utter_message(
                template="utter_search_properties",  # will be used in the domain.yml response
                property_listings=property_listings
            )
            
        return []


class ActionScheduleViewing(Action):
    def name(self) -> Text:
        return "action_schedule_viewing"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Extract user input
        location = tracker.get_slot("location")
        viewing_date = tracker.get_slot("viewing_date")
        # You can also extract other relevant information from the user's input

        # Establish a connection to the SQLite database
        conn = sqlite3.connect('property_listings.db')
        cursor = conn.cursor()

        # Insert the viewing information into the database
        cursor.execute("INSERT INTO viewings (location, viewing_date) VALUES (?, ?)", (location, viewing_date))
        conn.commit()
        conn.close()

        # Respond to the user
        dispatcher.utter_message(f"You have successfully scheduled a viewing for {location} on {viewing_date}.")

        return []
    

class ActionGetRecommendations(Action):
    def name(self) -> Text:
        return "action_get_recommendations"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Extract user preferences and criteria (you can customize this part)
        min_bedrooms = tracker.get_slot("min_bedrooms")
        max_price = tracker.get_slot("max_price")
        # You can extract other criteria as needed

        # Establish a connection to the SQLite database
        conn = sqlite3.connect('property_listings.db')
        cursor = conn.cursor()

        # Query the database for property recommendations based on user preferences
        cursor.execute("SELECT location, bedrooms, bathrooms, price FROM properties WHERE bedrooms >= ? AND price <= ?", (min_bedrooms, max_price))
        results = cursor.fetchall()

        if results:
            # Format and send property recommendations to the user
            recommendation_text = "Here are some property recommendations based on your preferences:\n"
            for result in results:
                location, bedrooms, bathrooms, price = result
                recommendation_text += f"Location: {location}, Bedrooms: {bedrooms}, Bathrooms: {bathrooms}, Price: ${price}\n"
            dispatcher.utter_message(
                template="utter_recommendations", #will be used in the domain.yml response
                recommendations=recommendation_text
            )
        else:
            dispatcher.utter_message("Sorry, we couldn't find any properties that match your criteria.")

        conn.close()

        return []