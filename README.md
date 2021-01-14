# Talexus The Talent Nexus

![Showcase.gif](/Showcase.gif)

## Table of Contents

* [Summary](#Summary)

* [Technologies](#Technologies)

* [Features](#Features)

* [Structure](#Structure)

* [Usage and Installation](#usage-and-installation)

## Summary

Talexus is an app to connect artists and venues made using Javascript, Python and Flask that I built to practice full stack programming as part of udacity nanodegree.

## Technologies

Flask was used as a backend using python.  
PostgreSql as the database I used.  
SQLAlchemy as the ORM of choice.  
HTML, CSS, Pure JS, WTForms and Bootstrap was used for the front end.  


## Features

1. Add venues, artist and shows with ease.

2. View the latest additions to the database on the homescreen.

3. Edit options for venues and artist.

4. Restrict booking dates to the ones when the artist is free.

5. View the dates on which the artist will be available.

6. View upcoming and past shows

## Structure
```
+
|   app.py
|   config.py
|   error.log
|   fabfile.py
|   forms.py
|   package-lock.json
|   package.json
|   README.md
|   requirements.txt
|   
+---static
|   +---css
|   |       bootstrap-theme.css
|   |       bootstrap-theme.min.css
|   |       bootstrap.css
|   |       bootstrap.min.css
|   |       bootstrap.min.js
|   |       layout.forms.css
|   |       layout.main.css
|   |       main.css
|   |       main.quickfix.css
|   |       main.responsive.css
|   |       
|   +---fonts
|   |       fontawesome-webfont.eot
|   |       fontawesome-webfont.svg
|   |       fontawesome-webfont.ttf
|   |       fontawesome-webfont.woff
|   |       FontAwesome.otf
|   |       
|   +---ico
|   |       favicon.png
|   |       
|   +---img
|   |       .gitkeep
|   |       front-splash.jpg
|   |       talexus.png
|   |       
|   \---js
|       |   plugins.js
|       |   script.js
|       |   
|       \---libs
|               bootstrap-3.1.1.min.js
|               jquery-1.11.1.min.js
|               jquery-1.11.1.min.map
|               modernizr-2.8.2.min.js
|               moment.min.js
|               respond-1.4.2.min.js
|               
\---templates
    +---errors
    |       404.html
    |       500.html
    |       
    +---forms
    |       edit_artist.html
    |       edit_venue.html
    |       new_artist.html
    |       new_show.html
    |       new_venue.html
    |       
    +---layouts
    |       form.html
    |       main.html
    |       
    \---pages
            artists.html
            home.css
            home.html
            search_artists.html
            search_venues.html
            show.html
            shows.html
            show_artist.html
            show_venue.html
            venues.html
            

```

## Usage and Installation

All the models for the database are already included and ready for use.
You can get the project up and running in 4 simple steps.

1. Use the following command to install the required packages
```
pip install -r requirements.txt
```
```
npm install
```
2. Supply your own Database connection string at config.py
```
SQLALCHEMY_DATABASE_URI = 'CONNECTION STRING HERE'
```
3. Migrate the models to your database
```
set FLASK_APP=ap.py
flask db init
flask db migrate 
flask db upgrade 
```
4. Use The following command to start the server and voila!
```
set FLASK_APP=ap.py
flask run
```
