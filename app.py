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
        f"/api/v1.0/[start format:yyyy-mm-dd]<br/>"
        f"/api/v1.0/[start format:yyyy-mm-dd]/[stop format:yyyy-mm-dd]<br/>"
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
        precip_dict['Precipitation'] = prcp
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
    results = session.query(Measurement.date, Measurement.tobs, Measurement.prcp).\
                filter(Measurement.date >= '2016-08-23').\
                filter(Measurement.station=='USC00519281').\
                order_by(Measurement.date).all()
    session.close()

    # Convert query results to a dictionary 
    tobs = []
    for prcp, date, temps in results:
        tobs_dict = {}
        tobs_dict["prcp"] = prcp
        tobs_dict["date"] = date
        tobs_dict["tobs"] = temps
            
        tobs.append(tobs_dict)

    return jsonify(tobs)


@app.route("/api/v1.0/<start>")
def Start (start):
    session = Session(engine)
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results = session.query(*sel).filter(Measurement.date >= start).all()
    session.close()

    start_tobs = []
    for min, avg, max in results:
        stobs_dict = {}
        stobs_dict["TMin"] = min
        stobs_dict["TAvg"] = avg
        stobs_dict["TMax"] = max
        start_tobs.append(stobs_dict)

    return jsonify(start_tobs)

@app.route('/api/v1.0/<start>/<stop>')
def Start_Stop (start,stop):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= stop).all()
    session.close()

    se_tobs = []
    for min,avg,max in results:
        setobs_dict = {}
        setobs_dict["TMin"] = min
        setobs_dict["TAvg"] = avg
        setobs_dict["TMax"] = max
        se_tobs.append(setobs_dict)

    return jsonify(se_tobs)


if __name__ == "__main__":
    app.run(debug=True)


