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
                data = [(freq, z) for seq, amp, freq, z in res_f_vs_impedance if seq == seq_target and amp == amp_target]
                L, C, R = self.lcr_from_impedance(data)
                res.append([seq_target, amp_target, L, C, R])


        return res

    def lcr_from_impedance(self, data):
        pass
