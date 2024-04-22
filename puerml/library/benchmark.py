import time
import json

__all__ = ['Benchmark']


class Benchmark:
    data = {}

    @staticmethod
    def time(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result     = func(*args, **kwargs)
            end_time   = time.time()

            # Update statistics
            func_name = func.__name__
            if func_name not in Benchmark.data:
                Benchmark.data[func_name] = [0, 0.0]  # Initialize [count, total_time]
            Benchmark.data[func_name][0] += 1  # Increment count
            Benchmark.data[func_name][1] += (end_time - start_time)  # Increment total time

            return result
        return wrapper

    @staticmethod
    def print():
        for f in Benchmark.data:
            print(f.ljust(30), str(Benchmark.data[f][0]).ljust(7), Benchmark.data[f][1])