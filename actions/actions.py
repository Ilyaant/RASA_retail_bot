from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.events import FollowupAction
from rasa_sdk.events import BotUttered
import sqlite3
from datetime import datetime as dt
import uuid

# change this to the location of your SQLite file
path_to_db = "actions/example.db"
path_to_cl_db = "actions/clients.db"
path_to_ratings_db = "actions/rating.db"

length_size = {
    23.0: 4,
    23.1: 4.5,
    23.2: 4.5,
    23.3: 4.5,
    23.4: 4.5,
    23.5: 5,
    23.6: 5,
    23.7: 5,
    23.8: 5,
    23.9: 5,
    24.0: 5.5,
    24.1: 5.5,
    24.2: 5.5,
    24.3: 5.5,
    24.4: 5.5,
    24.5: 6,
    24.6: 6,
    24.7: 6,
    24.8: 6,
    24.9: 6,
    25.0: 6.5,
    25.1: 6.5,
    25.2: 6.5,
    25.3: 6.5,
    25.4: 6.5,
    25.5: 7,
    25.6: 7.5,
    25.7: 7.5,
    25.8: 7.5,
    25.9: 7.5,
    26.0: 8,
    26.1: 8,
    26.2: 8,
    26.3: 8,
    26.4: 8,
    26.5: 8.5,
    26.6: 8.5,
    26.7: 8.5,
    26.8: 8.5,
    26.9: 8.5,
    27.0: 9,
    27.1: 9,
    27.2: 9,
    27.3: 9,
    27.4: 9,
    27.5: 9.5,
    27.6: 9.5,
    27.7: 9.5,
    27.8: 9.5,
    27.9: 9.5,
    28.0: 10,
    28.1: 10.5,
    28.2: 10.5,
    28.3: 10.5,
    28.4: 10.5,
    28.5: 11,
    28.6: 11,
    28.7: 11,
    28.8: 11,
    28.9: 11,
    29.0: 11.5,
    29.1: 11.5,
    29.2: 11.5,
    29.3: 11.5,
    29.4: 11.5,
    29.5: 12,
    29.6: 12,
    29.7: 12,
    29.8: 12,
    29.9: 12,
    30.0: 12.5,
    30.1: 12.5,
    30.2: 12.5,
    30.3: 12.5,
    30.4: 12.5,
    30.5: 13,
    30.6: 13,
    30.7: 13,
    30.8: 13,
    30.9: 13,
    31.0: 13.5,
    31.1: 13.5,
    31.2: 13.5,
    31.3: 13.5,
    31.4: 13.5,
    31.5: 14
}


class ActionProductSearch(Action):
    def name(self) -> Text:
        return "action_product_search"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # connect to DB
        connection = sqlite3.connect(path_to_db)
        cursor = connection.cursor()

        # get slots and save as tuple
        shoe = [(tracker.get_slot("color")), (tracker.get_slot("size"))]

        # place cursor on correct row based on search criteria
        cursor.execute(
            "SELECT * FROM inventory WHERE color=? AND size=?", shoe)

        # retrieve sqlite row
        data_row = cursor.fetchone()

        if data_row:
            # provide in stock message
            dispatcher.utter_message(template="utter_in_stock")
            connection.close()
            slots_to_reset = ["size", "color"]
            return [SlotSet(slot, None) for slot in slots_to_reset]
        else:
            # provide out of stock
            dispatcher.utter_message(template="utter_no_stock")
            connection.close()
            slots_to_reset = ["size", "color"]
            return [SlotSet(slot, None) for slot in slots_to_reset]


class SurveySubmit(Action):
    def name(self) -> Text:
        return "action_survey_submit"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(template="utter_open_feedback")
        dispatcher.utter_message(template="utter_survey_end")
        return [SlotSet("survey_complete", True)]


class OrderStatus(Action):
    def name(self) -> Text:
        return "action_order_status"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # connect to DB
        connection = sqlite3.connect(path_to_db)
        cursor = connection.cursor()

        # get email slot
        order_email = (tracker.get_slot("email"),)

        # retrieve row based on email
        cursor.execute("SELECT * FROM orders WHERE order_email=?", order_email)
        data_row = cursor.fetchone()

        if data_row:
            # convert tuple to list
            data_list = list(data_row)

            # respond with order status
            dispatcher.utter_message(
                template="utter_order_status", status=data_list[5])
            connection.close()
            return []
        else:
            # db didn't have an entry with this email
            dispatcher.utter_message(template="utter_no_order")
            connection.close()
            return []


class CancelOrder(Action):
    def name(self) -> Text:
        return "action_cancel_order"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # connect to DB
        connection = sqlite3.connect(path_to_db)
        cursor = connection.cursor()

        # get email slot
        order_email = (tracker.get_slot("email"),)

        # retrieve row based on email
        cursor.execute("SELECT * FROM orders WHERE order_email=?", order_email)
        data_row = cursor.fetchone()

        if data_row:
            # change status of entry
            status = [("cancelled"), (tracker.get_slot("email"))]
            cursor.execute(
                "UPDATE orders SET status=? WHERE order_email=?", status)
            connection.commit()
            connection.close()

            # confirm cancellation
            dispatcher.utter_message(template="utter_order_cancel_finish")
            return []
        else:
            # db didn't have an entry with this email
            dispatcher.utter_message(template="utter_no_order")
            connection.close()
            return []


