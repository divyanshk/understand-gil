#!/usr/bin/env python3
import time
import threading
import gil_demo

def time_function(func, *args, **kwargs):
    start = time.time()
    result = func(*args, **kwargs)
    end = time.time()
    return end - start, result

def demonstrate_gil_single_thread():
    print("=== Single Thread Performance ===")
    iterations = 10_000_000
    
    print(f"Running {iterations:,} iterations...")
    
    time_with_gil, _ = time_function(gil_demo.cpu_task_with_gil, iterations)
    time_without_gil, _ = time_function(gil_demo.cpu_task_without_gil, iterations)
    
    print(f"With GIL:    {time_with_gil:.3f}s")
    print(f"Without GIL: {time_without_gil:.3f}s")
    print(f"Difference:  {abs(time_with_gil - time_without_gil):.3f}s")
    print()

def demonstrate_gil_multi_thread():
    print("=== Multi-threaded Performance ===")
    iterations = 5_000_000
    num_threads = 5
    
    print(f"Running {iterations:,} iterations on {num_threads} threads...")
    
    def run_python_threads_with_gil():
        threads = []
        for _ in range(num_threads):
            t = threading.Thread(target=gil_demo.cpu_task_with_gil, args=(iterations,))
            threads.append(t)
        
        start = time.time()
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        return time.time() - start
    
    def run_python_threads_without_gil():
        threads = []
        for _ in range(num_threads):
            t = threading.Thread(target=gil_demo.cpu_task_without_gil, args=(iterations,))
            threads.append(t)
        
        start = time.time()
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        return time.time() - start
    
    time_python_with_gil = run_python_threads_with_gil()
    time_python_without_gil = run_python_threads_without_gil()
    
    time_cpp_with_gil = time_function(gil_demo.parallel_task_with_gil, iterations, num_threads)[0]
    time_cpp_without_gil = time_function(gil_demo.parallel_task_without_gil, iterations, num_threads)[0]
    time_cpp_with_python_objects = time_function(gil_demo.parallel_task_with_python_objects, iterations, num_threads)[0]
    
    print(f"Python threads (with GIL):     {time_python_with_gil:.3f}s")
    print(f"Python threads (without GIL):  {time_python_without_gil:.3f}s") 
    print(f"C++ threads (with GIL):        {time_cpp_with_gil:.3f}s")
    print(f"C++ threads (without GIL):     {time_cpp_without_gil:.3f}s")
    print(f"C++ threads (accessing Python): {time_cpp_with_python_objects:.3f}s")
    
    speedup = time_python_with_gil / time_python_without_gil
    python_obj_slowdown = time_cpp_with_python_objects / time_cpp_without_gil
    print(f"Speedup when releasing GIL:    {speedup:.2f}x")
    print(f"Slowdown when accessing Python objects: {python_obj_slowdown:.2f}x")
    print()

def main():
    print("Python GIL Demonstration")
    print("=" * 50)
    print()
    
    demonstrate_gil_single_thread()
    demonstrate_gil_multi_thread()
    
    print("Key Observations:")
    print("1. Single-threaded performance is similar with/without GIL")
    print("2. Multi-threaded performance improves dramatically when GIL is released")
    print("3. Python threads that release GIL can run truly in parallel")
    print("4. C++ code can release GIL to enable parallel execution")
    print("5. C++ threads accessing Python objects are serialized by the GIL")

if __name__ == "__main__":
    main()