import streamlit as st
from ship import Ship
import numpy as np
import matplotlib.pyplot as plt
import time

# Title of the app
st.title("Real-Time Ship Stability and Wave Interaction Simulator")

# Sidebar Inputs
st.sidebar.header("Ship Parameters")
length = st.sidebar.slider("Length Overall (m)", 50.0, 300.0, 100.0)
beam = st.sidebar.slider("Beam (m)", 10.0, 50.0, 20.0)
draft = st.sidebar.slider("Draft (m)", 5.0, 20.0, 10.0)
displacement = st.sidebar.number_input("Lightship Displacement (tonnes)", 5000.0, 500000.0, 20000.0)

# Initialize Ship
if "ship" not in st.session_state:
    st.session_state.ship = Ship(length, beam, draft, displacement, block_coefficient=0.7, 
                                 water_plane_area_coefficient=0.85, prismatic_coefficient=0.6, hull_form_factor=1.05)

ship = st.session_state.ship

# Cargo Inputs
st.sidebar.header("Cargo Distribution")
num_cargo = st.sidebar.number_input("Number of Cargo Items", min_value=0, max_value=10, value=0, step=1)
cargo_list = []

if num_cargo > 0:
    st.sidebar.subheader("Cargo Details")
    for i in range(int(num_cargo)):
        st.sidebar.markdown(f"**Cargo {i+1}**")
        weight = st.sidebar.number_input(f"Weight (tonnes) - Cargo {i+1}", min_value=0.0, value=500.0, key=f'weight_{i}')
        vertical_position = st.sidebar.slider(f"Vertical Position (m from keel) - Cargo {i+1}", min_value=0.0, max_value=draft, value=draft/2, key=f'vp_{i}')
        longitudinal_position = st.sidebar.slider(f"Longitudinal Position (m along length) - Cargo {i+1}", min_value=0.0, max_value=length, value=length/2, key=f'lp_{i}')
        cargo_item = {'weight': weight, 'vertical_position': vertical_position, 'longitudinal_position': longitudinal_position}
        cargo_list.append(cargo_item)

# Add cargo to ship
if cargo_list:
    ship.add_cargo(cargo_list)

# Display Hydrostatic Properties
st.subheader("Hydrostatic Properties")
st.write(f"**Total Displacement:** {ship.displacement:,.2f} tonnes")
st.write(f"**Center of Gravity (KG):** {ship.KG:.2f} m from keel")
st.write(f"**Metacentric Height (GM):** {ship.GM:.2f} m")
if ship.GM <= 0:
    st.error("Warning: The ship is unstable! Metacentric Height (GM) is zero or negative.")

# Righting Arm Calculation
heel_angles = np.arange(0, 91, 1)  # From 0 to 90 degrees
GZ_values = [ship.calculate_righting_arm(angle) for angle in heel_angles]

# Plot GZ Curve


# Sidebar Inputs for Wave Parameters
st.sidebar.header("Wave Parameters")
wave_height = st.sidebar.slider("Wave Height (m)", 0.1, 10.0, 2.0)
wave_length = st.sidebar.slider("Wave Length (m)", 10.0, 500.0, 100.0)
wave_period = st.sidebar.slider("Wave Period (seconds)", 1.0, 30.0, 10.0)

# Initialize session state variables for time tracking
if "time" not in st.session_state:
    st.session_state.time = 0

# Function to generate waveform based on wave parameters
def generate_waveform(wave_height, wave_length, wave_period, time):
    omega = 2 * np.pi / wave_period  # Wave frequency
    k = 2 * np.pi / wave_length  # Wave number
    waveform = wave_height * np.sin(k * time - omega * time)
    return waveform

# Real-Time Waveform Plot (Automatically updates every second)
@st.fragment(run_every=1)
def plot_real_time_wave():
    st.session_state.time += 0.1  # Increment time for real-time simulation
    time_values = np.linspace(0, 10, 500)
    wave_values = generate_waveform(wave_height, wave_length, wave_period, time_values + st.session_state.time)
    
    fig, ax = plt.subplots()
    ax.plot(time_values, wave_values)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Wave Elevation (m)")
    ax.set_title("Real-Time Waveform")
    ax.grid(True)
    
    st.pyplot(fig)

# Display Real-Time Waveform



# Function to calculate ship's response to waves
@st.fragment(run_every=1)
def calculate_wave_response():
    response = ship.calculate_wave_interaction(wave_height, wave_length, wave_period)
    
    fig, ax = plt.subplots()
    ax.bar(["Heave (m)", "Roll Period (s)", "Pitch Period (s)", "Response Amplitude"],
           [response["heave"], response["roll_period"], response["pitch_period"], response["motion_response"]])
    ax.set_title("Ship's Wave Response")
    
    st.pyplot(fig)

# Display Ship's Response to Waves


col1, col2, col3 = st.columns(3)

with col1:
    "GZ Curve"
    fig, ax = plt.subplots()
    ax.plot(heel_angles, GZ_values)
    ax.set_xlabel("Heel Angle (degrees)")
    ax.set_ylabel("Righting Arm (GZ) in meters")
    ax.set_title("GZ Curve")
    ax.grid(True)
    st.pyplot(fig)

with col2:
    "Real-Time Waveform"
    plot_real_time_wave()
    
with col3:
    "Ship's Response to Waves"
    calculate_wave_response()
    