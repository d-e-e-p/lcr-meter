import adi

from .CN0565Tester import CN0565Tester
from .ExtractLCR import ExtractLCR


def main():  # pragma: no cover
    dev = adi.cn0565(uri="serial:/dev/cu.usbmodem1202,230400,8n1n")

    tester = CN0565Tester(dev)
    amp_list = [100, 200, 500]
    freq_list = [1000, 2000, 5000, 10000, 20000]
    seq_list = range(12)
    res_impedance = tester.run(seq_list, amp_list, freq_list)

    calculator = ExtractLCR(seq_list, amp_list, freq_list)
    res_lcr = calculator.compute(res_impedance)

    for seq, amp, L, C, R in res_lcr:
        print(f"{seq=} {amp=} {L=} {C=} {R=}")


if __name__ == "__main__":  # pragma: no cover
    main()
