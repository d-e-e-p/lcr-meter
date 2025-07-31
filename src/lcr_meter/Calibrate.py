import numpy as np
from scipy.optimize import curve_fit

class Calibrate:
    def __init__(self, seq_list, amp_list):
        self.seq_list = seq_list
        self.amp_list = amp_list
        self.expected_r = [float(r) for r in """
         0
         1
         10
         22
         47
         68
         100
         150
         220
         330
         470
         1000
        """.split()]

    def create_compare_table(self, res_lcr):
        # res in format [seq_target, amp_target, L, C, R]
        comp = {amp: [] for amp in self.amp_list}
        for seq, amp, L, C, R in res_lcr:
            if amp in comp:
                expected_r = self.expected_r[seq]
                measured_r = R
                comp[amp].append([expected_r, measured_r])

        return comp

    def compare(self, res_lcr):
        res = []
        comp = self.create_compare_table(res_lcr)

        def linear_func(x, a, b):
            return a * x + b

        for amp, table in comp.items():
            if not table or len(table) < 2:
                # Cannot fit with less than 2 points
                continue

            # create regression table to map measured_r to expected_r
            expected_r_vals = np.array([item[0] for item in table])
            measured_r_vals = np.array([item[1] for item in table])

            # We want to map from measured (x) to expected (y)
            x_data = measured_r_vals
            y_data = expected_r_vals

            try:
                popt, pcov = curve_fit(linear_func, x_data, y_data)
                slope, intercept = popt

                # Calculate R-squared value
                residuals = y_data - linear_func(x_data, *popt)
                ss_res = np.sum(residuals**2)
                ss_tot = np.sum((y_data - np.mean(y_data))**2)
                if ss_tot == 0:
                    r_squared = 1.0 if ss_res == 0 else 0.0
                else:
                    r_squared = 1 - (ss_res / ss_tot)

                formula = f"y = {slope:.4f}x + {intercept:.4f}"
                print(f"{amp=}")
                print(f"{'Expected':>10} {'Measured':>10} {'Extrapolated':>15}")
                print("-" * 38)

                # Print each row
                for expected, measured in zip(expected_r_vals, measured_r_vals):
                    extrapolated = linear_func(measured, *popt)
                    print(f"{expected:10.0f} {measured:10.0f} {extrapolated:10.0f}")


                res.append([amp, r_squared, formula, popt])
            except RuntimeError:
                print(f"Warning: Could not perform curve fit for amplitude {amp}.")
                res.append([amp, 0.0, "fit failed", []])

        return res
