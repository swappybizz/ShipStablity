import numpy as np

class Ship:
    def __init__(self, length, beam, draft, displacement, block_coefficient, water_plane_area_coefficient, prismatic_coefficient, hull_form_factor):
        self.length = length  # Length Overall (LOA) in meters
        self.beam = beam  # Beam (width) in meters
        self.draft = draft  # Draft in meters
        self.displacement = displacement  # Displacement in tonnes
        self.block_coefficient = block_coefficient  # Block Coefficient (Cb)
        self.water_plane_area_coefficient = water_plane_area_coefficient  # Waterplane Area Coefficient (Cwp)
        self.prismatic_coefficient = prismatic_coefficient  # Prismatic Coefficient (Cp)
        self.hull_form_factor = hull_form_factor  # Form factor for resistance calculations

        # Hydrostatic data
        self.KB = 0  # Keel to buoyancy center
        self.KG = 0  # Keel to gravity center
        self.GM = 0  # Metacentric height
        self.BM = 0  # Metacentric radius
        self.KMT = 0  # Transverse Metacentric Height

        # Resistance and power data
        self.hull_resistance = 0  # Hull resistance in Newtons
        self.power_required = 0  # Power required in kilowatts

        self.cargo_list = []  # List to hold cargo items
        self.ballast_tanks = []  # List for ballast tank management

        # Wave parameters
        self.wave_height = 0
        self.wave_length = 0
        self.wave_period = 0
        self.time = 0

        # Perform initial hydrostatic calculations
        self.calculate_hydrostatics()

    def calculate_hydrostatics(self):
        # Constants
        self.rho_water = 1025  # kg/m³, density of seawater
        self.gravity = 9.81  # m/s², acceleration due to gravity

        # Hydrostatic calculations
        self.volume_displaced = self.displacement / self.rho_water  # m³
        self.buoyancy_force = self.rho_water * self.gravity * self.volume_displaced  # Newtons

        # Waterplane Area and Moment of Inertia (considering an elliptical waterplane)
        self.waterplane_area = self.length * self.beam * self.water_plane_area_coefficient  # m²
        self.waterplane_moment_inertia = (self.beam ** 3) * self.length / 12  # Ixx, m⁴ (simplified)

        # Centers of buoyancy and gravity (more refined, based on block coefficient)
        self.KB = self.block_coefficient * self.draft / 3  # Vertical center of buoyancy (approx)
        self.KG = self.draft / 2  # Assuming the center of gravity initially at half the draft

        # Metacentric radius and height (GM) with transverse metacentric height (KMT)
        self.BM = self.waterplane_moment_inertia / self.volume_displaced  # Transverse metacentric radius
        self.GM = self.KB + self.BM - self.KG  # Metacentric height (for transverse stability)
        self.KMT = self.BM  # Transverse metacentric height

        # Longitudinal stability (simplified for trim considerations)
        self.BML = self.length ** 2 / (12 * self.volume_displaced)  # Longitudinal metacentric radius
        self.GML = self.KB + self.BML - self.KG  # Longitudinal metacentric height

    def add_cargo(self, cargo_list):
        self.cargo_list = cargo_list
        self.update_cargo_effects()

    def update_cargo_effects(self):
        # Cargo weight and moment calculations (including CG shifts)
        total_cargo_weight = sum([cargo['weight'] for cargo in self.cargo_list])  # tonnes
        total_cargo_vertical_moment = sum([cargo['weight'] * cargo['vertical_position'] for cargo in self.cargo_list])  # tonne-meters
        total_cargo_longitudinal_moment = sum([cargo['weight'] * cargo['longitudinal_position'] for cargo in self.cargo_list])  # tonne-meters

        # Update displacement, KG, and longitudinal CG
        total_weight = self.displacement + total_cargo_weight  # Total weight
        total_vertical_moment = (self.KG * self.displacement) + total_cargo_vertical_moment  # tonne-meters
        total_longitudinal_moment = total_cargo_longitudinal_moment  # tonne-meters

        self.KG = total_vertical_moment / total_weight  # Update vertical CG
        self.displacement = total_weight  # Update displacement
        self.LCG = total_longitudinal_moment / total_weight  # Update longitudinal CG

        # Recalculate hydrostatic properties based on the new displacement
        self.calculate_hydrostatics()

    def calculate_wind_heeling_moment(self, wind_speed, wind_area, wind_direction_deg):
        # Heeling moment caused by wind force
        wind_force = 0.5 * 1.225 * wind_speed ** 2 * wind_area  # Wind force (using drag coefficient of ~1)
        wind_direction_rad = np.radians(wind_direction_deg)
        heeling_moment = wind_force * self.beam * np.sin(wind_direction_rad)  # Moment due to wind force
        return heeling_moment

    def calculate_resistance(self, ship_speed):
        # Resistance calculation using ITTC formula for frictional and residual resistance
        kinematic_viscosity = 1.19e-6  # m²/s for seawater
        reynolds_number = (ship_speed * self.length) / kinematic_viscosity  # Reynolds number

        # Frictional resistance using ITTC 1957 model
        cf = 0.075 / ((np.log10(reynolds_number) - 2) ** 2)  # Coefficient of friction
        wetted_surface_area = self.length * self.draft * 2 + self.beam * self.length  # Approx. wetted area

        frictional_resistance = 0.5 * self.rho_water * wetted_surface_area * cf * ship_speed ** 2
        residual_resistance = self.hull_form_factor * frictional_resistance  # Form factor accounts for residual resistance

        self.hull_resistance = frictional_resistance + residual_resistance  # Total hull resistance in Newtons
        self.power_required = self.hull_resistance * ship_speed / 1000  # Power required in kW
        return self.hull_resistance

    def add_ballast_tank(self, ballast_tank):
        self.ballast_tanks.append(ballast_tank)
        self.update_ballast_effects()

    def update_ballast_effects(self):
        # Recalculate displacement and KG based on ballast addition/removal
        total_ballast_weight = sum([tank['weight'] for tank in self.ballast_tanks])
        total_ballast_moment = sum([tank['weight'] * tank['vertical_position'] for tank in self.ballast_tanks])

        total_weight = self.displacement + total_ballast_weight
        total_moment = (self.KG * self.displacement) + total_ballast_moment

        self.KG = total_moment / total_weight
        self.displacement = total_weight

        # Recalculate hydrostatic properties
        self.calculate_hydrostatics()

    def calculate_wave_interaction(self, wave_height, wave_length, wave_period):
        # Wave interaction effects on stability and motions (heave, pitch, roll)
        wave_force = 0.5 * self.rho_water * (wave_height ** 2) * self.length * self.beam  # Simplified wave force
        natural_roll_period = 2 * np.pi * np.sqrt(self.GM / self.gravity)  # Approximate roll period in seconds
        natural_pitch_period = 2 * np.pi * np.sqrt(self.GML / self.gravity)  # Approximate pitch period

        response_amplitude_operator = wave_force / (self.displacement * self.gravity)  # Ratio of motion amplitude to wave amplitude
        return {
            "heave": wave_force / self.displacement,  # Vertical heave motion
            "roll_period": natural_roll_period,  # Natural roll period
            "pitch_period": natural_pitch_period,  # Natural pitch period
            "motion_response": response_amplitude_operator  # Response to waves
        }

    def check_structural_stress(self):
        # Simplified structural stress calculation based on hull girder bending moment
        bending_moment = 0.1 * self.displacement * self.length  # Simplified formula for max bending moment
        max_stress = bending_moment / (self.length * self.beam)  # Approximate max stress in the hull girder
        return max_stress

    def set_wave_parameters(self, wave_height, wave_length, wave_period):
        self.wave_height = wave_height
        self.wave_length = wave_length
        self.wave_period = wave_period

    def update_time(self, time):
        self.time = time

    def calculate_righting_arm(self, heel_angle_deg):
        # Calculate Righting Arm (GZ) at a given heel angle
        # Include wave-induced heel angle
        heel_angle_rad = np.radians(heel_angle_deg)

        # Wave-induced heel angle
        if self.wave_length > 0 and self.wave_period > 0:
            k = 2 * np.pi / self.wave_length
            omega = 2 * np.pi / self.wave_period
            wave_slope = self.wave_height * k * np.cos(k * 0 - omega * self.time)  # Assuming ship at x=0
            wave_induced_heel_angle_rad = np.arctan(wave_slope)
        else:
            wave_induced_heel_angle_rad = 0

        total_heel_angle_rad = heel_angle_rad + wave_induced_heel_angle_rad

        GZ = self.GM * np.sin(total_heel_angle_rad)
        return GZ
