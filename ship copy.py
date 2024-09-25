# ship.py

import numpy as np

class Ship:
    def __init__(self, length, beam, draft, displacement):
        self.length = length          # Length Over All (LOA)
        self.beam = beam              # Width of the ship
        self.draft = draft            # Vertical distance between waterline and keel
        self.displacement = displacement  # Weight of the ship

        # Initial calculations
        self.calculate_hydrostatics()

    def calculate_hydrostatics(self):
        # Simplified hydrostatic calculations
        self.volume_displaced = self.length * self.beam * self.draft
        self.rho_water = 1025  # kg/m^3, density of seawater
        self.buoyancy_force = self.rho_water * 9.81 * self.volume_displaced

        # Initial centers (assuming box-shaped hull)
        self.KB = self.draft / 2       # Center of Buoyancy
        self.KG = self.draft / 2       # Center of Gravity
        self.BM = (self.beam ** 2) / (12 * self.draft)  # Metacentric Radius
        self.GM = self.KB + self.BM - self.KG  # Metacentric Height

    def update_cargo(self, cargo_list):
        # Update KG based on cargo positions
        total_weight = self.displacement
        moment_sum = self.KG * self.displacement  # Initial moment

        for cargo in cargo_list:
            weight = cargo['weight']
            vertical_position = cargo['vertical_position']
            moment_sum += weight * vertical_position
            total_weight += weight

        self.KG = moment_sum / total_weight
        self.GM = self.KB + self.BM - self.KG

    def calculate_righting_arm(self, heel_angle_deg):
        # Calculate Righting Arm (GZ)
        heel_angle_rad = np.radians(heel_angle_deg)
        GZ = self.GM * np.sin(heel_angle_rad)
        return GZ
