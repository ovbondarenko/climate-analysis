import numpy as np

import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///data/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# ################################################
# Flask Setup
# ################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        "Welcome to the Hawaii Weather App!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation <br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs <br/>"
        f"/api/v1.0/<start> <br/>"
        f"/api/v1.0/<start>/<end> <br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of all precipitation records"""
    
    # Query all precipitation records
    date = session.query(Measurement.date).all()
    prcp = session.query(Measurement.prcp).all()
    prcp_dict ={key[0]:value[0] for key, value in zip(date, prcp)}


    return jsonify(prcp_dict)


@app.route("/api/v1.0/stations")
def stations():
    """Return a list all stations"""
    # Query all station names
    results = session.query(Station.name).all()
    all_stations= list(np.ravel(results))

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def temperature():
    """Return all temperature records"""
    ld_query = engine.execute(f'''select max(date) from measurement''').fetchall()
    end_date = dt.datetime.strptime(ld_query[0][0], '%Y-%m-%d')
    year_ago =end_date - dt.timedelta(days = 365)
    start_date = dt.datetime.strftime(year_ago, '%Y-%m-%d')

    tobs_year = engine.execute(f'''select date, tobs from measurement
                                where (date BETWEEN '{start_date}' AND '{end_date}');''').fetchall()
    tobs = dict(tobs_year)

    return jsonify(tobs)

@app.route("/api/v1.0/<start>")
def temperature_start(start):
    """Return a all temperature observation after a selected date"""
    ld_query = engine.execute(f'''select max(date) from measurement''').fetchall()
    end_date = dt.datetime.strptime(ld_query[0][0], '%Y-%m-%d')

    tobs_year = engine.execute(f'''select date, tobs from measurement
                                where (date BETWEEN '{start}' AND '{end_date}');''').fetchall()
    tobs = dict(tobs_year)

    return jsonify(tobs)

@app.route("/api/v1.0/<start>/<end>")
def temperature_start_end(start, end):
    """Return all temperature observation between selected start and end dates"""

    tobs_year = engine.execute(f'''select date, tobs from measurement
                                where (date BETWEEN '{start}' AND '{end}');''').fetchall()
    tobs = dict(tobs_year)

    return jsonify(tobs)

if __name__ == '__main__':
    app.run(debug=True)
