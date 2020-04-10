#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] =  False
db = SQLAlchemy(app)

migrate = Migrate(app, db)
# DONE: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.String)
    seeking_description = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String(120)), default = ['BLUES'])
    website = db.Column(db.String(500))

    shows = db.relationship('Show', backref = 'venue', lazy= True)
    # DONE: implement any missing fields, as a database migration using Flask-Migrate

    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)), default = ['BLUES'])
    image_link = db.Column(db.String(500))
    address = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.String(120))
    seeking_description = db.Column(db.String)
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(500))
    
    shows = db.relationship('Show', backref = 'artist', lazy = True)
    # DONE: implement any missing fields, as a database migration using Flask-Migrate
    
    def __repr__(self):
      return f'<Artist {self.id} {self.name}>'

# DONE Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = 'Show'
  id = db.Column(db.Integer, primary_key=True)
  id_artist = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable = False)
  id_venue = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable = False)
  start_time = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
  
  def __repr__(self):
      return f'<Shows {self.id} {self.id_artist} {self.id_venue}>'
  
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # DONE: replace with real venues data.
  # DONE: num_shows should be aggregated based on number of upcoming shows per venue.
  data = []

  all_venues = Venue.query.all()

  # get unique cities and states
  cities = []
  for venue in all_venues:
    cities.append(( venue.city, venue.state, venue.id))
  cities = list(set(cities))
  

  for each_city in cities:
    city_dict = {'city': each_city[0], 'state': each_city[1]}
    num_upcoming_shows = len(Show.query.filter_by(id_venue = each_city[2]).all())
    venues_list = []

    for venue in all_venues:
      if venue.city == each_city[0] and venue.state == each_city[1]:
        venues_list.append({'name': venue.name,'id': venue.id})
    city_dict['venues'] = venues_list
    city_dict['num_upcoming_shows'] = num_upcoming_shows
    data.append(city_dict)
  print ('#########: ',data)
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term')
  print  ('### Search Term is: ', search_term)
  # ilike for making case insensitive
  searched_venues = Venue.query.filter(Venue.name.ilike('%'+search_term+'%')).all()
  print (searched_venues)

  response = {}
  response['count'] = len(searched_venues)
  data = []
  for venue in searched_venues:
    data.append({'id':venue.id, 'name': venue.name, 'num_upcoming_shows': 0})
  
  response['data'] = data
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # DONE: replace with real venue data from the venues table, using venue_id
  
  venue = Venue.query.get(venue_id)

  show = Show.query.filter_by(id_venue = venue_id)

  past_shows = []
  upcoming_shows = []

  for each_show in show:
    show_artist = Artist.query.filter_by(id = each_show.id_artist).first()
    show_to_append = {'artist_id': each_show.id_artist,
                        'artist_name': show_artist.name,
                        'artist_image_link': show_artist.image_link,
                        'start_time': str(each_show.start_time)}

    if each_show.start_time<=datetime.now():
      past_shows.append(show_to_append)
    else:
      upcoming_shows.append(show_to_append)

  data={
    "id": venue_id,
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
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  print ('venue_data: ',data)
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # DONE: insert form data as a new Venue record in the db, instead
  # DONE: modify data to be the data object returned from db insertion
  try:
    form = VenueForm()
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']##
    genres = request.form['genres']
    facebook_link = request.form['facebook_link']
    seeking_talent = True #request.form['seeking_talent']
    seeking_description = "Seeking_exceptional Talent" #request.form['seeking_talent_description']
    image_link = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Madison_Square_Garden_%28MSG%29_-_Full_%2848124330357%29.jpg/275px-Madison_Square_Garden_%28MSG%29_-_Full_%2848124330357%29.jpg" #request.form['image_link']

    venue = Venue(name=name, city=city, state = state, 
                  address = address, phone = phone, genres = genres, 
                  facebook_link = facebook_link, seeking_talent = seeking_talent,
                  seeking_description = seeking_description,
                  image_link = image_link)

    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    
  except Exception as e:
    # DONE: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('Venue ' + request.form['name'] + ' Could not be created!')
    db.session.rollback()
    print (e)

  finally:
    db.session.close()


  return render_template('pages/home.html') 

@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
  # DONE: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    flash('Venue ' + str(venue_id) + ' Deleted!')
    db.session.commit()

  except Exception as e:
    print (e)
    db.session.rollback()
    flash('Venue ' + str(venue_id) + ' Could not be deleted!')
  finally:
    db.session.close()
  
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # DONE: replace with real data returned from querying the database

  all_artists = Artist.query.all()
  data = []
  for each_artist in all_artists:
    data.append({'id':each_artist.id, 'name': each_artist.name})
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term = request.form.get('search_term')
  print  ('### Search Term is: ', search_term)
  # ilike for making case insensitive
  searched_artists = Artist.query.filter(Artist.name.ilike('%'+search_term+'%')).all()
  print (searched_artists)

  response = {}
  response['count'] = len(searched_artists)
  data = []
  for artist in searched_artists:
    data.append({'id':artist.id, 'name': artist.name, 'num_upcoming_shows': 0})
  
  response['data'] = data

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # DONE: replace with real venue data from the venues table, using venue_id
  
  artist = Artist.query.get(artist_id)
  show = Show.query.filter_by(id_artist = artist_id)

  past_shows = []
  upcoming_shows = []

  for each_show in show:
    show_artist = Artist.query.filter_by(id = each_show.id_artist).first()
    show_to_append = {'artist_id': each_show.id_artist,
                        'artist_name': show_artist.name,
                        'artist_image_link': show_artist.image_link,
                        'start_time': str(each_show.start_time)}

    if each_show.start_time<=datetime.now():
      past_shows.append(show_to_append)
    else:
      upcoming_shows.append(show_to_append)

  data={
    "id": artist_id,
    "name": artist.name,
    "genres": artist.genres,
    "address": artist.address,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
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
  form = ArtistForm()

  artist = Artist.query.filter_by(id = artist_id).first()

  artist={
    "id": artist_id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link
    }

  # DONE: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # DONE: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  
  try:
    form =ArtistForm()
    artist = Artist.query.filter_by(id = artist_id).first()

    artist.name = request.form['name']
    artist.genres = request.form['genres']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.facebook_link = request.form['facebook_link']
    artist.image_link = 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/GNR_London_Stadium_2017_3_%28cropped%29.jpg/300px-GNR_London_Stadium_2017_3_%28cropped%29.jpg'
    artist.seeking_venue = 'yes'
    artist.seeking_description = 'seeking venues'
    artist.website = 'www.youtube.com'
    db.session.commit()
  except Exception as e:
    print (e)
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.filter_by(id = venue_id).first()

  venue={
    "id": venue_id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": True,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link
  }

  # DONE: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # DONE: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  try:
    form = VenueForm()
    venue = Venue.query.filter_by(id = venue_id).first()

    venue.name = request.form['name']
    venue.genres = request.form['genres']
    venue.address = request.form['address']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.phone = request.form['phone']
    venue.facebook_link = request.form['facebook_link']
    venue.seeking_talent = 'Yes'
    venue.seeking_description = 'Seeking intersting talent'
    venue.image_link = 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Madison_Square_Garden_%28MSG%29_-_Full_%2848124330357%29.jpg/1920px-Madison_Square_Garden_%28MSG%29_-_Full_%2848124330357%29.jpg'
    venue.website = 'www.youtube.com'

  except Exception as e:
    db.session.rollback()

  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # DONE: insert form data as a new Venue record in the db, instead
  # DONE: modify data to be the data object returned from db insertion

  try:
    form = ArtistForm()
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    genres = request.form['genres']
    image_link = 'https://cdn.antenne.de/thumbs/images/galleries/407413/107406_metallica_2018_Ross_Halfin_230916_04283000_crop.b237ccfa.png'
    address = 'Alexanderplatz'
    facebook_link = request.form['facebook_link']
    seeking_venue = 'Yes'
    seeking_description = 'Seeking interesting Venue'
    website = 'www.youtube.com'

    artist = Artist(name=name, city=city, state = state, phone = phone,genres=genres,
    image_link = image_link, address=address, facebook_link= facebook_link, seeking_venue = seeking_venue,
    seeking_description = seeking_description, website= website)

    db.session.add(artist)
    db.session.commit()

    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except Exception as e:
    db.session.rollback()
    print (e)
    flash('Artist ' + request.form['name'] + ' failed to be listed!')
  finally:
    db.session.close()

  # on successful db insert, flash success
  
  # DONE: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # DONE: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  for show in Show.query.all():
    data.append({'venue_id': show.id_venue,
                'venue_name':Venue.query.filter_by(id = show.id_venue).first().name,
                'artist_id':show.id_artist,
                'artist_name': Artist.query.filter_by(id = show.id_artist).first().name,
                'artist_image_link': Artist.query.filter_by(id = show.id_artist).first().image_link,
                'start_time': str(show.start_time) })
  
  '''data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]'''
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # DONE: insert form data as a new Show record in the db, instead
  try:
    id_artist = request.form['artist_id']
    id_venue = request.form['venue_id']
    start_time = request.form['start_time']

    show = Show(id_artist=id_artist, id_venue= id_venue, start_time = start_time)

    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except Exception as e:
    db.session.rollback()
    print (e)
    flash('Show Could not be listed listed!')
  finally:
    db.session.close()
  # on successful db insert, flash success
  
  # DONE: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


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
