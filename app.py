#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for,jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime
import datetime
from models import app, db, Venue, Artist, Show
from forms import VenueForm
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#


moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

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
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
 data_venues = Venue.query.all()
 data = []
 for venue in data_venues:
    area_data = {
        "city": venue.city,
        "state": venue.state,
        "venues": []
    }
    venue_data = {
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": venue.upcoming_shows_count
    }
    area_data["venues"].append(venue_data)
    data.append(area_data)
 return render_template('pages/venues.html', areas=data)
@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_venues=request.form['search_term']
    result_venues = Venue.query.filter(Venue.name.ilike(f'%{search_venues}%')).all()
    # print(result_venues)
    data_search = []
    for venue in result_venues:
        data_search.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": venue.upcoming_shows_count
        })

    response = {
        "count": len(result_venues),
        "data": data_search
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  # print(venue)
  past_shows = []
  upcoming_shows = []
  # shows = venue.shows
  shows = db.session.query(Show).join(Artist).filter(Show.venue_id == venue.id).all()
  for show in shows:
    show_info ={
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
    }
    past_shows.append(show_info)

  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres.split(','),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website_link": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
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
    form=request.form
    
    new_venue = Venue(
    name = form['name'],
    city = form['city'],
    state = form['state'],
    address = form['address'],
    phone = form['phone'],
    genres = form['genres'],
    facebook_link = form['facebook_link'],
    image_link = form['image_link'],
    website_link = form['website_link'],
    seeking_talent = True if form['seeking_talent'] =='y' else False,
    seeking_description = form['seeking_description']
    )
    print(new_venue)
    try:
      db.session.add(new_venue)
      db.session.commit()
  # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
       db.session.rollback()
  # TODO: on unsuccessful db insert, flash an error instead.
       flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.') 
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    finally:
       db.session.close()
    return redirect(url_for('index'))


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  # function deleteVenue(id)
  # venue_id = request.form.get('venue_id')
  deleted_venue = Venue.query.get(venue_id)
  venueName = deleted_venue.name
  print(deleted_venue)
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  try:
    db.session.delete(deleted_venue)
    db.session.commit()
    flash('Venue ' + venueName + ' was successfully deleted!')
  except:
    db.session.rollback()
    flash('please try again. Venue ' + venueName + ' could not be deleted.')
  finally:
    db.session.close()
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data= Artist.query.with_entities(Artist.id, Artist.name).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_Artist=request.form['search_term']
  result_artists = Artist.query.filter(Artist.name.ilike(f'%{search_Artist}%')).all()
  data_search = []
  for artist in result_artists:
        data_search.append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": artist.upcoming_shows_count
        })

  response = {
        "count": len(result_artists),
        "data": data_search
    }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
  # print(artist)
  past_shows = []
  upcoming_shows = []
  shows = artist.shows
  for show in shows:
    show_info = {
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": str(show.start_time)
    }
    
    past_shows.append(show_info)

  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.split(','), 
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website_link": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description":artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # artist_id = request.args.get('artist_id')
  
  artist = Artist.query.get(artist_id)

  print(artist)
  artist_info={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.split(','),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website_link": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist_info)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.get(artist_id)
  artist.name = request.form['name']
  artist.city = request.form['city']
  artist.state = request.form['state']
  artist.phone = request.form['phone']
  artist.facebook_link = request.form['facebook_link']
  artist.genres = request.form['genres']
  artist.image_link = request.form['image_link']
  artist.website_link = request.form['website_link']
  try:
    db.session.commit()
    flash("Artist {} is updated successfully".format(artist.name))
  except:
    db.session.rollback()
    flash("Artist {} isn't updated successfully".format(artist.name))
  finally:
    db.session.close()
  # return redirect(url_for('show_artist', artist_id=artist_id))
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # venue_id = request.args.get('venue_id')
  venue = Venue.query.get(venue_id)
  venue_info={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres.split(','),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website_link": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue_info)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)
  print(venue)
  venue.name = request.form['name']
  venue.city = request.form['city']
  venue.state = request.form['state']
  venue.address = request.form['address']
  venue.phone = request.form['phone']
  venue.facebook_link = request.form['facebook_link']
  venue.genres = request.form['genres']
  venue.image_link = request.form['image_link']
  venue.website_link = request.form['website_link']
  try:
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + venue.name + ' could not be updated.')
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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form=request.form
  new_artist= Artist(
    name = form['name'],
    city = form['city'],
    state = form['state'],
    phone = form['phone'],
    genres = form['genres'],
    facebook_link = form['facebook_link'],
    image_link = form['image_link'],
    website_link = form['website_link'],
    seeking_venue = True if form['seeking_venue'] =='y' else False,
    seeking_description = form['seeking_description']
  )
  try:
     db.session.add(new_artist)
     db.session.commit()
  # on successful db insert, flash success
     flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
  # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + new_artist.name + ' could not be listed.')
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  finally:
     db.session.close()
  return redirect(url_for('index'))
# render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows_list = Show.query.all()
  data = []
  for show in shows_list:
      data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
      })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form=request.form
  print(form['start_time'])
  new_show= Show(
     start_time=form['start_time'],
     artist_id=form['artist_id'],
     venue_id=form['venue_id']
  )
  try:
      db.session.add(new_show)
      db.session.commit()
  # on successful db insert, flash success
      flash('Show was successfully listed!')
  except:
      db.session.rollback()
      flash('An error occurred. Show could not be listed.')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
      db.session.close()
  return redirect(url_for('index'))
# render_template('pages/home.html')

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
