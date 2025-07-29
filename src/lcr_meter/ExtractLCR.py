import numpy as np
from scipy.optimize import curve_fit


class ExtractLCR:
    def __init__(self, seq_list, amp_list, freq_list):
        self.seq_list = seq_list
        self.amp_list = amp_list
        self.freq_list = freq_list
        pass

    def compute(self, res_f_vs_impedance):
        res = []
        for amp_target in self.amp_list:
            for seq_target in self.seq_list:
                data = [
                    (freq, z)
                    for seq, amp, freq, z in res_f_vs_impedance
                    if seq == seq_target and amp == amp_target and not math.isnan(z)
                ]
                # Sort data by frequency to help with initial guess
                data.sort(key=lambda x: x[0])
                L, C, R = self.lcr_from_impedance(data)
                res.append([seq_target, amp_target, L, C, R])

        return res

    def lcr_from_impedance(self, data):
        """
        Calculates L, C, and R from impedance measurements at different frequencies.
        The assumed model is a parallel combination of a capacitor (C) and a
        series resistor-inductor (RL) branch.

        Z_total = (1/Z_RL + 1/Z_C)^-1
        where Z_RL = R + j*omega*L and Z_C = 1/(j*omega*C)

        Args:
            data: A list of tuples, where each tuple contains
                  (frequency_in_Hz, impedance_complex).

        Returns:
            A tuple (L, C, R) with the calculated values for inductance (H),
            capacitance (F), and resistance (Ohm). Returns (None, None, None)
            if fitting fails.
        """
        if len(data) < 3:  # Need at least 3 points to fit 3 parameters
            return None, None, None

        freqs = np.array([d[0] for d in data])
        omegas = 2 * np.pi * freqs
        impedances = np.array([d[1] for d in data])

        admittances = 1 / impedances
        G_measured = admittances.real
        B_measured = admittances.imag

        def fit_func(w_stacked, L, C, R):
            n = len(w_stacked) // 2
            w = w_stacked[:n]

            # Ensure parameters are physically meaningful
            if R <= 0 or L <= 0 or C <= 0:
                return np.full(len(w_stacked), np.inf)

            denominator = R ** 2 + (w * L) ** 2
            # Handle potential division by zero if R and L are very small
            if np.any(denominator == 0):
                return np.full(len(w_stacked), np.inf)

            G_calc = R / denominator
            B_calc = w * C - (w * L) / denominator

            return np.concatenate((G_calc, B_calc))

        # Prepare data for fitting
        omegas_stacked = np.concatenate((omegas, omegas))
        measured_stacked = np.concatenate((G_measured, B_measured))

        # --- Initial Guess Calculation ---
        # At low frequencies, Zc is high, so Z ~ R + jwL
        low_freq_z = impedances[0]
        low_omega = omegas[0]
        # At high frequencies, Y ~ 1/Z_RL + jwC. If R,L are not too large, Y ~ jwC
        high_freq_y = admittances[-1]
        high_omega = omegas[-1]

        # Guesses, ensuring they are positive and non-zero
        R_guess = abs(low_freq_z.real)
        if R_guess < 1e-3:
            R_guess = 1e-3

        L_guess = abs(low_freq_z.imag / low_omega)
        if L_guess < 1e-9:
            L_guess = 1e-9  # 1 nH

        C_guess = abs(high_freq_y.imag / high_omega)
        if C_guess < 1e-15:
            C_guess = 1e-15  # 1 fF

        initial_guess = [L_guess, C_guess, R_guess]

        # Set bounds to keep parameters positive
        bounds = ([0, 0, 0], [np.inf, np.inf, np.inf])

        try:
            popt, _ = curve_fit(
                fit_func,
                omegas_stacked,
                measured_stacked,
                p0=initial_guess,
                bounds=bounds,
                maxfev=5000,  # Increase iterations for better convergence
            )
            L, C, R = popt
            return L, C, R
        except RuntimeError:
            # Could not find optimal parameters
            return None, None, None
