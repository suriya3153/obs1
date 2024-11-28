import streamlit as st
import psutil
import time
from datetime import datetime
import pymongo

# Connect to MongoDB
client = pymongo.MongoClient("mongodb+srv://suriya315:12345678s@cluster0.kbh9v.mongodb.net/?retryWrites=true&w=majority")
db = client["obs_tracking"]
collection = db["sessions"]

# Check if OBS is running
def is_obs_running():
    for process in psutil.process_iter(['pid', 'name']):
        if 'obs64.exe' in process.info['name'].lower():
            return True
    return False

# Store session data in MongoDB
def store_time_data(start_time, end_time, total_time):
    session_data = {
        'start_time': start_time,
        'end_time': end_time,
        'total_time_hours': total_time
    }
    # Store in MongoDB collection
    collection.insert_one(session_data)

# Streamlit app interface
st.title("OBS Work Time Tracker")

# Track OBS usage
st.sidebar.header("OBS Time Tracker Settings")
obs_status = st.sidebar.radio("Is OBS Running?", ["Not Running", "Running"])

if obs_status == "Running":
    st.write("OBS is running! Tracking time...")

    # Start tracking time
    start_time = time.time()
    while is_obs_running():
        time.sleep(10)  # Check every 10 seconds if OBS is still running
    end_time = time.time()

    # Calculate the total work time
    total_time = (end_time - start_time) / 3600  # Convert to hours
    end_time_formatted = datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')

    st.write(f"OBS stopped at: {end_time_formatted}")
    st.write(f"Total time worked: {total_time:.2f} hours")

    # Store data in MongoDB
    store_time_data(datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S'), end_time_formatted, total_time)

else:
    st.write("OBS is not running. Please start OBS and select 'Running'.")

st.sidebar.subheader("Recent Sessions:")
# Display all past sessions from MongoDB
sessions_cursor = collection.find()
for session in sessions_cursor:
    st.sidebar.write(f"Start: {session['start_time']}, End: {session['end_time']}, Time: {session['total_time_hours']:.2f} hours")

