#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, flash, abort
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    genres = db.Column(db.ARRAY(db.String()))
    address = db.Column(db.String())
    state = db.Column(db.String(120))
    city = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue', cascade='all, delete-orphan')


class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    genres = db.Column(db.ARRAY(db.String()))
    state = db.Column(db.String(120))
    city = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    availability = db.Column(db.String())
    shows = db.relationship('Show', backref='artist', cascade='all, delete-orphan')

class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  artists = Artist.query.with_entities(Artist.id, Artist.name, Artist.city, Artist.state).order_by(Artist.id.desc()).limit(5)
  venues =  Venue.query.with_entities(Venue.id, Venue.name, Venue.city, Venue.state).order_by(Venue.id.desc()).limit(5)
  return render_template('pages/home.html', artists=artists, venues=venues)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # Get all the unique location combinations (state/city) using the DISTINCT keyword
  # So even if there is a similar city in another state (eg. Springfield, Illinois and Springfield, Oregon) it will be different.
  # Order them alphabetically for easier reading 
  locations = Venue.query.with_entities(Venue.state, Venue.city).distinct().order_by(Venue.city, Venue.state)
  data = []
  # Loop through all the locations
  for location in locations:
      # Get the venues that are in that location
      raw_venues = Venue.query.filter_by(state=location.state, city=location.city).all()
      venues = []
      # For each venue there add into a list
      for venue in raw_venues:
          venues.append({'id': venue.id, 'name': venue.name})
      data.append({
          'city': location.city,
          'state': location.state,
          'venues': venues
      })
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  venues = []
  search_pattern = f'%{search_term.strip()}%'
  # If the search term includes a comma then its a location search
  if ',' in search_term :
    city_state = search_term.split(',')
    matching_venues = Venue.query.filter_by(city=city_state[0], state=city_state[1].strip())
  else :
    matching_venues = Venue.query.filter(Venue.name.ilike(search_pattern)).all()
  num_upcoming_shows = 0
  for venue in matching_venues :
    shows = Show.query.filter_by(venue_id=venue.id)
    current_time = datetime.now()
    for show in shows :
      if show.start_time > current_time :
        num_upcoming_shows += 1
    venues.append({
      'id' : venue.id,
      'name' : venue.name,
      'num_upcoming_shows' : num_upcoming_shows
    })
  response={
    "count": len(venues),
    "data": venues
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  # If the query returned no results abort to the 404 page
  if not venue:
    abort(404)
  shows = Show.query.filter_by(venue_id=venue_id)
  past_shows = []
  upcoming_shows = []
  # Temporary object for shows that will be passed to either lists
  show_holder = []
  current_time = datetime.now()
  for show in shows:
    show_holder = {
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": str(show.start_time)
    }
    if show.start_time < current_time:
      past_shows.append(show_holder)
    else :
      upcoming_shows.append(show_holder)
  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link":venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm()
  try:
    seeking_talent = False
    if form.seeking_talent.data == "Yes" :
      seeking_talent = True
    venue = Venue(
      name = form.name.data,
      genres = form.genres.data,
      address = form.address.data,
      state = form.state.data,
      city = form.city.data,
      phone = form.phone.data,
      website = form.website.data,
      facebook_link = form.facebook_link.data,
      seeking_talent = seeking_talent,
      seeking_description = form.seeking_description.data,
      image_link = form.image_link.data
    )
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + form.name.data + ' was successfully listed!')
  except Exception as err:
    db.session.rollback()
    flash('An error occurred. Venue ' + form.name.data + ' could not be listed. ' + str(err))
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except Exception as error:
    flash(str(error))
    db.session.rollback()
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return ('', 204)

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  # If the query returned no results abort to the 404 page
  if not venue:
    abort(404)
  form = VenueForm(obj=venue)
  data ={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address" : venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link":venue.image_link,
  }
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm()
  try:
    venue = Venue.query.get(venue_id)
    seeking_talent = False
    if form.seeking_talent.data == "Yes" :
      seeking_talent = True
    venue.name = form.name.data
    venue.genres = form.genres.data
    venue.state = form.state.data
    venue.city = form.city.data
    venue.address = form.address.data
    venue.phone = form.phone.data
    venue.website = form.website.data
    venue.facebook_link = form.facebook_link.data
    venue.seeking_talent = seeking_talent
    venue.seeking_description = form.seeking_description.data
    venue.image_link = form.image_link.data
    db.session.commit()
    flash('Venue ' + form.name.data + ' was successfully edited!')
  except Exception as err:
    db.session.rollback()
    flash('An error occurred. Venue ' + form.name.data + ' could not be edited. ' + str(err))
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # Sort artists alphabetically for UX
  artists = Artist.query.order_by(Artist.name)
  data = []
  for artist in artists :
    data.append({
      'id' : artist.id,
      'name' : artist.name
    })
  return render_template('pages/artists.html', artists=data)


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm()
  try:
    availabe_dates = []
    seeking_venue = False
    if form.seeking_venue.data == "Yes" :
      seeking_venue = True
    artist = Artist(
      name = form.name.data,
      genres = form.genres.data,
      state = form.state.data,
      city = form.city.data,
      phone = form.phone.data,
      website = form.website.data,
      facebook_link = form.facebook_link.data,
      seeking_venue = seeking_venue,
      seeking_description = form.seeking_description.data,
      image_link = form.image_link.data,
      availability = form.availability.data.strip()
    )
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + form.name.data + ' was successfully listed!')
  except Exception as err:
    db.session.rollback()
    flash('An error occurred. Artist ' + form.name.data + ' could not be listed. ' + str(err))
    #flash(availabe_dates[0])
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  artists = []
  search_pattern = f'%{search_term.strip()}%' 
  if ',' in search_term :
    city_state = search_term.split(',')
    matching_artists = Artist.query.filter_by(city=city_state[0], state=city_state[1].strip())
  else :
    matching_artists = Artist.query.filter(Artist.name.ilike(search_pattern)).all()
  for artist in matching_artists :
    artists.append({
      'id' : artist.id,
      'name' : artist.name,
      'num_upcoming_shows' : 0
    })
  response={
    "count": len(artists),
    "data": artists
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist = Artist.query.get(artist_id)
  # If the query returned no results abort to the 404 page
  if not artist: 
    abort(404)
  shows = Show.query.filter_by(artist_id=artist_id)
  past_shows = []
  upcoming_shows = []
  # Temporary object for shows that will be passed to either lists
  show_holder = []
  current_time = datetime.now()
  for show in shows:
    show_holder = {
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "venue_image_link": show.venue.image_link,
        "start_time": str(show.start_time)
    }
    if show.start_time < current_time:
      past_shows.append(show_holder)
    else :
      upcoming_shows.append(show_holder)
  data ={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link":artist.image_link,
    "availability": artist.availability,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  # If the query returned no results abort to the 404 page
  if not artist:
    abort(404)
  form = ArtistForm(obj=artist)
  data ={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link":artist.image_link,
    "availability": artist.availability
  }
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm()
  try:
    artist = Artist.query.get(artist_id)
    seeking_venue = False
    if form.seeking_venue.data == "Yes" :
      seeking_venue = True
    artist.name = form.name.data
    artist.genres = form.genres.data
    artist.state = form.state.data
    artist.city = form.city.data
    artist.phone = form.phone.data
    artist.website = form.website.data
    artist.facebook_link = form.facebook_link.data
    artist.seeking_venue = seeking_venue
    artist.seeking_description = form.seeking_description.data
    artist.image_link = form.image_link.data
    artist.availability = form.availability.data.strip()
    db.session.commit()
    flash('Artist ' + form.name.data + ' was successfully edited!')
  except Exception as err:
    db.session.rollback()
    flash('An error occurred. Artist ' + form.name.data + ' could not be edited. ' + str(err))
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))




#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  # num_shows should be aggregated based on number of upcoming shows per venue.
  shows = Show.query.all()
  data = []
  for show in shows :
    data.append({
    "venue_id": show.venue_id,
    "venue_name": show.venue.name,
    "artist_id": show.artist_id,
    "artist_name":show.artist.name,
    "artist_image_link": show.artist.image_link,
    "start_time": format_datetime(str(show.start_time))
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm()
  id = form.artist_id.data.strip()
  booking_date = str(form.start_time.data).strip()
  available_dates = str(Artist.query.with_entities(Artist.availability).filter_by(id=id).all())
  # If he has no dates aka no restrictions move on
  if len(available_dates) > 1:
    if booking_date not in available_dates :
      abort(500,'Artist not available at this time')
  try:
    show = Show (
    artist_id = form.artist_id.data,
    venue_id = form.venue_id.data,
    start_time = form.start_time.data
    )
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except Exception as err:
    db.session.rollback()
    flash('An error occurred. Show could not be listed. ' + str(err))
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html', error=error), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
