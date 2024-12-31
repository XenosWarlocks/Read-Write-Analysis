# DataProcessor Pro 📚

## 🚀 High-Performance Data Processing Framework

A comprehensive demonstration of different data processing methods in both Go and Python, featuring sequential, concurrent, batch, and asynchronous processing approaches. 

This educational project will help you understand different data processing methods in both Python and Go. We'll explore how various processing approaches perform with real data, and you'll get hands-on experience with both languages.

### 🎯 Learning Objectives

- Understand different data processing methodologies
- Compare performance characteristics of various approaches
- Learn about concurrent and parallel programming
- Practice working with file I/O in both Python and Go

### 🎯 Features

- **Multiple Processing Methods:**
  - Sequential Processing (baseline)
  - Concurrent/Threaded Processing
  - Batch Processing
  - Asynchronous Processing (Python only)

- **Performance Analysis:**
  - Real-time progress tracking
  - Memory usage monitoring
  - Processing speed comparisons
  - Visual performance metrics (Python implementation)

- **File Handling:**
  - Excel file processing
  - CSV output generation
  - Efficient data splitting
  - Buffered I/O operations

### 🛠️ Implementation Details

#### Go Implementation (`/go`)
- Utilizes goroutines for concurrent processing
- Implements worker pools for batch processing
- Features progress bars for real-time monitoring
- Supports both source and compiled execution

#### Python Implementation (`/python`)
- Uses pandas for data manipulation
- Implements threading and asyncio
- Generates synthetic data using Faker
- Creates performance visualization plots

#### Step 1: Generate Test Data
First, we'll use our Python script to create sample data. This will give us a consistent dataset to work with!

1. Install Python dependencies:
```bash
pip install pandas
pip install faker
pip install matplotlib
pip install openpyxl
```

2. Run the Python script:
```bash
python main.py
```

This will create:
- `testing_vis.xlsx`: Our input data file
- `writing_performance.png`: A visualization of Python's performance

Take a moment to look at `writing_performance.png` - it shows us how different Python processing methods compare! 📊

#### Step 2: Process Data with Go
Now that we have our data, let's see how Go handles it!

1. Install Go dependencies:
```bash
go get github.com/schollz/progressbar/v3
go get github.com/xuri/excelize/v2
```

2. Run the Go program:
```bash
# Either run directly:
go run main.go testing_vis.xlsx

# Or build and run (if you want to keep an executable):
go build -o main.exe main.go
./main.exe testing_vis.xlsx
```

Watch the progress bars - they show you real-time processing status! 🚀


## 📝 Step-by-Step Guide

### 📊 Understanding the Output

### 📊 Output

Both implementations generate:
- Processed data files
- Performance metrics
- The Python version additionally creates a performance visualization plot

Both programs will create several files:
- Python creates `testing_vis.xlsx` (input data)
- Go creates:
  - `VA_sequential.csv`
  - `VB_sequential.csv`
  - `VA_concurrent.csv`
  - `VB_concurrent.csv`
  - `VA_batch.csv`
  - `VB_batch.csv`
  
### 📈 Performance Comparison

The framework provides detailed performance metrics including:
- Processing duration
- Rows processed per second
- Memory usage
- CPU utilization

Take time to examine how the data is split between files! 🧐

### 🤔 Discussion Points

Consider these questions as you work with the code:
1. Why might we choose one processing method over another?
2. How do the implementations differ between Python and Go?
3. What are the trade-offs between memory usage and processing speed?

### 🛠️ Technical Details

#### Python Implementation
- Uses pandas for data handling
- Implements 4 processing methods:
  - Sequential (basic approach)
  - Threaded (parallel processing)
  - Batch (chunked processing)
  - Async (using asyncio)

#### Go Implementation
- Uses goroutines for concurrency
- Implements 3 processing methods:
  - Sequential (single-threaded)
  - Concurrent (using goroutines)
  - Batch (with worker pools)

### 💡 Extra Activities

1. Try modifying the data size in the Python script
2. Experiment with different batch sizes
3. Add timing measurements to compare Python and Go directly

### 🆘 Need Help?

If you're stuck, try these steps:
1. Check that you've installed all dependencies
2. Verify that `testing_vis.xlsx` was created by the Python script
3. Make sure you're running the Go program with the correct file path


### 📚 Further Reading

- [Go Concurrency Patterns](https://go.dev/blog/pipelines)
- [Python asyncio Documentation](https://docs.python.org/3/library/asyncio.html)
- [Parallel Processing in Python](https://docs.python.org/3/library/multiprocessing.html)

### 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.


### 🙏 Acknowledgments

- Thanks to the Go and Python communities for excellent documentation
- Inspired by real-world data processing challenges
---
*Remember: The journey of learning is just as important as the destination. Take your time to understand each concept, and don't hesitate to experiment with the code!* 

Happy coding 🚀
