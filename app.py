import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt
from datetime import date

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
   
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/--insert start date--<br/>"
        f"/api/v1.0/--insert start date--/--insert end date--<br/>"
        f"Note: use date format yyyy-mm-dd in range 2010-01-01 to 2017-08-23"
    )
        
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Returns precipitation data for past year
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Calculates the date 1 year ago from the last data point in the database

    # Finds row with last date 
    last_row = session.query(Measurement).order_by(Measurement.date.desc()).first()

    # Pulls the date value as a string
    last_date_str = last_row.date

    #converts to a datetime.date object
    last_date = dt.datetime.strptime(last_date_str, '%Y-%m-%d').date()

    year_previous = last_date - dt.timedelta(days=365)

    last_year = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date > year_previous).all()

    session.close()

    # Converts result to a dictionary and returns json of temp data
    
    temps_dict = {}
    
    for date, prcp in last_year:
        temps_dict[date] = prcp

    return jsonify(temps_dict)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Create a list of stations
    stations = session.query(Station.station).all()

    session.close()

    # Convert query results into regular list and returns json data
    stations_list = list(np.ravel(stations))

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Design a query to retrieve the last 12 months of temperature observation data (tobs).

    temps_for_year = session.query(Measurement.station, Measurement.date, Measurement.tobs).all()

    session.close()
 
    # Convert query results into regular list and returns json of temp data
    temps_list = list(np.ravel(temps_for_year))

    return jsonify(temps_list)

@app.route("/api/v1.0/<start_date>")
def startdate(start_date):

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Returns: TMIN, TAVE, and TMAX for observations after the given start date

    temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

    session.close()

    # Convert query results into regular list and returns json of temp data
    temps_list = list(np.ravel(temps))

    return jsonify(temps_list)


@app.route("/api/v1.0/<start_date>/<end_date>")
def enddate(start_date, end_date):

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Returns: TMIN, TAVE, and TMAX for observations between the two given dates
    
    temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    session.close()

    # Convert query results into regular list and returns json of temp data
    temps_list = list(np.ravel(temps))

    return jsonify(temps_list)

if __name__ == '__main__':
    app.run(debug=True)