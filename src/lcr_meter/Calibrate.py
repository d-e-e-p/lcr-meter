

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
        comp = []
        for amp_target in self.amp_list:
            comp = [.. ]
        return comp


    def compare(res):
        comp = self.create_compare_table()




