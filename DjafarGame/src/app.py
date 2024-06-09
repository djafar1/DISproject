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
import re

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
    
    #Getting all different release years:
    diffyears = '''select DISTINCT EXTRACT(YEAR FROM ReleaseDate) as years FROM video_games ORDER by years DESC;'''
    cur.execute(diffyears)
    years = list(cur.fetchall())
    lengthyears = len(years)

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
            input_userScore = request.form["RAuserScore"].lower()
            return redirect(url_for("querypage", title = input_title, genre=input_genre, releaseDate=input_releaseDate,
                                    userScore=input_userScore))
        length = len(games)
        return render_template("homepage.html", content=games, length=length, randomNumber = randomNumber, genres = genres, lengthgenres = lengthgenres,
                               years = years, lengthyears = lengthyears)

@app.route("/games/<title>/<genre>/<releaseDate>/<userScore>")
def querypage(title, releaseDate, genre, userScore):
    cur = conn.cursor()
    rest = 0

    sqlcode = f'''select * from video_games where '''
    if title != " " :
        sqlcode += f''' title ILIKE '%{title}%' and'''
        rest += 1
    
    if genre != "all":
        sqlcode += f''' genres ILIKE '%{genre}%' and'''
        rest += 1

    if releaseDate != "all":
        sqlcode += f''' EXTRACT(YEAR FROM ReleaseDate) = '{releaseDate}' and'''
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


@app.route("/changepassword", methods=['GET', 'POST'])
def changepassword():

    if request.method == 'POST':
        cur = conn.cursor()
        username = request.form['username']
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if new_password != confirm_password:
            flash("New passwords do not match!")
            return redirect(url_for('changepassword'))

        passtest = f''' SELECT * from users where username = '{username}' and password = '{current_password}' '''

        cur.execute(passtest)

        ifcool = len(cur.fetchall()) != 0

        if ifcool:
            sql1 = "UPDATE users SET password = %s WHERE username = %s"
            cur.execute(sql1,  (new_password, username))
            conn.commit()
            flash("Password successfully changed!")
            session.pop('logged_in', None)
            session.pop('username', None)
            return redirect(url_for('home'))
        else:
            flash("Current password is incorrect!")
            return redirect(url_for('changepassword'))

    return render_template('changepassword.html')

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

    if not session.get('logged_in'):
        return render_template('login.html')

    if request.method == "POST":
        # Add til favourite
        username = session['username']
        action = request.form.get('action')
        try: 
            if action == 'add':
                sql1 = f'''INSERT into favorites(id, username) values ('{gameid}', '{username}') '''
                cur.execute(sql1)
            elif action == 'remove':
                sql1 = f'''DELETE from favorites where id = '{gameid}' and username = '{username}' '''
                cur.execute(sql1)
            if action == 'addWish':
                sql1 = f'''INSERT into wishlist(id, username) values ('{gameid}', '{username}') '''
                cur.execute(sql1)
            elif action == 'removeWish':
                sql1 = f'''DELETE from wishlist where id = '{gameid}' and username = '{username}' '''
                cur.execute(sql1)
            conn.commit()
        except:
            conn.rollback()
            
    sql1 = f''' select * from video_games where id = '{gameid}' '''

    cur.execute(sql1)
    ct = cur.fetchone()

    return render_template("gameProfile.html", content=ct, games=ct)

@app.route("/contact", methods=['POST', 'GET'])
def contact():
    cur = conn.cursor()
    
    if not session.get('logged_in'):
        return render_template('login.html')
    
    if request.method == 'POST':
        new_email = request.form.get('email')
        if new_email and re.match(r"[^@]+@[^@]+\.ku\.dk", new_email):
            cur.execute("SELECT * FROM emails WHERE email = %s", (new_email,))
            unique = cur.fetchall()
            if len(unique) == 0:
                cur.execute("INSERT INTO emails(email) VALUES (%s)", (new_email,))
                conn.commit()
                flash('Email signed up!')
            else:
                flash('Email already exists!')
        else:
            flash('Invalid email format or email is required.')
    else:
        flash(' ')
    return render_template("contact.html")


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True)
