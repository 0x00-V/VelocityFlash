from flask import Flask, redirect, url_for, request, session, render_template, flash
from databaseOperations import *
from wtforms.validators import ValidationError

import re


def email_check(email_address):
    pattern = r"""
        (?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*
        |"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\[\x01-\x09\x0b\x0c\x0e-\x7f])*")
        @
        (?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?
        |\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\[\x01-\x09\x0b\x0c\x0e-\x7f])+)])
    """
    return bool(re.match(pattern, email_address, re.VERBOSE)) 


app = Flask(__name__)
app.secret_key = 'SuperSecretSecureKey:)'
db_Setup = DatabaseOperations()
db_Setup.initDB()


@app.route("/")
def index():
    return render_template('index.html', session=session)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if session.get('email') != None:
        return redirect(url_for('dashboard'))
    db = DatabaseOperations()
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        print(email_check(email))
        if email.replace(" ", "") == "" or password.replace(" ", "") == "":
            error = "Fill in all fields."
        elif email_check(email) == False:
            error = "Enter a valid email"
        else:
            UserLogin = db.UserLogin(email, password)
            if UserLogin['Success'] == True:
                session['email'] = email
                return redirect(url_for('dashboard'))
            else:
                error = UserLogin['Error']
    return render_template('login.html', session=session,error=error)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if session.get('email') != None:
        return redirect(url_for('dashboard'))
    db = DatabaseOperations()
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if email.replace(" ", "") == "" or password.replace(" ", "") == "":
            error = "Fill in all fields."
        elif email_check(email) == False:
            error = "Enter a valid email"
        elif len(password) < 6:
            error = "Password must be at least 6 characters."
        else:
            RegisterUser = db.RegisterUser(email, password)
            if RegisterUser["Success"] == True:
                flash('Account Created!')
                return redirect(url_for('login'))
            else:
                error = RegisterUser['Error']
    return render_template('register.html', session=session, error=error)


@app.route("/logout", methods=['GET', 'POST'])
def logout():
    if session.get('email') != None:
        session.clear()
    return redirect(url_for('login'))


@app.route("/settings", methods=['GET'])
def settings():
    if session.get('email') == None:
        return redirect(url_for('login'))
    return render_template('settings.html', session=session)


@app.route("/settings/update_password", methods=['GET', 'POST'])
def change_password():
    if session.get('email') == None:
        return redirect(url_for('login'))
    error = None
    if request.method == 'POST':
        db = DatabaseOperations()
        old_pass = request.form.get('old_pass')
        new_pass = request.form.get('new_pass1')
        new_pass1 = request.form.get('new_pass2')
        if old_pass.replace(" ", "") == "" or new_pass.replace(" ", "") == "" or new_pass1.replace(" ", "") == "":
           error = "Fill in all forms."
        elif len(new_pass) < 6:
            error = "New password must be at least 6 characters"
        elif new_pass != new_pass1:
            error = "Passwords do not match."
        else:
            response = db.UpdatePassword(session.get('email'), old_pass, new_pass)
            if response["Success"] == True:
                session.clear()
                return redirect(url_for('login')) 
            else:
                error = "Old password was incorrect."      
    return render_template('change_password.html', session=session, error=error)


@app.route("/dashboard")
def dashboard():
    if session.get('email') == None:
        return redirect(url_for('login'))
    db = DatabaseOperations()
    decks = db.GetDecks(session.get('email'))
    for key, value in decks.items():
        print(f"{key} - {value}")
        
    return render_template('dashboard.html', session=session, template_decks=decks)


@app.route('/new_deck', methods=['GET', 'POST'])
def new_deck():
    if session.get('email') == None:
        return redirect(url_for('login'))
    if request.method == 'POST':
        db = DatabaseOperations()
        email = session.get('email')
        title = request.form.get('title')
        front = request.form.get('front')
        back = request.form.get('back')
        if title.replace(" ", "") == "" or front.replace(" ", "") == "" or back.replace(" ", "") == "":
            flash("Title, Front, or Back must not be blank.")
            return redirect(url_for('new_deck'))
            
        db.NewDeck(email, title, front, back)
        return redirect(url_for('login'))
    return render_template('new_deck.html', session=session)


@app.route('/decks/<int:deck_id>')    
def decks(deck_id):
    if session.get('email') == None:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))


@app.route('/deck/<int:deck_id>')
def deck(deck_id):
    if session.get('email') == None:
        return redirect(url_for('login'))
    db = DatabaseOperations()
    cards = db.GetCards(session.get('email'), deck_id)    
    return render_template('deck_page.html', session=session, template_cards=cards)


@app.route('/edit_deck/<int:deck_id>', methods=['GET', 'POST'])
def edit_deck(deck_id, error=None):
    if session.get('email') == None:
        return redirect(url_for('login'))
    db = DatabaseOperations()
    deck_content = db.DeckView(session.get('email'), deck_id)
    if request.method == 'POST':
        for k,v in request.form.items():
            if k == "title":
                if v.replace(" ", "") == "":
                    print("THROW ERROR HERE (Edit_DECK)")
            if "front_new" in k or "back_new" in k:
                if v.replace(" ", "") == "":
                    print("THROW ERROR HERE (Edit_DECK")
        db.EditDeck(session.get('email'), request.form, deck_id)
        return redirect(url_for('edit_deck', deck_id=deck_id))
    return render_template('edit_deck_page.html', session=session, deck_id=deck_id, template_deck=deck_content)

@app.route('/edit_deck/<int:deck_id>/delete_card/<int:card_id>', methods=['POST'])
def delete_card(deck_id, card_id):
    if session.get('email') == None:
       return redirect(url_for('login'))
    db = DatabaseOperations()
    error = None
    result = db.DeleteCard(session.get('email'), deck_id, card_id)
    if 'Error' in result:
        if result["Error"] == "LastCard":
            error="Deck must have at least 1 card."
    return redirect(url_for('edit_deck', deck_id=deck_id, error=error))    


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8081)

"""
# TODO:
# Delete decks
#account page - change email, 
"""
