import csv, subprocess

traces = ["swim.trace", "bzip.trace", "gcc.trace", "sixpack.trace"]
algs = ["rand", "lru", "clock"]
frames = [2, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256, 384, 512]

with open("results_coarse.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["trace","algorithm","frames","events","disk_reads","disk_writes","page_fault_rate"])
    for t in traces:
        for a in algs:
            for fr in frames:
                out = subprocess.check_output(
                    ["python3", "memsim.py", t, str(fr), a, "quiet"],
                    text = True
                )

                def grab(prefix):
                    for line in out.splitlines():
                        if line.startswith(prefix):
                            return line.split(":")[1].strip()
                events = grab("events in trace")
                reads = grab("total disk reads")
                writes = grab("total disk writes")
                pfr = grab("page fault rate")
                w.writerow([t, a, fr, events, reads, writes, pfr])