class ReturnOrder(Action):
    def name(self) -> Text:
        return "action_return"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # connect to DB
        connection = sqlite3.connect(path_to_db)
        cursor = connection.cursor()

        # get email slot
        order_email = (tracker.get_slot("email"),)

        # retrieve row based on email
        cursor.execute("SELECT * FROM orders WHERE order_email=?", order_email)
        data_row = cursor.fetchone()

        if data_row:
            # change status of entry
            status = [("returning"), (tracker.get_slot("email"))]
            cursor.execute(
                "UPDATE orders SET status=? WHERE order_email=?", status)
            connection.commit()
            connection.close()

            # confirm return
            dispatcher.utter_message(template="utter_return_finish")
            return []
        else:
            # db didn't have an entry with this email
            dispatcher.utter_message(template="utter_no_order")
            connection.close()
            return []


class GiveName(Action):
    def name(self) -> Text:
        return "action_give_name"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        evt = BotUttered(
            text="my name is bot? idk",
            metadata={
                "nameGiven": "bot"
            }
        )

        return [evt]


class ConsultSize(Action):
    def name(self) -> Text:
        return "action_consult_size"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        length = float(tracker.get_slot("length"))
        your_size = length_size[length]
        dispatcher.utter_message(
            "It looks like your size is {}".format(your_size))
        return []


class ConsultClient(Action):
    def name(self) -> Text:
        return "action_consult_client"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # connect to DB
        connection = sqlite3.connect(path_to_cl_db)
        cursor = connection.cursor()

        name = str(tracker.get_slot("name"))
        phone = str(tracker.get_slot("phone"))
        date = dt.now().strftime('%Y-%m-%d')
        time = dt.now().strftime('%H:%M:%S')

        slots_to_reset = ["name", "phone"]

        if (phone[0] == '+' or phone[0] == '8') and (len(phone) == 12 or len(phone) == 11):
            new_client = (date, time, name, phone)
            cursor.execute('INSERT INTO clients VALUES (?,?,?,?)', new_client)
            connection.commit()
            connection.close()

            dispatcher.utter_message(
                'Thank you, please, wait for the call!')

            return [SlotSet(slot, None) for slot in slots_to_reset]

        else:
            dispatcher.utter_message('Please, enter a valid phone number')
            connection.close()
            return [SlotSet(slot, None) for slot in slots_to_reset]


class OrderShoes(Action):
    def name(self) -> Text:
        return "action_order_shoes"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        size = float(tracker.get_slot("size"))
        color = str(tracker.get_slot("color"))
        email = str(tracker.get_slot("email"))
        type_del = str(tracker.get_slot("type_del"))
        date = dt.now().strftime('%Y-%m-%d')
        id = uuid.uuid1().int
        id_str = str(id)
        id = int(id_str[0:8])
        status = ''
        if type_del == 'self':
            status = 'Delivering to shop'
        else:
            status = 'Delivering to address'

        connection = sqlite3.connect(path_to_db)
        cursor = connection.cursor()

        # get slots and save as tuple
        shoe = [(color), (size)]

        # place cursor on correct row based on search criteria
        cursor.execute(
            "SELECT * FROM inventory WHERE color=? AND size=?", shoe)

        # retrieve sqlite row
        data_row = cursor.fetchone()

        if data_row:
            new_order = (date, id, email, color, size, status)
            cursor.execute(
                'INSERT INTO orders VALUES (?,?,?,?,?,?)', new_order)
            dispatcher.utter_message(template="Your order is created!")
            connection.commit()
            connection.close()
            slots_to_reset = ["size", "color"]
            return [SlotSet(slot, None) for slot in slots_to_reset]
        else:
            # provide out of stock
            dispatcher.utter_message(template="utter_no_stock")
            connection.close()
            slots_to_reset = ["size", "color"]
            return [SlotSet(slot, None) for slot in slots_to_reset]


class CheckOrderNum(Action):
    def name(self) -> Text:
        return "action_check_order_num"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        num = int(tracker.get_slot("order_num"))
        status = 'Finished'
        check = [(num), (status)]
        connection = sqlite3.connect(path_to_db)
        cursor = connection.cursor()
        cursor.execute(
            "SELECT * FROM orders WHERE order_number=? AND status=?", check)
        data_row = cursor.fetchone()
        connection.close()

        if data_row:
            return [SlotSet("order_true", True)]
        else:
            return [SlotSet("order_true", False)]


class RecordFeedback(Action):
    def name(self) -> Text:
        return "action_record_feedback"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        service = int(tracker.get_slot("q_service"))
        convenience = int(tracker.get_slot("q_convenience"))
        shoes = int(tracker.get_slot("q_shoes"))
        num = int(tracker.get_slot("order_num"))

        new_rating = (num, service, convenience, shoes)
        connection = sqlite3.connect(path_to_ratings_db)
        cursor = connection.cursor()
        cursor.execute('INSERT INTO ratings VALUES (?,?,?,?)', new_rating)
        connection.commit()
        dispatcher.utter_message('Thank you for your feedback!')
        connection.close()

        return []
