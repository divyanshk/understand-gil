#include <pybind11/pybind11.h>
#include <thread>
#include <chrono>
#include <cmath>

double cpu_intensive_task(int iterations) {
    double result = 0.0;
    for (int i = 0; i < iterations; ++i) {
        result += std::sin(i) * std::cos(i) + std::sqrt(i + 1);
    }
    return result;
}

double cpu_task_with_gil(int iterations) {
    return cpu_intensive_task(iterations);
}

double cpu_task_without_gil(int iterations) {
    double result;
    {
        pybind11::gil_scoped_release release;
        result = cpu_intensive_task(iterations);
    }
    return result;
}

void parallel_task_with_gil(int iterations, int num_threads) {
    std::vector<std::thread> threads;
    std::vector<double> results(num_threads);
    
    for (int i = 0; i < num_threads; ++i) {
        threads.emplace_back([&results, i, iterations]() {
            results[i] = cpu_intensive_task(iterations);
        });
    }
    
    for (auto& t : threads) {
        t.join();
    }
}

void parallel_task_without_gil(int iterations, int num_threads) {
    pybind11::gil_scoped_release release;
    
    std::vector<std::thread> threads;
    std::vector<double> results(num_threads);
    
    for (int i = 0; i < num_threads; ++i) {
        threads.emplace_back([&results, i, iterations]() {
            results[i] = cpu_intensive_task(iterations);
        });
    }
    
    for (auto& t : threads) {
        t.join();
    }
}

void parallel_task_with_python_objects(int iterations, int num_threads) {
    std::vector<std::thread> threads;
    std::vector<double> results(num_threads);
    
    // Create a Python list that threads will access
    pybind11::list py_list;
    for (int i = 0; i < num_threads; ++i) {
        py_list.append(0.0);
    }
    
    // Release GIL before creating threads to prevent deadlock
    {
        pybind11::gil_scoped_release release;
        
        for (int i = 0; i < num_threads; ++i) {
            threads.emplace_back([&results, &py_list, i, iterations]() {
                // Each thread needs to acquire GIL to access Python objects
                pybind11::gil_scoped_acquire acquire;
                
                double result = cpu_intensive_task(iterations);
                results[i] = result;
                
                // Access Python object - this requires the GIL
                py_list[i] = pybind11::float_(result);
                
                // Also do some Python operations to increase GIL contention
                pybind11::object math_module = pybind11::module_::import("math");
                pybind11::object sqrt_func = math_module.attr("sqrt");
                sqrt_func(result);
            });
        }
        
        for (auto& t : threads) {
            t.join();
        }
    }
}

PYBIND11_MODULE(gil_demo, m) {
    m.doc() = "GIL demonstration module";
    
    m.def("cpu_task_with_gil", &cpu_task_with_gil, 
          "CPU intensive task that keeps the GIL");
    
    m.def("cpu_task_without_gil", &cpu_task_without_gil, 
          "CPU intensive task that releases the GIL");
    
    m.def("parallel_task_with_gil", &parallel_task_with_gil, 
          "Parallel CPU task that keeps the GIL (won't actually run in parallel)");
    
    m.def("parallel_task_without_gil", &parallel_task_without_gil, 
          "Parallel CPU task that releases the GIL (runs truly in parallel)");
    
    m.def("parallel_task_with_python_objects", &parallel_task_with_python_objects, 
          "Parallel CPU task that accesses Python objects (true GIL contention)");
}