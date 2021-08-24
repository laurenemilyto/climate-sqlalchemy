#  Import Dependencies
import datetime as dt
import numpy as np
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to tables
# print(Base.classes.keys()) 
Station = Base.classes.station
Measurement = Base.classes.measurement

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    "List  API routes"
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available routes: <br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<stop>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create session (link) from Python to the DB
    session = Session(engine)

    # Query
    sel = [Measurement.date,Measurement.prcp]
    results = session.query(*sel).all()

    session.close()

    # Convert query results to a dictionary 
    prcps = []
    for date,prcp in results:
        precip_dict ={}
        precip_dict['Date'] = date
        precip_dict['Precipitation'] = prcps
        prcps.append(precip_dict)

    # Return json list of precipitation values
    return jsonify(prcps)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()
    # Convert list of tuples into normal list
    stations = list(np.ravel(results))

    # Return json list of station values
    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def temperatures():
    session = Session(engine)
    last_str = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_date = dt.datetime.strptime(last_str, '%Y-%m-%d')
    querydate = dt.date(last_date.year -1, last_date.month, last_date.day)

    # Query
    sel = [Measurement.date, Measurement.tobs]
    results = session.query().filter(Measurement.date > querydate.all())

    session.close()

    # Convert query results to a dictionary 
    tobs = []
    for date, temp in results:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tobs.append(tobs_dict)

    return jsonify(tobs)

@app.route('/api/v1.0/<start>')
def start_temp (start):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    tobs = []
    for tmin,tmax,tavg in results:
        tobs_dict = {}
        tobs_dict["TMin"] = tmin
        tobs_dict["TMax"] = tmax
        tobs_dict["TAvg"] = tavg
        tobs.append(tobs_dict)

    return jsonify(tobs)

@app.route('/api/v1.0/<start>/<stop>')
def get_t_start_stop(start,stop):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= stop).all()
    session.close()

    tobs = []
    for tmin,tmax,tavg in results:
        tobs_dict = {}
        tobs_dict["TMin"] = tmin
        tobs_dict["TMax"] = tmax
        tobs_dict["TAvg"] = tavg
        tobs.append(tobs_dict)

    return jsonify(tobs)


if __name__ == "__main__":
    app.run(debug=True)


