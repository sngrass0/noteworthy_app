# import the function that will return an instance of a connection
from flask_app.config.mysqlconnection import connectToMySQL
# import a prettier print
from pprint import pprint
from flask import flash
from flask_app.models import tag

DATABASE = 'journal_schema'

class Entry:
    def __init__(self, data):
        self.id = data['id']
        self.title = data['title']
        self.text = data['text']
        self.entry_date = data['entry_date']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.tags = []
    
    @classmethod
    def create(cls, data):
        query = 'INSERT INTO entries (user_id, text, title, entry_date, created_at, updated_at) VALUES (%(user_id)s, %(text)s, %(title)s, %(entry_date)s, NOW(), NOW());'
        return connectToMySQL(DATABASE).query_db(query, data)
    
    @classmethod
    def add_to_tag_list(cls, data):
        query = 'INSERT INTO tag_list (entry_id, tag_id) VALUES (%(entry_id)s, %(tag_id)s);'
        return connectToMySQL(DATABASE).query_db(query, data)

    # i have NO IDEA if this will work or not TTTTT
    @classmethod
    def create_new_entry(cls, data):
        # tags
        tag_item = tag.Tag.select_tag({'title' : data['title']})
        # if tag already in the tags table 
        if not tag_item:
            tag_id = tag.Tag.create({'title' : data['title']}) 
        else:
            tag_id = tag_item.id
        
        return cls.add_to_tag_list({'entry_id' : data['entry_id'], 'tag_id' : tag_id})

    @classmethod
    def get_all_user_posts(cls, data):
        query = "SELECT * FROM entries WHERE user_id = %(user_id)s ORDER BY entry_date DESC;"
        results = connectToMySQL(DATABASE).query_db(query, data)
        pprint(results)

        entries = []

        for entry in results:
            entries.append( cls(entry) )

        return entries

    @classmethod
    def update_entry(cls, data):
        query = "UPDATE entries SET title = %(title)s, text = %(text)s, updated_at = NOW() WHERE id = %(id)s;"
        return connectToMySQL(DATABASE).query_db(query, data)
    
    @classmethod
    def delete_entry(cls, data):
        query = "DELETE FROM entries WHERE id = %(id)s;"
        return connectToMySQL(DATABASE).query_db(query, data)
    
    @classmethod
    def delete_tag_from_list(cls, data):
        query = "DELETE FROM tag_list WHERE id = %(id)s"
        return connectToMySQL(DATABASE).query_db(query, data)
    
    @classmethod
    def delete_all_entry_tags(cls,data):
        query = "DELETE FROM tag_list WHERE entry_id = %(entry_id)s"
        return connectToMySQL(DATABASE).query_db(query, data)

    @classmethod
    def get_by_date(cls, data):
        query = """
                SELECT entries.*, tags.* FROM entries 
                LEFT JOIN tag_list ON tag_list.entry_id = entries.id
                LEFT JOIN tags ON tags.id = tag_list.tag_id
                WHERE user_id = %(user_id)s and entry_date = %(entry_date)s;
            """
        results = connectToMySQL(DATABASE).query_db(query, data)

        if not results:
            return False

        entry = cls( results[0] )
        print(results)
        
        for row in results:
            data = {
                'id' : row['tags.id'],
                'title' : row['tags.title'],
                'created_at' : row['tags.created_at'],
                'updated_at' : row['tags.updated_at'],
            }
            entry.tags.append( tag.Tag(data) )
        
        return entry

    @classmethod 
    def get_most_recent(cls, data):
        query = "SELECT * FROM entries WHERE user_id = %(user_id)s ORDER BY updated_at DESC LIMIT 5;"
        results = connectToMySQL(DATABASE).query_db(query, data)

        pprint(results)

        if not results:
            return False
        
        entries = []

        for entry in results:
            entries.append( cls(entry) )
        
        return entries