
from .RegisterAccess import RegisterAccess


class CN0565Tester:
    def __init__(self, dev, dev1, dev2):
        self.dev = dev
        self.dev1 = dev1
        self.dev2 = dev2
        self.reg = RegisterAccess(dev1)
        self.init_dev()

    def init_dev(self):
        dev = self.dev
        dev.gpio1_toggle = True
        dev.magnitude_mode = False
        # In impedance mode, device measures voltage and current and to compute the impedance.
        dev.impedance_mode = True
        dev.immediate = True
        dev.electrode_count = 16
        self.dump_state()
        self.set_rtia()


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
                    # splus, sminus = fplus, fminus

                    # Read impedance measurement
                    self.dev.open_all()
                    self.dev[fminus][0] = True
                    self.dev[fminus][1] = True
                    self.dev[fplus][2] = True
                    self.dev[fplus][3] = True

                    self.set_rtia()
                    z = self.dev.channel["voltage0"].raw
                    print(f" amp={self.dev.excitation_amplitude} freq={self.dev.excitation_frequency} {seq=} {z.real=:.0f} {z.imag=:.0f}")
                    ret.append([seq, amp, freq, z])

        return ret

    def set_state(self):
        self.reg.write_register("CALDATLOCK", 'Value', 0xDE87A5AF)  # unlock
        self.reg.write_register("DACGAIN", 'Value', 0x800)          # no gain

        self.reg.write_register("HSRTIACON", 'CTIACON', 0b000001)   # 1pF
        self.reg.write_register("HSRTIACON", 'TIASW6CON', 0b0)      # Diode OFF

        # disable high speed DAC
        self.reg.write_register("AFECON", 'DACEN', 0b0)
        self.reg.write_register("AFECON", 'ADCCONVEN', 0b1)
        self.reg.write_register("AFECON", 'ADCEN', 0b1)
        # enable low speed TIA
        self.reg.write_register("LPDACCON0", 'PWDEN', 0b0)
        # Enable Writes to Low Power DAC Data Register
        self.reg.write_register("LPDACCON0", 'RSTEN', 0b1)
        # Set Low Power DAC Output Voltages
        self.reg.write_register("LPDACDAT0", 'DACIN6', 0x3F)
        self.reg.write_register("LPDACDAT0", 'DACIN12', 0xFFF)
        # Enable the DC DAC Buffer
        # external RTIA
        self.reg.write_register("LPTIACON0", 'TIAGAIN', 0b0)
        # low-pass filter resistor (RLPF)
        self.reg.write_register("LPTIACON0", 'TIARF', 0b111)
        # Power Up the Low Power TIA
        self.reg.write_register("LPTIACON0", 'TIAPDEN', 0b0)





        

        """
        To use the DE0 pin for the external RTIA value, set the following register values:
            ► DE0RESCON = 0x97.
            ► HSRTIACON, Bits[3:0] = 0xF.
        """
        rtia_external = True
        if rtia_external:
            self.reg.write_register("DE0RESCON", 'DE0RCON', 0x97)       #
            self.reg.write_register("HSRTIACON", 'RTIACON', 0xF)        # disconnect rtia
        else:
            self.reg.write_register("HSRTIACON", 'RTIACON', 0x0)        # 200 Ω


        # self.reg.write_register("HSRTIACON", 'RTIACON', 0xF)      # open




    def dump_state(self):
        print("RTIA: ")
        self.reg.read_register("HSRTIACON")


