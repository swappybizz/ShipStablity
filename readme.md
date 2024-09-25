# Real-Time Ship Stability and Wave Interaction Simulator

This is a real-time ship stability and wave interaction simulator built with Streamlit. The application allows you to input various ship parameters and simulate how the ship interacts with waves over time. It visualizes the righting arm curve (GZ curve) and dynamically updates both the waveforms and the ship's response to wave interactions in real-time.

## Features

- **Dynamic Ship Simulation**: Input key ship parameters (length, beam, draft, displacement) and simulate ship behavior in waves.
- **Real-Time Waveform Simulation**: A continuously updating graph of the wave pattern over time.
- **GZ (Righting Arm) Curve**: Calculates and plots the righting arm for different heel angles.
- **Wave Interaction Response**: Simulates and plots the ship's response to wave forces, displaying metrics such as heave, roll, pitch, and motion response amplitude.
- **Cargo Loading**: Adjust the ship's stability by loading different weights at various positions along the length and height of the ship.
- **Ballast Management**: Manage ballast tanks and update the ship's hydrostatic properties based on ballast operations.

## Technologies Used

- **Python**
- **Streamlit**: For creating an interactive web interface and real-time graphs.
- **Matplotlib**: For plotting dynamic graphs.
- **Numpy**: For numerical calculations and waveform generation.

## Run on the following 
shipstability.vercel.app