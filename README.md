# Python GIL Demonstration

This project demonstrates Python's Global Interpreter Lock (GIL) behavior by comparing performance between code that holds the GIL vs code that releases it.

## What it demonstrates

- **Single-threaded performance**: Similar with/without GIL
- **Multi-threaded performance**: Dramatic improvement when GIL is released
- **True parallelism**: C++ extensions can release GIL to enable parallel execution

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Build the C++ extension:
```bash
python setup.py build_ext --inplace
```

3. Run the demonstration:
```bash
python main.py
```

## How it works

### C++ Extension (`gil_demo.cpp`)
- `cpu_task_with_gil()`: Keeps GIL during CPU-intensive work
- `cpu_task_without_gil()`: Releases GIL using `pybind11::gil_scoped_release`
- `parallel_task_*()`: Demonstrates threading behavior with/without GIL

### Python Main (`main.py`)
- Compares single-threaded performance
- Demonstrates multi-threaded behavior
- Shows the performance impact of GIL release

## Key Concepts

**GIL (Global Interpreter Lock)**: Python's mechanism that ensures only one thread executes Python bytecode at a time.

**Releasing GIL**: C extensions can release the GIL during CPU-intensive operations, allowing true parallelism. **Note**: When you call a C++ function via pybind11 from Python, the GIL (Global Interpreter Lock) is not automatically released. If you want the GIL to be released while executing C++ code, you must explicitly release it in your C++ function using: `pybind11::gil_scoped_release release;` 

**Performance Impact**: Without GIL, multi-threaded CPU-bound tasks can achieve near-linear speedup.

**C++ threads accessing Python objects**: this requires acquiring the GIL and can impact performance. Also, if you're creating threads that need the GIL, release it first so they can acquire it.