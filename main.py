import os
import time
import shutil
import multiprocessing
import statistics
from concurrent.futures import ProcessPoolExecutor

import matplotlib.pyplot as plt

def clean_companies_file(input_file, clean_file):
    """
    Clean the companies file by removing quotes and extra whitespaces
    """
    with open(input_file, 'r') as infile, open(clean_file, 'w') as outfile:
        for line in infile:
            # Remove quotes and strip whitespaces
            cleaned_line = line.strip().strip('"').strip()
            if cleaned_line:  # Only write non-empty lines
                outfile.write(cleaned_line + '\n')

def task1_sequential_write(clean_file, output_file):
    """
    Task 1: Sequential writing of companies to a new file
    """
    start_time = time.perf_counter()
    
    with open(clean_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            outfile.write(line.strip() + '\n')
    
    end_time = time.perf_counter()
    return max(end_time - start_time, 0.000001)  # Ensure non-zero time

def task2_batch_write(clean_file, output_file, batch_size=1000):
    """
    Task 2: Batch processing write
    """
    start_time = time.perf_counter()
    
    with open(clean_file, 'r') as infile, open(output_file, 'w') as outfile:
        batch = []
        for line in infile:
            batch.append(line.strip() + '\n')
            
            if len(batch) >= batch_size:
                outfile.writelines(batch)
                batch = []
        
        # Write any remaining lines
        if batch:
            outfile.writelines(batch)
    
    end_time = time.perf_counter()
    return max(end_time - start_time, 0.000001)  # Ensure non-zero time

def process_chunk(chunk):
    """
    Helper function for parallel processing
    """
    return [line.strip() + '\n' for line in chunk]

def task3_parallel_sequential_write(clean_file, output_file):
    """
    Task 3: Parallel processing while maintaining original sequence
    """
    start_time = time.perf_counter()
    
    # Read all lines
    with open(clean_file, 'r') as f:
        lines = f.readlines()
    
    # Determine number of processes
    num_processes = min(multiprocessing.cpu_count(), len(lines))
    
    # Split lines into chunks
    chunk_size = len(lines) // num_processes
    chunks = [lines[i:i+chunk_size] for i in range(0, len(lines), chunk_size)]
    
    # Process chunks in parallel
    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        processed_chunks = list(executor.map(process_chunk, chunks))
    
    # Write processed chunks maintaining original sequence
    with open(output_file, 'w') as outfile:
        for chunk in processed_chunks:
            outfile.writelines(chunk)
    
    end_time = time.perf_counter()
    return max(end_time - start_time, 0.000001)  # Ensure non-zero time

def task4_fastest_write(clean_file, output_file):
    """
    Task 4: Fastest sequential write using efficient file operations
    """
    start_time = time.perf_counter()
    
    # Use efficient file copying
    shutil.copy2(clean_file, output_file)
    
    end_time = time.perf_counter()
    return max(end_time - start_time, 0.000001)  # Ensure non-zero time

def compare_performance(times):
    """
    Task 5: Compare performance using mathematical analysis and visualization
    """
    print("\nPerformance Analysis:")
    print("------------------------")
    
    # Basic statistics
    print(f"Mean Execution Time: {statistics.mean(times):.6f} seconds")
    print(f"Median Execution Time: {statistics.median(times):.6f} seconds")
    
    # Variance and Standard Deviation
    variance = statistics.variance(times)
    std_dev = statistics.stdev(times)
    print(f"Variance: {variance:.6f}")
    print(f"Standard Deviation: {std_dev:.6f}")
    
    # Relative Performance
    fastest_time = min(times)
    performance_ratios = [fastest_time / max(t, 0.000001) for t in times]
    
    print("\nRelative Performance:")
    task_names = [
        "Sequential Write (Task 1)", 
        "Batch Processing (Task 2)", 
        "Parallel Sequential (Task 3)", 
        "Fastest Write (Task 4)"
    ]
    
    for name, time_val, ratio in zip(task_names, times, performance_ratios):
        print(f"{name}: {time_val:.6f} seconds (Speedup: {ratio:.2f}x)")
    
    # Visualization
    visualize_performance(task_names, times, performance_ratios)

def visualize_performance(task_names, times, performance_ratios):
    """
    Create visualization of performance results
    """
    plt.figure(figsize=(12, 6))
    
    # Execution Times Bar Plot
    plt.subplot(1, 2, 1)
    plt.bar(task_names, times, color='skyblue')
    plt.title('Execution Times Comparison')
    plt.ylabel('Time (seconds)')
    plt.xticks(rotation=45, ha='right')
    
    # Add time values on top of each bar
    for i, time_val in enumerate(times):
        plt.text(i, time_val, f'{time_val:.6f}', 
                 ha='center', va='bottom', fontsize=9)
    
    # Performance Speedup Bar Plot
    plt.subplot(1, 2, 2)
    plt.bar(task_names, performance_ratios, color='lightgreen')
    plt.title('Relative Performance Speedup')
    plt.ylabel('Speedup Ratio')
    plt.xticks(rotation=45, ha='right')
    
    # Add speedup values on top of each bar
    for i, ratio in enumerate(performance_ratios):
        plt.text(i, ratio, f'{ratio:.2f}x', 
                 ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('performance_analysis.png')
    plt.close()

def main():
    # Input and output file names
    input_file = 'companies.txt'
    clean_file = 'companies_cleaned.txt'
    output_files = [
        'task1_output.txt',
        'task2_output.txt',
        'task3_output.txt',
        'task4_output.txt'
    ]
    
    # Clean the input file first
    clean_companies_file(input_file, clean_file)
    
    # Execute tasks and collect times
    times = [
        task1_sequential_write(clean_file, output_files[0]),
        task2_batch_write(clean_file, output_files[1]),
        task3_parallel_sequential_write(clean_file, output_files[2]),
        task4_fastest_write(clean_file, output_files[3])
    ]
    
    # Compare performance
    compare_performance(times)

if __name__ == "__main__":
    main()