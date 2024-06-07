from flask import Flask, render_template, redirect, url_for, session, abort, request, flash
import requests
from bs4 import BeautifulSoup
import psycopg2
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os
import glob
import pandas as pd
import random

app = Flask(__name__ , static_url_path='/static')

# set your own database name, username and password
db = "dbname='GameThing' user='postgres' host='localhost' password='hmx89ymf'" #potentially wrong password
conn = psycopg2.connect(db)
cursor = conn.cursor()


bcrypt = Bcrypt(app)

@app.route("/createaccount", methods=['POST', 'GET'])
def createaccount():
    cur = conn.cursor()
    if request.method == 'POST':
        new_username = request.form['username']
        new_password = request.form['password']
        cur.execute(f'''select * from users where username = '{new_username}' ''')
        unique = cur.fetchall()
        flash('Account created!')
        if  len(unique) == 0:
            cur.execute(f'''INSERT INTO users(username, password) VALUES ('{new_username}', '{new_password}')''')
            flash('Account created!')
            conn.commit()

            return redirect(url_for("home"))
        else: 
            flash('Username already exists!')


    return render_template("createaccount.html")




@app.route("/", methods=["POST", "GET"])
def home():
    cur = conn.cursor()
    #Getting 10 random rows from Attributes
    tenrand = '''select * from video_games order by random() limit 10;'''
    cur.execute(tenrand)
    games = list(cur.fetchall())
    length = len(games)
    
    #Getting all different genres
    diffgenres = '''select DISTINCT genres FROM video_games;'''
    cur.execute(diffgenres)
    genres = list(cur.fetchall())
    lengthgenres = len(genres)

    #Getting random id from table Attributes
    randint = '''select id from video_games order by random() limit 1;'''
    cur.execute(randint)
    randomNumber = cur.fetchone()[0]
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        if request.method == "POST":
            input_title = request.form["RAtitle"].lower()
            input_genre = request.form["RAgenre"].lower()
            input_releaseDate = request.form["RAreleaseDate"].lower()
            input_developer = request.form["RAdeveloper"].lower()
            input_publisher = request.form["RApublisher"].lower()
            input_userScore = request.form["RAuserScore"].lower()
            input_userRatingsCount = request.form["RAuserRatingsCount"].lower()
            input_id = request.form["gameid"].lower()

            if input_id != "":
                input_id = input_id.zfill(4)
                return redirect(url_for("gamepage", gameid=input_id))
            return redirect(url_for("querypage", title = input_title, genre=input_genre, releaseDate=input_releaseDate, developer=input_developer, publisher=input_publisher,
                                    userScore=input_userScore, userRatingsCount=input_userRatingsCount))
        length = len(games)
        return render_template("homepage.html", content=games, length=length, randomNumber = randomNumber, genres = genres, lengthgenres = lengthgenres)

@app.route("/games/<title>/<genre>/<releaseDate>/<developer>/<publisher>/<userScore>/<userRatingsCount>")
def querypage(title, genre, releaseDate, developer, publisher, userScore, userRatingsCount):
    cur = conn.cursor()
    rest = 0

    sqlcode = f'''select * from video_games where '''
    if title != "all":
        sqlcode += f''' title ILIKE '%{title}%' and'''
        rest += 1
    if genre != "all":
        sqlcode += f''' genres ILIKE '%{genre}%' and'''
        rest += 1
    if releaseDate != "all":
        sqlcode += f''' releaseDate = '{releaseDate}' and'''
        rest += 1

    if developer != "all":
        sqlcode += f''' developer = '{developer}' and'''
        rest += 1

    if publisher != "all":
        sqlcode += f''' publisher = '{publisher}' and'''
        rest += 1

    if userScore != "all":
        if userScore == "0-3":
            sqlcode += ''' userScore BETWEEN 0 AND 3 and'''
        elif userScore == "3-6":
            sqlcode += ''' userScore BETWEEN 3 AND 6 and'''
        elif userScore == "6-9":
            sqlcode += ''' userScore BETWEEN 6 AND 9 and'''
        else:
            sqlcode += f''' userScore = '{userScore}' and'''
        rest += 1
        
    if userRatingsCount != "all":
        sqlcode += f''' userRatingsCount = '{userRatingsCount}' and'''
        rest += 1
        
    if rest == 0: 
        sqlcode = f''' select * from  video_games '''

    else: 
        sqlcode  = sqlcode[:-3]

    cur.execute(sqlcode)
    ct = list(cur.fetchall())

    length = len(ct)

    return render_template("videogames.html", games = ct, length=length)


