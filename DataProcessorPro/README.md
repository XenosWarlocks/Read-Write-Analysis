# DataProcessor Pro

## 🚀 High-Performance Data Processing Framework

A comprehensive demonstration of different data processing methods in both Go and Python, featuring sequential, concurrent, batch, and asynchronous processing approaches. This project showcases best practices for handling large datasets with performance comparisons and visualizations.

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

### 📋 Requirements

#### Go Requirements
```bash
go get github.com/schollz/progressbar/v3
go get github.com/xuri/excelize/v2
```

#### Python Requirements
```bash
pip install pandas
pip install faker
pip install matplotlib
pip install openpyxl
```

### 🚀 Usage

#### Go Version
```bash
# Run from source
go run maths.go input.xlsx

# Or build and run executable
go build -o maths.exe maths.go
./maths.exe input.xlsx
```

#### Python Version
```bash
python main.py
```

### 📊 Output

Both implementations generate:
- Processed data files
- Performance metrics
- The Python version additionally creates a performance visualization plot

### 📈 Performance Comparison

The framework provides detailed performance metrics including:
- Processing duration
- Rows processed per second
- Memory usage
- CPU utilization

### 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.


### 🙏 Acknowledgments

- Thanks to the Go and Python communities for excellent documentation
- Inspired by real-world data processing challenges
```
