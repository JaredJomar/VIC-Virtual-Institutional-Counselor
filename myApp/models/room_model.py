# myApp/models/room_model.py

import psycopg2

class RoomModel:

    def __init__(self, db_url):
        self.db_url = db_url
        self.conn = psycopg2.connect(self.db_url)
    

    def insert_room(self, room_building, room_number, room_capacity):
        cursor = self.conn.cursor()
        query = "insert into room(building, room_number, capacity) values (%s, %s, %s) returning rid"
        cursor.execute(query, (room_building, room_number, room_capacity))
        rid = cursor.fetchone()[0]
        self.conn.commit()
        return rid
    

    def fetch_all_rooms(self):
        cursor = self.conn.cursor()
        query = "select * from room"
        cursor.execute(query)
        retrieved_rooms = cursor.fetchall()
        return retrieved_rooms


    def fetch_room(self, room_id):
        cursor = self.conn.cursor()
        query = "select rid, building, room_number, capacity from room where rid = %s"
        cursor.execute(query, (room_id,))
        found_room = cursor.fetchone()
        return found_room
    

    def update_room(self, room_id, room_building, room_number, room_capacity):
        cursor = self.conn.cursor()
        query = "update room set building=%s, room_number=%s, capacity=%s where rid=%s"
        cursor.execute(query, (room_building, room_number, room_capacity, room_id))
        self.conn.commit()
        return (cursor.rowcount == 1)
    

    def delete_room(self, room_id):
        cursor = self.conn.cursor()
        query = "delete from room where rid = %s"
        cursor.execute (query, (room_id,))
        self.conn.commit()
        return (cursor.rowcount == 1)