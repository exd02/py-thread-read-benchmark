import subprocess
import statistics
import time
import csv
import platform
import psutil
import cpuinfo 
import sys

REPEATS = 30
WARMUPS = 3  # the first n tests will be ignored for the final calculation
THREAD_COUNTS = [2,4,8,16]


def get_system_info():
    """Collect system information for benchmark header using py-cpuinfo"""
    cpu_info = cpuinfo.get_cpu_info()
    
    system_info = {
        "Processor": cpu_info['brand_raw'],  # Clean CPU name like "AMD Ryzen 7 5700X"
        "Physical Cores": psutil.cpu_count(logical=False),
        "Total Threads": psutil.cpu_count(logical=True),
        "RAM (GB)": round(psutil.virtual_memory().total / (1024**3), 2),
        "Operating System": f"{platform.system()} {platform.release()}"
    }
    return system_info


def run_command(command):
    start = time.perf_counter()
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    end = time.perf_counter()
    return end - start


# filter outliers using IQR method
def filter_outliers(times):
    q = statistics.quantiles(times, n=4)
    iqr = q[2] - q[0]
    lower = q[0] - 1.5 * iqr
    upper = q[2] + 1.5 * iqr
    outlier_flags = [(t < lower or t > upper) for t in times]
    return outlier_flags


def benchmark_program(label, command):
    times = []

    for _ in range(REPEATS):
        elapsed_time = run_command(command)
        times.append(elapsed_time)

    outlier_flags = filter_outliers(times)

    states = []
    for i, t in enumerate(times):
        if i < WARMUPS:
            states.append("warmup")
        elif outlier_flags[i]:
            states.append("outlier")
        else:
            states.append("valid")

    filtered_times = []
    for i in range(len(times)):
        if states[i] == "valid":
            filtered_times.append(times[i])
    
    mean_time = statistics.mean(filtered_times) if filtered_times else float('NaN')

    return {
        "label": label,
        "times": times,
        "states": states,
        "mean_time": mean_time
    }


def save_results_csv(system_info, results, filename="benchmark_results.csv"):
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        writer.writerow(["SYSTEM INFORMATION"])
        for key, value in system_info.items():
            writer.writerow([key, value])
        
        # empty line to separate
        writer.writerow([])
        
        writer.writerow(["BENCHMARK RESULTS"])
        writer.writerow(["Label", "Execution", "Time (s)", "Status"])
        
        for result in results:
            for i, (t, state) in enumerate(zip(result["times"], result["states"])):
                writer.writerow([result["label"], f"run_{i+1}", t, state])
            writer.writerow([result["label"], "mean_filtered", result["mean_time"], "computed"])


def main():
    system_info = get_system_info()

    results = []
    results.append(benchmark_program("A.py", [sys.executable, "A.py"]))

    for threads in THREAD_COUNTS:
        for executor in ["process", "thread"]:
            label = f"B.py - {threads} threads - {executor.capitalize()}"
            command = [sys.executable, "B.py", str(threads), executor]
            results.append(benchmark_program(label, command)) 

    save_results_csv(system_info, results)
    print("Benchmark completed. Results saved to 'benchmark_results.csv'")


if __name__ == "__main__":
    main()