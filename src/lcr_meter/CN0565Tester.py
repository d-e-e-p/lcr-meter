
from .RegisterAccess import RegisterAccess


class CN0565Tester:
    def __init__(self, dev, dev1, dev2):
        self.dev = dev
        self.dev1 = dev1
        self.dev2 = dev2
        self.register_access = RegisterAccess(dev)
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

    def dump_state(self):
        self.register_access.read_register("AFECON")

    def set_rtia(self):
        # RTIA = open    -> bits [3:0] = 1111
        # RTIA = 200 ohm -> bits [3:0] = 0000
        # Diode OFF -> bit [4] = 0
        # CTIA = 4pF -> bits [12:5] = 0b0010 -> shifted left by 5 = 0b0010 << 5 = 0x40

        rtia_bits = 0b0000             # RTIA = 200 ohm (bits [3:0])
        # rtia_bits = 0b1111             # RTIA = open (bits [3:0])
        diode_bit = 0 << 4             # Diode OFF (bit 4 = 0)
        ctia_bits = 0b0010 << 5        # CTIA = 4 pF (bits [12:5] = 0x40)

        hsrtiacon_value = ctia_bits | diode_bit | rtia_bits
        # print(f"HSRTIACON = 0x{hsrtiacon_value:08X}")
        self.dev1.reg_write(0x20F0, hsrtiacon_value)
        self.dev1.reg_write(0x20F8, 0x97) # disconnect internal rtia
        self.dev1.reg_write(0x20F8, 0xFF) # reset
        self.dev1.reg_write(0x20F8, 0x00) # default
        reg_val = self.dev1.reg_read(0x20F0)
        # self.decode_hsrtia_config(reg_val)

    def decode_hsrtia_config(self, reg_val):
        print(f"Raw HSRTIACON Register: 0x{reg_val:08X}")

        # Bits [3:0] ? RTIACON
        rtia_bits = reg_val & 0xF
        rtia_map = {
            0x0: "200 ",
            0x1: "1 k",
            0x2: "5 k",
            0x3: "10 k",
            0x4: "20 k",
            0x5: "40 k",
            0x6: "80 k",
            0x7: "160 k",
        }
        rtia_desc = rtia_map.get(rtia_bits, "RTIA is open")

        # Bit [4] ? TIASW6CON (diode control)
        sw6_bit = (reg_val >> 4) & 0x1
        sw6_desc = "Diode ON (SW6 closed)" if sw6_bit else "Diode OFF (SW6 open)"

        # Bits [12:5] ? CTIACON
        ctiacon_bits = (reg_val >> 5) & 0xFF  # 8 bits
        ctia_map = {
            0b00000001: "1 pF",
            0b00000010: "2 pF",
            0b00000100: "4 pF",
            0b00001000: "8 pF",
            0b00010000: "16 pF",
            0b00100000: "32 pF",
        }
        ctia_desc = ctia_map.get(ctiacon_bits, "Unknown/unused setting")

        # Output
        print(f"    RTIA Configuration     : {rtia_desc} (bits 3:0 = {rtia_bits:04b})")
        # print(f"    SW6 Diode Parallel     : {sw6_desc} (bit 4 = {sw6_bit})")
        # print(f"    CTIA Capacitance       : {ctia_desc} (bits 12:5 = {ctiacon_bits:08b})")
