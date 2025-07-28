class CN0565Tester:
    def __init__(self, dev):
        self.dev = dev
        self.init_dev(dev)
        self._switch_sequence = self.generate_switch_sequence()

    def init_dev(self, dev):
        dev.gpio1_toggle = True
        dev.magnitude_mode = False
        """In impedance mode, device measures voltage and current and to compute the impedance.
        Otherwise, only the voltage is measured."""
        dev.impedance_mode = True
        dev.immediate = True

    def generate_switch_sequence(self):
        switch_seq = []
        for base in range(0, 16, 2):  # step by 2: (0,1), (2,3), ...
            fplus = base
            fminus = base + 1
            # splus = fplus, sminus = fminus
            switch_seq.append([fplus, fminus, fplus, fminus])
        return switch_seq

    def run(self, amp_list, freq_list):
        ret = []
        for amp in amp_list:
            for freq in freq_list:
                for seq in self._switch_sequence:
                    # Reset crosspoint switch
                    self.dev.excitation_amplitude = amp
                    self.dev.excitation_frequency = freq
                    self.dev.gpio1_toggle = True

                    # Set F+/F-/S+/S- to channels 0-3
                    self.dev[seq[0]][0] = True
                    self.dev[seq[1]][1] = True
                    self.dev[seq[2]][2] = True
                    self.dev[seq[3]][3] = True

                    # Read impedance measurement
                    s = self.dev.channel["voltage0"].raw
                    print(f" amp={self.dev.excitation_amplitude} freq={self.dev.excitation_frequency} {seq=} {s.real=:.0f} {s.imag=::.0f}")
                    ret.append([amp, freq, seq, s.real, s.imag])

        return ret
