import adi

from .CN0565Tester import CN0565Tester
from .ExtractLCR import ExtractLCR
from .Calibrate import Calibrate


def main():  # pragma: no cover

    dev0 = adi.cn0565(uri="serial:COM3, 230400, 8n1n")
    ctx = dev0.ctx
    print(f"connected: {ctx.attrs}")

    dev1 = ctx.find_device("ad5940")  
    dev2 = ctx.find_device("adg2128")  

    print(f" found device {dev1.name}")
    for name, attr in dev1.attrs.items():
        print(f"    {name} = {attr.value}") 

    print(f" found device {dev2.name}")
    for name, attr in dev2.attrs.items():
        print(f"    {name} = {attr.value}") 

    tester = CN0565Tester(dev0, dev1, dev2)
    amp_list = [100, 200, 500]
    freq_list = [1000, 2000, 5000, 10000, ]
    amp_list = [100, ]
    seq_list = range(12)
    # seq_list = [6]
    res_impedance = tester.run(seq_list, amp_list, freq_list)

    calculator = ExtractLCR(seq_list, amp_list, freq_list)
    res_lcr = calculator.compute(res_impedance)

    print(" lcr estimates: ")
    for seq, amp, L, C, R in res_lcr:
        print(f"{seq=} {amp=} {L=} {C=} {R=}")

    print(" comparison: ")
    calibrate = Calibrate(seq_list, amp_list)
    res_comp = calibrate.compare(res_lcr)
    for amp, Rsq, formula, _ in res_comp['R']:
        print(f"R {amp=} {Rsq=} {formula}")
    for amp, Rsq, formula, _ in res_comp['L']:
        print(f"L {amp=} {Rsq=} {formula}")

if __name__ == "__main__":  # pragma: no cover
    main()
