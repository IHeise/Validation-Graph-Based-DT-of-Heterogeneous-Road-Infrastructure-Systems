import time
import tracemalloc
import threading
import psutil
import os
import numpy as np
import pandas as pd
from ... import SoS_Querying
from ... import GraphCreation

process = psutil.Process(os.getpid())

def monitor_memory(stop_event, samples):
    while not stop_event.is_set():
        samples.append(process.memory_info().rss)
        time.sleep(0.05)

def warmup(func, *args):
    func(*args)
    func(*args)
    func(*args)


def measure(func, *args, repeats=1,teardown=None):



    times = []
    cpu_times = []
    mem_peaks = []
    cpu_times_system = []
    cpu_times_user = []
    i = 1
    for _ in range(repeats):
        samples = []
        stop_event = threading.Event()
        monitor_thread = threading.Thread(
            target=monitor_memory,
            args=(stop_event, samples)
        )

        #experiment run
        start_cpu = process.cpu_times().user + process.cpu_times().system
        start_cpu_user = process.cpu_times().user
        start_cpu_system = process.cpu_times().system
        start = time.perf_counter()
        monitor_thread.start()

        func(*args)

        stop_event.set()
        monitor_thread.join()

        end = time.perf_counter()
        end_cpu_user = process.cpu_times().user
        end_cpu_system = process.cpu_times().system

        end_cpu = process.cpu_times().user + process.cpu_times().system

        peak_mem = max(samples) if samples else process.memory_info().rss


        times.append(end - start)
        cpu_times.append(end_cpu - start_cpu)
        cpu_times_user.append(end_cpu_user - start_cpu_user)
        cpu_times_system.append(end_cpu_system - start_cpu_system)
        mem_peaks.append(peak_mem / (1024**2))


        # cleanup temprel after measurement

        if teardown:
            teardown(*args)

        print(f"---> run {i} finished")
        i=i+1


    return {
        "mean_time": np.mean(times),
        "std_time": np.std(times),
        "mean_cpu_time": np.mean(cpu_times),
        "std_cpu_time": np.std(cpu_times),
        "mean_cpu_time_user": np.mean(cpu_times_user),
        "std_cpu_time_user": np.std(cpu_times_user),
        "mean_cpu_time_system": np.mean(cpu_times_system),
        "std_cpu_time_system": np.std(cpu_times_system),
        "mean_mem_MB": np.mean(mem_peaks),
        "std_mem_MB": np.std(mem_peaks),
    }

def run_scalability(func, sizes, repeats=7):
    results = []


    for n in sizes:

        teardown_db(n)

        warmup(func, n)

        data = n

        teardown_db(n)

        stats = measure(func, data, repeats=repeats,teardown=teardown_db)
        results.append({
            "n": n,
            **stats
        })


        print(f"n={n} done")

    return pd.DataFrame(results)


def teardown_db(n):

    GraphCreation(DataBaseName=f"sos-temp-{n}").cleanDataBase()

    # make sure temprel its empty
    c = 1
    query = """CALL db.stats.retrieve('GRAPH COUNTS')
                yield data
                return data.nodes[0]"""
    while c != 0:
        result=GraphCreation(DataBaseName=f"sos-temp-{n}").send_query(query)
        record = result[0]
        c = record["data.nodes[0]"]["count"]







