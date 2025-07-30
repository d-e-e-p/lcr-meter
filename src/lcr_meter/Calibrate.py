

class Calibrate:
    def __init__(self, seq_list, amp_list):
        self.seq_list = seq_list
        self.amp_list = amp_list
        self.expected_r = """
            470
            1000
            2000
            20000
            10
            120
            1
            7500
            47
            68
            100
            220
        """.split()

    def create_compare_table(self, res_lcr):
        # res in format [seq_target, amp_target, L, C, R]
        comp = {}
        for seq, amp, L, C, R in res_lcr:
            expected_r = self.expected_r[seq]
            measured_r = R
            comp[amp].append([expected_r, measured_r])

        return comp

    def compare(self, res_lcr):
        res = []
        comp = self.create_compare_table()
        for amp, table in cmp:
            # create regression table to map measured_r to expected_r

            res.append(amp, rsq, formula...)

        return res



