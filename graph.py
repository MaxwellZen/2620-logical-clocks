import sys
import ast 
import matplotlib.pyplot as plt

name = sys.argv[1]

for t in range(1,6):
    for i in range(3):
        f = open(f"data/{name}{t}_{i}_data.txt", 'r')
        cps = int(f.readline()[19:])
        times = ast.literal_eval(f.readline()[14:])
        log_times = ast.literal_eval(f.readline()[21:])
        plt.plot(times, log_times, label = f"id={i},cps={cps}")
    plt.xlabel("System Time (seconds)")
    plt.ylabel("Logical Clock Time")
    plt.title(f"Settings: {name}, Trial: {t}")
    plt.legend()
    plt.savefig(f"graphs/{name}{t}.png", dpi=300)
    plt.close()