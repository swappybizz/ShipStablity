import streamlit as st
from ship import Ship
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from stl import mesh  # For loading STL files
import tempfile  # For temporary file handling

st.set_page_config(page_title="Real-Time Ship Stability and Wave Interaction Simulator", page_icon="🚢", layout="wide")

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

# Function to calculate ship's response to waves
@st.fragment(run_every=1)
def calculate_wave_response():
    response = ship.calculate_wave_interaction(wave_height, wave_length, wave_period)
    
    fig, ax = plt.subplots()
    ax.bar(["Heave (m)", "Roll Period (s)", "Pitch Period (s)", "Response Amplitude"],
           [response["heave"], response["roll_period"], response["pitch_period"], response["motion_response"]])
    ax.set_title("Ship's Wave Response")
    
    st.pyplot(fig)

# Function to plot 3D model (either default or uploaded STL)

# Function to plot the 3D ship model
def plot_3d_ship_model():
    stl_file = st.sidebar.file_uploader("Upload Ship Model (.stl)", type=['stl'])

    if stl_file is not None:
        # Load the STL file into a temporary file and render it
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(stl_file.read())
            tmp_file_path = tmp_file.name

        # Load the STL file using numpy-stl
        your_mesh = mesh.Mesh.from_file(tmp_file_path)
        
        # Extract vertices and faces
        x = your_mesh.x.flatten()
        y = your_mesh.y.flatten()
        z = your_mesh.z.flatten()

        fig = go.Figure(data=[go.Mesh3d(x=x, y=y, z=z, opacity=0.5)])
        fig.update_layout(
            title="3D Ship Model (Uploaded)",
            scene=dict(
                xaxis_title="X",
                yaxis_title="Y",
                zaxis_title="Z"
            ),
            width=700, height=700
        )
        st.plotly_chart(fig)

    else:
        # Default ship dimensions
        length = 30
        beam = 10
        draft = -10

        # Ship hull (rectangular prism) vertices
        x_hull = [-length/2, length/2, length/2, -length/2, -length/2, length/2, length/2, -length/2]
        y_hull = [-beam/2, -beam/2, beam/2, beam/2, -beam/2, -beam/2, beam/2, beam/2]
        z_hull = [0, 0, 0, 0, draft, draft, draft, draft]  # Draft should be negative to represent depth below waterline

        # Water surface (a flat blue plane)
        x_water = [-length/2, length/2, length/2, -length/2]
        y_water = [-beam/2, -beam/2, beam/2, beam/2]
        z_water = [0, 0, 0, 0]  # Water surface at z = 0

        # Define faces for the hull (rectangular prism)
        i_hull = [0, 0, 0, 1, 4, 5, 6, 7, 4, 2, 3, 6]
        j_hull = [1, 3, 2, 4, 5, 6, 2, 3, 7, 6, 7, 5]
        k_hull = [2, 2, 1, 5, 6, 7, 0, 0, 5, 4, 3, 1]

        # Create the 3D mesh for the hull (brown) and water (blue)
        fig = go.Figure()

        # Ship hull (brown)
        fig.add_trace(go.Mesh3d(
            x=x_hull, y=y_hull, z=z_hull, 
            i=i_hull, j=j_hull, k=k_hull, 
            color='brown', opacity=0.7
        ))

        # Water surface (blue)
        fig.add_trace(go.Mesh3d(
            x=x_water, y=y_water, z=z_water, 
            i=[0], j=[1], k=[2], 
            color='blue', opacity=0.5
        ))

        # Update the layout of the plot
        fig.update_layout(
            title="3D Ship Model with Water",
            scene=dict(
                xaxis_title="Length (m)",
                yaxis_title="Beam (m)",
                zaxis_title="Draft (m)"
            ),
            width=700, height=700
        )

        st.plotly_chart(fig)

# Run the function to plot
# plot_3d_ship_model()
# Now call the function in your main app code:
# plot_3d_ship_model()

# Columns for layout
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("GZ Curve")
    fig, ax = plt.subplots()
    ax.plot(heel_angles, GZ_values)
    ax.set_xlabel("Heel Angle (degrees)")
    ax.set_ylabel("Righting Arm (GZ) in meters")
    ax.set_title("GZ Curve")
    ax.grid(True)
    st.pyplot(fig)

with col2:
    st.subheader("Real-Time Waveform")
    plot_real_time_wave()
    
with col3:
    st.subheader("Ship's Response to Waves")
    calculate_wave_response()

# Display the 3D Ship Visualization
st.subheader("3D Ship Visualization")
plot_3d_ship_model()
