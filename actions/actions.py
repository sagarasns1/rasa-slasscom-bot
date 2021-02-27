# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, EventType, SessionStarted
from rasa_sdk.executor import CollectingDispatcher

import webbrowser

import sqlite3
import os 

os.chdir("..\\sqlite")
retval = os.getcwd()
conn = sqlite3.connect(str(retval)+'\\slassbot.db')
cursor = conn.execute("ATTACH DATABASE 'slassbot.db' as slassbot;")

class ValidateRegistrationForm(Action):

    def name(self) -> Text:
        return "registration_form"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[EventType]: 
        required_slots = ["PERSON", "phone-number", "number_of_tickets", "is_slasscom_member"]

        for slot_name in required_slots:
            if tracker.slots.get(slot_name) is None:
                # The slot is not filled yet. Request the user to fill this slot next.
                return [SlotSet("requested_slot", slot_name)]        

        # All slots are filled.
        return [SlotSet("requested_slot", None)]

class ActionSubmit(Action):
    def name(self) -> Text:
        return "action_submit"

    def run(self, dispatcher, tracker: Tracker, domain: "DomainDict")-> List[Dict[Text, Any]]:

        is_member = tracker.get_slot("is_slasscom_member")
        cursor = None
        unit_price = None
        if is_member:
            cursor = conn.execute("SELECT unit_price FROM slassbot.ticket_info WHERE user_type='member';")
        else:
            cursor = conn.execute("SELECT unit_price FROM slassbot.ticket_info WHERE user_type='non-member';")
        
        for row in cursor:
            unit_price = float(row[0])

        TKT_CNT = tracker.get_slot("number_of_tickets")
        currency = tracker.get_slot("currency")
        price = int(TKT_CNT) * unit_price

        dispatcher.utter_message(template="utter_user_details", 
        Name = tracker.get_slot("PERSON"), 
        Mobile_number = tracker.get_slot("phone-number"),
        TKT_CNT = tracker.get_slot("number_of_tickets"),
        TKT_PRICE = currency+str("{:.2f}".format(price)))

        return [SlotSet("amount-of-money", price)]

class ActionGetPrice(Action):
    def name(self) -> Text:
        return "action_get_price"

    def run(self, dispatcher, tracker: Tracker, domain: "DomainDict")-> List[Dict[Text, Any]]:

        is_member = tracker.get_slot("is_slasscom_member")
        cursor = None
        unit_price = None
        if is_member:
            cursor = conn.execute("SELECT unit_price FROM slassbot.ticket_info WHERE user_type='member';")
        else:
            cursor = conn.execute("SELECT unit_price FROM slassbot.ticket_info WHERE user_type='non-member';")
        
        for row in cursor:
            unit_price = float(row[0])

        TKT_CNT = tracker.get_slot("number_of_tickets")
        currency = tracker.get_slot("currency")
        price = int(TKT_CNT) * unit_price
        dispatcher.utter_message(template="utter_price_details", TKT_PRICE = currency+str("{:.2f}".format(price)))
        return [SlotSet("amount-of-money", price)]

class ActionRestarted(Action):

    def name(self):
        return "action_chat_restart"

    def run(self, dispatcher, tracker, domain):
        return []

