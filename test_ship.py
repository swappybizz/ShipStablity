# test_ship.py

from ship import Ship

# Initialize ship parameters
ship = Ship(length=100, beam=20, draft=10, displacement=20000)

# Print initial hydrostatic properties
print(f"Buoyancy Force: {ship.buoyancy_force:.2f} N")
print(f"Metacentric Height (GM): {ship.GM:.2f} m")
