# Setting up the game database :

You need to have a functional Python 3 installation to use the site. 

1. First install all the dependencies using the code below
>$ pip install -r requirements.txt

2. Initialize the 5 necessary database, by running the SQL files
	  psql -d{database} -U{user} -f Favorites.sql
	  psql -d{database} -U{user} -f WishList.sql
	  psql -d{database} -U{user} -f Email.sql
	  psql -d{database} -U{user} -f Create VideoGame.sql
	  psql -d{database} -U{user} -f Create Users.sql
 

3. Go into the app.py file and set your own database, username and password

4. Then you can run Web-App by using the code below
>$ python src/app.py


----------------------------------------------------------------------------------------------

# How to use the application:

1. Create an account 
2. Change password (UPDATE SQL is used he re)
3. login
	if the password is wrong you cant log in
4. frontpage filters (SELECT)
	we used filters with drop down menues and a search bar
5. vaorites and wishlist pages (DELETE and INSERT)
6. contact page (ER is used here)
	you can aónly use @alumni.ku.dk mails 

(1) Create account / You start by pressing the 'Create Account' button, you then get to page where you choose your username and password.

(2) Login / Now you can login on your account by typing in your username and password.

(3) Frontpage / On the frontpage you will see 10 random NFT's (cryptopunks) and some different filter options.

(4) Punks / Each punk have their own page where you can see 'attributes', price and you have the option to add the punk to your favourites.

(5) Searching / You can get to a random punk by pushing the 'random' button, you will also have the option to type in the 'punk ID'.
		On the frontpage the searching is made easy by types you can choose. It can e.g. be a 'male', 'human', 'medium' skin color, 
		then you can type in some specific 'accessories' and at last choose the amount of accessories the punk should have.
		
(6) Accessories / Under 'accessories' you can search for a lot of things e.g. "mohawk", "beard", "earring", "cigarette", "lipstick", "glasses",
		  "nerd glasses", "bandana", "eye patch", "VR", "3D glasses", specfic colors like "green" and etc.

(7) User page / Each user have their own individual page where they can see their favourite punks.

(8) Contact / At last we have a 'contact' page so you have an option to contact the three founders and thank them for their awesome work!


