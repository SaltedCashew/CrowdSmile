from flask import Flask, Response, request, render_template, g, redirect, url_for
from pydub import AudioSegment
from twilio.rest import TwilioRestClient
from conf import account_sid, auth_token
from flask.ext.cors import CORS, cross_origin

from os.path import exists
from os import makedirs, walk
from random import randint
import sqlite3

DATABASE = 'database.db'

client = TwilioRestClient(account_sid, auth_token)
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Database handling
def connect_to_database():
    return sqlite3.connect(DATABASE)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/table/create')
def create_table():
    cursor = get_db().cursor()
    cursor.execute('CREATE TABLE users(id INTEGER PRIMARY KEY, phone TEXT, city TEXT, happines INTEGER)')
    get_db().commit()
    return 'OK'


# Get happines
def get_happines(city):
    return randint(0, 100)


# Home page
@app.route('/')
def hello():
    return 'Hello, Flask!'


# Create a new card
@app.route('/smile')
def smile():
    directory = 'cards'
    f = []
    for (dirpath, dirnames, filenames) in walk(directory):
        f.extend(dirnames)
        break
    new_dirname = int(f[-1]) + 1
    print new_dirname
    return redirect(url_for('show_card', card_id=new_dirname))


# Get the new card's id
@app.route('/getsmile')
def getsmile():
    directory = 'cards'
    f = []
    for (dirpath, dirnames, filenames) in walk(directory):
        f.extend(dirnames)
        break
    new_dirname = int(f[-1]) + 1
    return str(new_dirname)


# Show the card with the ability to record
@app.route('/<int:card_id>')
def show_card(card_id):
    directory = 'cards/' + str(card_id)
    print directory
    if not exists(directory):
        print 'Directory', directory, 'does not exist yet.'
        makedirs(directory)
    else:
        print 'Directory', directory, 'already exists.'

    f = []
    for (dirpath, dirnames, filenames) in walk(directory):
        f.extend(filenames)
        break

    if len(f) >= 3:
        return 'Card is already completed'
    else:
        return render_template('card.html', directory=directory)

    return 'OK'


@app.route('/play/<card_id>', methods=['GET', 'POST'])
def play(card_id):
    xml = '<?xml version="1.0" encoding="UTF-8"?><Response><Play>http://exodia.ngrok.com/static/cards/' + card_id + '.wav</Play><Redirect/></Response>'
    return Response(xml, mimetype='text/xml')


# Print a list of all users
@app.route('/users')
def users():
    for user in query_db('select * from users ORDER BY happines ASC'):
        print user['id'], user['phone'], user['city'], user['happines']
    return 'OK'


# Call one unhappy person
'''
@app.route('/call')
def test():
    call = client.calls.create(
        to="+447933225896",
        from_="+441228830148",
        url="http://exodia.ngrok.com/play/2"
    )
    return 'OK'
'''

# Receive an unhappy's person call
@app.route('/receive', methods=['GET', 'POST'])
def receive():
    if request.method == 'POST':
        from_number = request.values.get('From', None)
        city = request.values.get('Body', None)
        print from_number, city

        happines = get_happines(city)
        print happines

        cursor = get_db().cursor()
        cursor.execute("INSERT INTO users(phone, city, happines) VALUES(?, ?, ?)", (from_number, city, happines))
        get_db().commit()
        return 'OK'


# Upload a happy person's audio
@app.route('/audio/<card_id>', methods=['GET', 'POST'])
@cross_origin()
def audio(card_id):
    print 'Audio request: ', card_id

    if request.method == 'POST':
        audio_file = request.files['file']
        filename = audio_file.filename
        print filename
        
        directory = 'cards/' + card_id
        if not exists(directory):
            print 'Directory', directory, 'does not exist yet.'
            makedirs(directory)
        else:
            print 'Directory', directory, 'already exists.'

        f = []
        for (dirpath, dirnames, filenames) in walk(directory):
            f.extend(filenames)
            break

        if (len(f) >= 3):
            return 'used'

        audio_file.save(directory + '/sound' + str(len(f) + 1) + '.wav')

        if len(f) == 2:
            sound1 = AudioSegment.from_file(directory + "/sound1.wav")
            sound2 = AudioSegment.from_file(directory + "/sound2.wav")
            sound3 = AudioSegment.from_file(directory + "/sound3.wav")
            
            combined1 = sound1.overlay(sound2)
            combined2 = combined1.overlay(sound3)

            combined2.export('static/cards/' + card_id + '.wav', format='wav')

            # Get the unhappiest user
            user = query_db('select * from users ORDER BY happines ASC', one=True)
            if user is None:
                return 'overflow'
            else:
                print user['id'], user['phone'], user['city'], user['happines']

                call = client.calls.create(
                    to=user['phone'],
                    from_="+441228830148",
                    url="http://exodia.ngrok.com/play/" + card_id
                )

                get_db().cursor().execute("delete from users where id='%d'" % user['id'])
                get_db().commit()

                return 'full'
        else:
            return 'partial'

    return 'OK'

if __name__ == "__main__":
    app.run()