@app.route('/login', methods=['POST'])
def do_admin_login():
    cur = conn.cursor()
    username = request.form['username']
    password = request.form['password'] 

    insys = f''' SELECT * from users where username = '{username}' and password = '{password}' '''

    cur.execute(insys)

    ifcool = len(cur.fetchall()) != 0

    if ifcool:
        session['logged_in'] = True
        session['username'] = username
    else:
        flash('wrong password!')
    return redirect(url_for("home"))


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()

@app.route("/favorite")
def favorite():
    cur = conn.cursor()
    if not session.get('logged_in'):
        return render_template('login.html')
    
    username = session['username']

    sql1 = f'''
    SELECT vg.title, vg.releasedate, vg.developer, vg.publisher, vg.genres, vg.productrating, vg.userscore, vg.userratingscount, vg.id 
    FROM favorites f
    JOIN video_games vg ON CAST(f.id AS INTEGER) = vg.id 
    WHERE f.username = '{username}'
    '''

    cur.execute(sql1)
    favs = cur.fetchall()
    length = len(favs)
    return render_template("Favorites.html", games=favs, length=length, username = username)

@app.route("/wishlist")
def wishlist():
    cur = conn.cursor()
    if not session.get('logged_in'):
        return render_template('login.html')
    
    username = session['username']

    sql1 = f'''
    SELECT vg.title, vg.releasedate, vg.developer, vg.publisher, vg.genres, vg.productrating, vg.userscore, vg.userratingscount, vg.id 
    FROM wishlist f
    JOIN video_games vg ON CAST(f.id AS INTEGER) = vg.id 
    WHERE f.username = '{username}'
    '''

    cur.execute(sql1)
    wish = cur.fetchall()
    length = len(wish)
    return render_template("wishList.html", games=wish, length=length, username = username)


@app.route("/games")
def videogames():
    cur = conn.cursor()
    if not session.get('logged_in'):
        return render_template('login.html')
    
    sql = '''SELECT * FROM video_games'''
    cur.execute(sql)
    games = cur.fetchall()
    length = len(games)
    return render_template("videogames.html", games = games, length=length)

@app.route("/games/<gameid>", methods=["POST", "GET"])
def gamepage(gameid):
    cur = conn.cursor()
    """
    Instead of PunkID we would have our database content
    for 1 cryptopunk instead.
    """
    if not session.get('logged_in'):
        return render_template('login.html')

    if request.method == "POST":
        # Add til favourite
        username = session['username']
        action = request.form.get('action')
        try: 
            if action == 'add':
                sql1 = f'''insert into favorites(id, username) values ('{gameid}', '{username}') '''
                cur.execute(sql1)
            elif action == 'remove':
                sql1 = f'''delete from favorites where id = '{gameid}' and username = '{username}' '''
                cur.execute(sql1)
            if action == 'addWish':
                sql1 = f'''insert into wishlist(id, username) values ('{gameid}', '{username}') '''
                cur.execute(sql1)
            elif action == 'removeWish':
                sql1 = f'''delete from wishlist where id = '{gameid}' and username = '{username}' '''
                cur.execute(sql1)
            conn.commit()
        except:
            conn.rollback()
            
    sql1 = f''' select * from video_games where id = '{gameid}' '''

    cur.execute(sql1)
    ct = cur.fetchone()

    return render_template("gameProfile.html", content=ct, games=ct)

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True)
