# import the function that will return an instance of a connection
from flask_app.config.mysqlconnection import connectToMySQL
# import a prettier print
from pprint import pprint
from flask import flash
import re
from flask_app.models import entry

DATABASE = 'journal_schema'

class Tag:
    def __init__( self , data ):
        self.id = data['id']
        self.title = data['title']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.entries = []
    
    @classmethod
    def create(cls, data):
        query = 'INSERT INTO tags (title, created_at, updated_at) VALUES (%(title)s, NOW(), NOW());'
        return connectToMySQL(DATABASE).query_db(query, data)
    
    @classmethod
    def select_tag(cls, data):
        query = 'SELECT * FROM tags WHERE title = %(title)s'
        result = connectToMySQL(DATABASE).query_db(query, data)

        if not result:
            return False

        pprint(result[0])

        return cls( result[0] )

    
    @classmethod
    def show_all_tagged(cls, data):
        query = """
                SELECT tags.*, entries.* FROM tags
                LEFT JOIN tag_list ON tag_list.tag_id = tags.id
                LEFT JOIN entries ON entries.id = tag_list.entry_id
                WHERE tags.id = %(id)s and user_id = %(user_id)s;
                """
        results = connectToMySQL(DATABASE).query_db(query, data)

        if not results:
            return False

        tagged = cls(results[0])
        
        for row in results:
            data = {
                'id' : row['entries.id'],
                'title' : row['entries.title'],
                'text' : row['text'],
                'entry_date' : row['entry_date'],
                'created_at' : row['entries.created_at'],
                'updated_at' : row['entries.updated_at'],
            }
            tagged.entries.append( entry.Entry(data) )

        return tagged
        
        
