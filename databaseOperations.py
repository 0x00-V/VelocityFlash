import sqlite3, datetime
from werkzeug.security import generate_password_hash, check_password_hash 


class DatabaseOperations:
    def __init__(self):
        self.con = sqlite3.connect("database.db")
        self.con.row_factory = sqlite3.Row
        self.con.execute("PRAGMA foreign_keys = ON")
        self.cur = self.con.cursor()
        
    
    def initDB(self):
        self.cur.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, email TEXT NOT NULL, password TEXT NOT NULL)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS decks(id INTEGER PRIMARY KEY, owner_id INTEGER, created_at TEXT NOT NULL, title TEXT UNIQUE NOT NULL, FOREIGN KEY (owner_id) REFERENCES users(id))")
        self.cur.execute("CREATE TABLE IF NOT EXISTS cards(id INTEGER PRIMARY KEY, deck_id INTEGER, front TEXT NOT NULL, back TEXT NOT NULL, FOREIGN KEY (deck_id) REFERENCES decks(id) ON DELETE CASCADE)")
        self.con.commit()


    def RegisterUser(self, email, password):
        try:
            query = '''SELECT * FROM users WHERE email = ?'''
            self.cur.execute(query, (email,))
            result = self.cur.fetchone()
            if result:
                return {"Success": False, "Error": "Email in use."}
            query = '''INSERT INTO users(email, password) VALUES (?, ?)'''
            password_hashed = generate_password_hash(password)
            self.cur.execute(query, (email, password_hashed,))
            self.con.commit()
            return {"Success": True}
        except sqlite3.OperationalError as error:
            return {"Success": False, "Error": error}
    

    def UserLogin(self, email, password):
        try:
            query = '''SELECT * FROM users WHERE email = ?'''
            self.cur.execute(query, (email,))
            result = self.cur.fetchone()
            if result:
                if check_password_hash(result["password"], password):
                    return {"Success": True, "Email": result["email"]}
            return {"Success": False, "Error": "Incorrect Credentials."}
        except sqlite3.OperationalError as error:
            return {"Success": False, "Error": error}
       
    
    def ValidateSession(self, email):
        try:
            query = 'SELECT id FROM users WHERE email = ?'
            self.cur.execute(query, (email,))
            result = self.cur.fetchone()
            if not result:
                return {"Success": False, "Error": "Could not validate user."}
            return {"Success": True}
        except Exception as error:
            return {"Success": False, "Error": error}

    def UpdatePassword(self, email, old_pass, new_pass):
        try:
            query = '''SELECT * FROM users WHERE email = ?'''
            self.cur.execute(query, (email,))
            result = self.cur.fetchone()
            if result:
                if check_password_hash(result["password"], old_pass):
                    password_hashed = generate_password_hash(new_pass)
                    query = "UPDATE users SET password = ? WHERE email = ?"
                    self.cur.execute(query, (password_hashed, email,))
                    self.con.commit()
                    return {"Success": True}
            return {"Success": False, "Error": "Incorrect Password."}
        except sqlite3.OperationalError as error:
            return {"Success": False, "Error": error}
        

    def NewDeck(self, email, title, front, back):
        try:
            get_userid_query = 'SELECT id FROM users WHERE email = ?'
            self.cur.execute(get_userid_query, (email,))
            result = self.cur.fetchone()
            if not result:
                return {"Success": False, "Error": "Could not validate user."}
            user_id = result["id"]  
            
            query = 'SELECT * FROM decks WHERE owner_id = ? AND title = ?'
            self.cur.execute(query, (user_id, title,))
            result = self.cur.fetchall()
            if len(result) > 0:
                return {"Success": False, "Error": "ERROR (ADD LATER)"}
            
            query = 'INSERT INTO decks(owner_id, created_at, title) VALUES (?, ?, ?)'
            self.cur.execute(query, (user_id, datetime.datetime.now(), title))
            get_deck_id = 'SELECT id FROM decks WHERE title = ?'
            self.cur.execute(get_deck_id, (title,))
            result = self.cur.fetchone()
            if not result:
                return {"Success": False, "Error": "ERROR (ADD LATER)"}
            deck_id = result["id"]

            query = 'INSERT INTO cards(deck_id, front, back) VALUES (?, ?, ?)'
            self.cur.execute(query, (deck_id, front, back))
            self.con.commit()
        except sqlite3.OperationalError as error:
            return {"Success": False, "Error": error}


    def GetDecks(self, email):
        try:
            get_userid_query = 'SELECT id FROM users WHERE email = ?'
            self.cur.execute(get_userid_query, (email,))
            result = self.cur.fetchone()
            if not result:
                return {"Success": False, "Error": "Could not validate user."}
            user_id = result["id"] 
            query = "SELECT id, strftime('%Y-%m-%d %H:%M:%S', created_at) as created_at, title FROM decks WHERE owner_id = ?"
            self.cur.execute(query, (user_id,))
            result = self.cur.fetchall()
            return {"Success": True, "Decks": result}
        except Exception as err:
            return {"Success": False, "Error": err}
    

    def DeckView(self, email, deck_id):
        try:
            get_userid_query = 'SELECT id FROM users WHERE email = ?'
            self.cur.execute(get_userid_query, (email,))
            result = self.cur.fetchone()
            if not result:
                return {"Success": False, "Error": "Could not validate user."}
            user_id = result["id"] 

            query = "SELECT * FROM decks WHERE id = ? AND owner_id = ?"
            self.cur.execute(query, (deck_id, user_id))
            deck_result = self.cur.fetchone()
            if not deck_result:
                return {"Success": False, "Error": "Could not find deck."}
            deck_id = deck_result["id"]

            query = "SELECT id,front,back FROM cards WHERE deck_id = ?"
            self.cur.execute(query, (deck_id,))
            card_result = self.cur.fetchall()
            if not card_result:
                return {"Success": False, "Error": "Could not find any cards."}
            cards = {}
            for row in card_result:
                cards[row[0]] = [row[1], row[2]]
            return {"deck_title": deck_result["title"], "cards": cards}
        except sqlite3.OperationalError as error:
            return {"Success": False, "Error": error}
    

    def GetCards(self, email, deck_id):
        try:
            get_userid_query = 'SELECT id FROM users WHERE email = ?'
            self.cur.execute(get_userid_query, (email,))
            result = self.cur.fetchone()
            if not result:
                return {"Success": False, "Error": "Could not validate user."}
            user_id = result["id"] 
            result = None
            query = "SELECT id FROM decks WHERE owner_id = ? and id = ?"
            self.cur.execute(query, (user_id, deck_id))
            result = self.cur.fetchone()
            if not result:
                return {"Success": False, "Error": "You do not have permission to view this deck."}
            deck_id = result["id"]
            query = "SELECT id,front,back FROM cards WHERE deck_id = ?"
            result = None
            self.cur.execute(query, (deck_id,))
            result = self.cur.fetchall()
            if not result:
                return {"Success": False, "Error": "Deck Empty"}
            cards = {}
            for card in result:
                cards[card[0]] = [card[1], card[2]]
            return cards
        except sqlite3.OperationalError as error:
            return {"Success": False, "Error": error}


    def EditDeck(self, email, updated_deck, deck_id):
        try:
            self.cur.execute('SELECT id FROM users WHERE email = ?', (email,))
            user = self.cur.fetchone()
            if not user:
                return {"Success": False, "Error": "Could not validate user."}
            title = updated_deck.get("title")
            if title:
                self.cur.execute(
                    "UPDATE decks SET title = ? WHERE id = ?",
                    (title, deck_id)
                )
            fronts = {}
            backs = {}
            for k, v in updated_deck.items():
                if k.startswith("front_new_"):
                    idx = k.replace("front_new_", "")
                    fronts[idx] = v

                if k.startswith("back_new_"):
                    idx = k.replace("back_new_", "")
                    backs[idx] = v
            for idx in fronts:
                if idx in backs:
                    f = fronts[idx].strip()
                    b = backs[idx].strip()
                    if f or b:
                        self.cur.execute(
                            "INSERT INTO cards(deck_id, front, back) VALUES (?, ?, ?)",
                            (deck_id, f, b)
                        )
            self.con.commit()
            return {"Success": True}
        except Exception as e:
            return {"Success": False, "Error": str(e)}


    def DeleteCard(self, email, deck_id, card_id):
        try:
            query = 'SELECT id FROM users WHERE email = ?'
            self.cur.execute(query, (email,))
            result = self.cur.fetchone()
            if not result:
                return {"Success": False, "Error": "Could not validate user."}
            user_id = result["id"]
            
            result = None
            query = "SELECT * FROM decks WHERE id = ?"
            self.cur.execute(query, (deck_id,))
            result = self.cur.fetchone()
            if not result:
                return {"Success": False, "Error": "Couldn't locate deck/Couldn't validate ownership of deck"}
            result = None
           
            query = "SELECT COUNT(*) as count FROM cards WHERE deck_id = ?"
            self.cur.execute(query, (deck_id,))
            result = self.cur.fetchone()["count"]
            if result <= 1:
                return {"Success": False, "Error": "LastCard"}
            result = None
            query = "DELETE FROM cards WHERE id = ?"
            self.cur.execute(query, (card_id,))
            result = self.cur.rowcount
            if result > 0:
                self.con.commit()
                return {"Success": True}
            else:
                return {"Success": False}
        except Exception as error:
            return {"Success": False, "Error": error}

    def DeleteDeck(self, email, deck_id):
        try:
            query = 'SELECT id FROM users WHERE email = ?'
            self.cur.execute(query, (email,))
            result = self.cur.fetchone()
            if not result:
                return {"Success": False, "Error": "Could not validate user."}
            user_id = result["id"]
            
            result = None
            query = "SELECT * FROM decks WHERE id = ?"
            self.cur.execute(query, (deck_id,))
            result = self.cur.fetchone()
            if not result:
                return {"Success": False, "Error": "Couldn't locate deck/Couldn't validate ownership of deck"}
            result = None
            query = "DELETE FROM decks WHERE id = ?"
            self.cur.execute(query, (deck_id,))
            result = self.cur.rowcount
            print(result)
            if result > 0:
                self.con.commit()
                return {"Success": True}
            else:
                return {"Success": False}
        except Exception as error:
            return {"Success": False, "Error": error}



def ComparePassword(hashed_password, password):
    if check_password_hash(hashed_password, password):
        return True
    return False