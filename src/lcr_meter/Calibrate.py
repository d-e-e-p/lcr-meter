import math
import numpy as np
from scipy.optimize import curve_fit

class Calibrate:
    def __init__(self, seq_list, amp_list):
        self.seq_list = seq_list
        self.amp_list = amp_list
        # R L C
        self.expected_rlc_table = """
             0      1      0  
             1      2.7    0  
            10      10     0  
            22      20     0  
            47      40     0  
            68       4      0  
            100      0      0  
            150     23     0  
            220     0.44     0  
            330     .2     0  
            470     12     0  
            1000    30    0  
        """
        # Parse the table and create a mapping from sequence target to expected [R, L, C]
        expected_rlc = self.parse_rlc_table(self.expected_rlc_table)
        self.expected_map = {seq: rlc for seq, rlc in zip(self.seq_list, expected_rlc)}

    def parse_rlc_table(self, table_str):
        triplets = []
        for line in table_str.strip().splitlines():
            if line.strip():  # skip empty lines
                parts = line.split()
                triplets.append([float(p) for p in parts])
        return triplets

    def create_compare_tables(self, res_lcr):
        # Initialize comparison tables for R, L, and C
        comp_r = {amp: [] for amp in self.amp_list}
        comp_l = {amp: [] for amp in self.amp_list}
        comp_c = {amp: [] for amp in self.amp_list}

        # res_lcr in format [seq_target, amp_target, L, C, R]
        for seq, amp, measured_l, measured_c, measured_r in res_lcr:
            if amp in self.amp_list and seq in self.expected_map:
                expected_r, expected_l, expected_c = self.expected_map[seq]
               
                if measured_r is not None and math.isfinite(measured_r):
                    comp_r[amp].append([expected_r, measured_r])

                if measured_l is not None and math.isfinite(measured_l):
                    comp_l[amp].append([expected_l, measured_l])

                if measured_c is not None and math.isfinite(measured_c):
                    comp_c[amp].append([expected_c, measured_c])

        return {'R': comp_r, 'L': comp_l, 'C': comp_c}

    def _fit_and_print_component(self, component_name, comp_table):
        print(f"\n--- Calibration for {component_name} ---")
        
        def linear_func(x, a, b):
            return a * x + b

        fit_results = []
        for amp, table in comp_table.items():
            if not table or len(table) < 2:
                continue

            expected_vals = np.array([item[0] for item in table])
            measured_vals = np.array([item[1] for item in table])

            # We want to map from measured (x) to expected (y)
            x_data = measured_vals
            y_data = expected_vals

            try:
                popt, pcov = curve_fit(linear_func, x_data, y_data)
                slope, intercept = popt

                residuals = y_data - linear_func(x_data, *popt)
                ss_res = np.sum(residuals**2)
                ss_tot = np.sum((y_data - np.mean(y_data))**2)
                if ss_tot == 0:
                    r_squared = 1.0 if ss_res == 0 else 0.0
                else:
                    r_squared = 1 - (ss_res / ss_tot)

                formula = f"y = {slope:.4f}x + {intercept:.4f}"
                print(f"\nAmplitude: {amp}")
                print(f"Fit Formula: {formula}, R-squared: {r_squared:.4f}")
                print(f"{'Expected':>12} {'Measured':>12} {'Extrapolated':>15}")
                print("-" * 41)

                for expected, measured in zip(expected_vals, measured_vals):
                    extrapolated = linear_func(measured, *popt)
                    print(f"{expected:12.2f} {measured:12.2f} {extrapolated:15.2f}")
                
                fit_results.append([amp, r_squared, formula, popt])
            except RuntimeError:
                print(f"Warning: Could not perform curve fit for amplitude {amp}.")
                fit_results.append([amp, 0.0, "fit failed", []])
        
        return fit_results

    def compare(self, res_lcr):
        all_results = {}
        comp_tables = self.create_compare_tables(res_lcr)

        # Perform fit for Resistance
        res_r = self._fit_and_print_component("Resistance (R)", comp_tables['R'])
        all_results['R'] = res_r

        # Perform fit for Inductance
        res_l = self._fit_and_print_component("Inductance (L)", comp_tables['L'])
        all_results['L'] = res_l

        # Perform fit for Capacitance
        res_c = self._fit_and_print_component("Capacitance (C)", comp_tables['C'])
        all_results['C'] = res_c
        
        return all_results
