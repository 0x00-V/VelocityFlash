from flask import Flask, redirect, url_for, request, session, render_template, flash
from databaseOperations import *
from wtforms.validators import ValidationError



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
        if not email or not password:
            error = "Fill in all fields."
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
def edit_deck(deck_id):
    if session.get('email') == None:
        return redirect(url_for('login'))
    db = DatabaseOperations()
    deck_content = db.DeckView(session.get('email'), deck_id)
    if request.method == 'POST':
        for k,v in request.form.items():
            if "front_new" in k or "back_new" in k:
                if v.replace(" ", "") == "":
                    print("THROW ERROR HERE (Edit_DECK")
        db.EditDeck(session.get('email'), request.form, deck_id)
        return render_template('edit_deck_page.html', session=session, template_deck=deck_content)
    return render_template('edit_deck_page.html', session=session, template_deck=deck_content)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8081)

"""
# TODO
Tidy this up and tighten logic before continuing

Delete individial cards
Delete decks
account input validation - email validation, password req
account page - reset password, change email, 
"""
