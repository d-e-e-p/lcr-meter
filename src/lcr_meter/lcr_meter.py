import adi
import CN0565Tester


if __name__ == "__main__":  # pragma: no cover
    dev = adi.cn0565(uri="serial:/dev/cu.usbmodem1202,230400,8n1n")
    tester = CN0565Tester(dev)
    amp_list = [100, 200, 500]
    freq_list = [1000, 2000, 5000, 10000, 20000]

    results = tester.run(amp_list, freq_list)

    for idx, (real, imag) in enumerate(results):
        print(f"Electrodes {idx*2}/{idx*2+1}: Re={real:.2f} Ω, Im={imag:.2f} Ω")

