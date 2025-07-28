class CN0565Tester:
    def __init__(self, dev):
        self.dev = dev
        self.init_dev(dev)

    def init_dev(self, dev):
        dev.gpio1_toggle = True
        dev.magnitude_mode = False
        """In impedance mode, device measures voltage and current and to compute the impedance.
        Otherwise, only the voltage is measured."""
        dev.impedance_mode = True
        dev.immediate = True

    def run(self, seq_list,  amp_list, freq_list):
        ret = []
        for amp in amp_list:
            for freq in freq_list:
                for seq in seq_list:
                    # Reset crosspoint switch
                    self.dev.excitation_amplitude = amp
                    self.dev.excitation_frequency = freq
                    self.dev.gpio1_toggle = True

                    # Set F+/F-/S+/S- to channels 0-3
                    fplus, fminus = seq*2, seq*2 + 1
                    splus, sminus = fplus, fminus

                    self.dev[fplus][0] = True
                    self.dev[splus][1] = True
                    self.dev[sminus][2] = True
                    self.dev[fminus][3] = True

                    # Read impedance measurement
                    z = self.dev.channel["voltage0"].raw
                    print(f" amp={self.dev.excitation_amplitude} freq={self.dev.excitation_frequency} {seq=} {z.real=:.0f} {z.imag=::.0f}")
                    ret.append([seq, amp, freq, z])

        return ret
