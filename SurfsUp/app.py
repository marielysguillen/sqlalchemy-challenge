# Import the dependencies.
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
base = automap_base()

# reflect the tables
base.prepare(engine, reflect=True)

# Save references to each table
measurement = base.classes.measurement
station = base.classes.station
#print(Base.classes.keys())

# Create our session (link) from Python to the DB
session = Session(engine)

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
        f'<a href="http://127.0.0.1:5000/api/v1.0/precipitation"><button>Precipitation</button></a><br/>'
        f'<a href="http://127.0.0.1:5000/api/v1.0/stations"><button>Stations</button></a><br/>'
        f'<a href="http://127.0.0.1:5000/api/v1.0/tobs"><button>Temperature</button></a><br/>'
        f'<a href="http://127.0.0.1:5000/api/v1.0/2017-08-23"><button>Start</button></a><br/>'
        f'<a href="http://127.0.0.1:5000/api/v1.0/2016-08-23/2017-08-23"><button>Start/End</button></a><br/>'
       
    )
    

# Define the route for /api/v1.0/precipitation
@app.route('/api/v1.0/precipitation')
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    """Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) 
    to a dictionary using date as the key and prcp as the value."""
    
    most_recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    date_string = most_recent_date[0]
    
    date_obj = dt.datetime.strptime(date_string, '%Y-%m-%d')
    year_days_before = date_obj - dt.timedelta(days = 365)
    formatted_year_ago = year_days_before.strftime('%Y-%m-%d')
#print(year_days_before) -> 2016-08-23 00:00:00
#print(formatted_year_ago) ->-> 2016-08-23

# Perform a query to retrieve the data and precipitation scores
    data_prec_query = session.query(measurement.date, measurement.prcp).filter(measurement.date >= formatted_year_ago).all()

    session.close()
    
    precipitation_data = {}
    for date, prcp in data_prec_query:
        precipitation_data[date] = prcp

    # Return the JSON representation of the dictionary
    return jsonify(precipitation_data)

# Define the route for /api/v1.0/stations
@app.route('/api/v1.0/stations')
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """Return a JSON list of stations from the dataset."""
    
    #Let's create a dict and list to return
    station_list = []
    stations = session.query(station.station,station.name).all()
    for station_id, station_name in stations:
        station_data = {}
        station_data['station'] = station_id
        station_data['name'] = station_name
        station_list.append(station_data)
        
    
    session.close()
    
    # Return the list of stations as JSON
    return jsonify(station_list)
    
# Define the route for tobs
@app.route('/api/v1.0/tobs')
def tobs():
    """Query the dates and temperature observations of the most-active station for the previous year of data."""
    
     # Design a query to find the most active stations (i.e. which stations have the most rows?)
     # Query to find the most active station
    most_active_station = session.query(measurement.station, func.count(measurement.station)).\
        group_by(measurement.station).\
        order_by(func.count(measurement.station).desc()).first()
    
    # Get the station ID of the most active station
    most_active_station_id = most_active_station[0]

    # Calculate the date one year ago from the most recent date in the dataset
    most_recent_date = session.query(func.max(measurement.date)).scalar()
    date_obj = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')
    year_ago_date = date_obj - dt.timedelta(days=365)
    formatted_year_ago = year_ago_date.strftime('%Y-%m-%d')

    # Query temperature observations for the most active station for the previous year
    temperature_data = session.query(measurement.station,measurement.date, measurement.tobs).\
        filter(measurement.station == most_active_station_id).\
        filter(measurement.date >= formatted_year_ago).all()  

     # Convert the query result to a list of dictionaries
    temperature_list = []
    for row in temperature_data:
        #if row[0] == 'USC00519281':
        temperature_dict = {'station': row[0], 'date': row[1], 'tobs': row[2]}
        temperature_list.append(temperature_dict)

    return jsonify(temperature_list)


@app.route('/api/v1.0/<start>')
def temps_start(start):
     # Create our session (link) from Python to the DB
    session = Session(engine)
    
    """Return min, max, and average temperatures from the given start date to the end of the dataset."""

    # Query for min, max, and average temperatures from start date to end of dataset
    start_data = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
        filter(measurement.date >= start).all()
    session.close()

    # Convert the query result to a dictionary
    all_start_data = []
    for min_temp, max_temp, avg_temp in start_data:
        temp_data = {}
        temp_data['TMIN'] = min_temp
        temp_data['TMAX'] = max_temp
        temp_data['TAVG'] = avg_temp
        all_start_data.append(temp_data)

    return jsonify(all_start_data)

@app.route('/api/v1.0/<start>/<end>')
def temps_start_end(start, end):
     # Create our session (link) from Python to the DB
    session = Session(engine)
    
    """Return min, max, and average temperatures from the given start date to the given end date."""

    # Query for min, max, and average temperatures from start date to end date
    start_end_data = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
        filter(measurement.date >= start).\
        filter(measurement.date <= end).all()
    session.close()
    
    # Convert the query result to a dictionary
    all_start_end_data = []
    for min_temp, max_temp, avg_temp in start_end_data:
        temp_data = {}
        temp_data['TMIN'] = min_temp
        temp_data['TMAX'] = max_temp
        temp_data['TAVG'] = avg_temp
        all_start_end_data.append(temp_data)

    return jsonify(all_start_end_data)




if __name__ == '__main__':
    app.run(debug=True)

    
    



