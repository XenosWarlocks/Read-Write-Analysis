import os
import time
import shutil
import multiprocessing
import statistics
import threading
from queue import Queue, Empty
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import matplotlib.pyplot as plt
import asyncio  # For async operations
import aiofiles  # For async file operations

def clean_companies_file(input_file, clean_file):
    """
    Clean the companies file by removing quotes and extra whitespaces
    """
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found!")
        return

    with open(input_file, 'r') as infile, open(clean_file, 'w') as outfile:
        for line in infile:
            cleaned_line = line.strip().strip('"').strip()
            if cleaned_line:
                outfile.write(cleaned_line + '\n')

def task1_sequential_write(clean_file, output_file):
    start_time = time.perf_counter()
    
    with open(clean_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            outfile.write(line.strip() + '\n')
    
    end_time = time.perf_counter()
    return max(end_time - start_time, 0.000001)

def task2_batch_write(clean_file, output_file, batch_size=1000):
    start_time = time.perf_counter()
    
    with open(clean_file, 'r') as infile, open(output_file, 'w') as outfile:
        batch = []
        for line in infile:
            batch.append(line.strip() + '\n')
            if len(batch) >= batch_size:
                outfile.writelines(batch)
                batch = []
        
        if batch:
            outfile.writelines(batch)
    
    end_time = time.perf_counter()
    return max(end_time - start_time, 0.000001)

def process_chunk(chunk):
    return [line.strip() + '\n' for line in chunk]

def task3_parallel_sequential_write(clean_file, output_file):
    start_time = time.perf_counter()
    
    with open(clean_file, 'r') as f:
        lines = f.readlines()
    
    num_processes = min(multiprocessing.cpu_count(), len(lines))
    chunk_size = len(lines) // num_processes
    chunks = [lines[i:i+chunk_size] for i in range(0, len(lines), chunk_size)]
    
    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        processed_chunks = list(executor.map(process_chunk, chunks))
    
    with open(output_file, 'w') as outfile:
        for chunk in processed_chunks:
            outfile.writelines(chunk)
    
    end_time = time.perf_counter()
    return max(end_time - start_time, 0.000001)

def task4_fastest_write(clean_file, output_file):
    start_time = time.perf_counter()
    shutil.copy2(clean_file, output_file)
    end_time = time.perf_counter()
    return max(end_time - start_time, 0.000001)

def task5_sort_write(clean_file, output_file):
    start_time = time.perf_counter()
    
    with open(clean_file, 'r') as infile:
        lines = infile.readlines()
        lines.sort()  # Sort the lines alphabetically
    
    with open(output_file, 'w') as outfile:
        outfile.writelines(lines)
    
    end_time = time.perf_counter()
    return max(end_time - start_time, 0.000001)

async def task6_async_write(clean_file, output_file):
    """
    Asynchronous file writing using aiofiles
    """
    start_time = time.perf_counter()
    
    async with aiofiles.open(clean_file, 'r') as infile:
        content = await infile.read()
        lines = content.splitlines()
    
    async with aiofiles.open(output_file, 'w') as outfile:
        for line in lines:
            await outfile.write(line + '\n')
    
    end_time = time.perf_counter()
    return max(end_time - start_time, 0.000001)

def task7_threaded_queue_write(clean_file, output_file, num_threads=4):
    """
    Multi-threaded writing using a queue system
    """
    start_time = time.perf_counter()
    
    # Read all lines
    with open(clean_file, 'r') as infile:
        lines = infile.readlines()
    
    # Create a queue to hold the lines
    line_queue = Queue()
    for line in lines:
        line_queue.put(line.strip())
    
    # Create a lock for file writing
    file_lock = threading.Lock()
    
    def worker():
        while True:
            try:
                # Check if queue is empty
                if line_queue.empty():
                    break
                    
                line = line_queue.get()
                with file_lock:
                    with open(output_file, 'a') as outfile:
                        outfile.write(line + '\n')
                line_queue.task_done()
            except Exception as e:
                print(f"Error in worker thread: {e}")
                break
    
    # Create and start threads
    threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)
    
    # Wait for all threads to complete
    for t in threads:
        t.join()
    
    end_time = time.perf_counter()
    return max(end_time - start_time, 0.000001)

def task8_thread_pool_write(clean_file, output_file):
    """
    Using ThreadPoolExecutor for parallel writing
    """
    start_time = time.perf_counter()
    
    with open(clean_file, 'r') as infile:
        lines = infile.readlines()
    
    def write_chunk(chunk):
        with open(output_file, 'a') as outfile:
            for line in chunk:
                outfile.write(line.strip() + '\n')
    
    # Split lines into chunks
    num_threads = min(threading.active_count() * 2, len(lines))
    chunk_size = max(1, len(lines) // num_threads)
    chunks = [lines[i:i+chunk_size] for i in range(0, len(lines), chunk_size)]
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        executor.map(write_chunk, chunks)
    
    end_time = time.perf_counter()
    return max(end_time - start_time, 0.000001)

def task9_mixed_pool_write(clean_file, output_file):
    """
    Combining both process and thread pools for hybrid parallelism
    """
    start_time = time.perf_counter()
    
    with open(clean_file, 'r') as infile:
        lines = infile.readlines()
    
    # Move process_chunk outside to make it picklable
    num_processes = multiprocessing.cpu_count()
    chunk_size = max(1, len(lines) // num_processes)
    chunks = [lines[i:i+chunk_size] for i in range(0, len(lines), chunk_size)]
    
    # Process data in parallel
    with ProcessPoolExecutor(max_workers=num_processes) as process_executor:
        processed_chunks = []
        for chunk in chunks:
            processed_chunk = [line.strip() + '\n' for line in chunk]
            processed_chunks.append(processed_chunk)
    
    # Write processed chunks using threads
    def write_chunk(processed_chunk):
        with open(output_file, 'a') as outfile:
            outfile.writelines(processed_chunk)
    
    with ThreadPoolExecutor(max_workers=num_processes*2) as thread_executor:
        thread_executor.map(write_chunk, processed_chunks)
    
    end_time = time.perf_counter()
    return max(end_time - start_time, 0.000001)

async def task10_chunked_async_write(clean_file, output_file, chunk_size=1000):
    """
    Chunked asynchronous writing with multiple coroutines
    """
    start_time = time.perf_counter()
    
    async def write_chunk(chunk, semaphore):
        async with semaphore:
            async with aiofiles.open(output_file, 'a') as outfile:
                for line in chunk:
                    await outfile.write(line.strip() + '\n')
    
    # Read all lines
    async with aiofiles.open(clean_file, 'r') as infile:
        content = await infile.read()
        lines = content.splitlines()
    
    # Split into chunks
    chunks = [lines[i:i+chunk_size] for i in range(0, len(lines), chunk_size)]
    
    # Create semaphore to limit concurrent file operations
    semaphore = asyncio.Semaphore(5)
    
    # Create tasks for each chunk
    tasks = [write_chunk(chunk, semaphore) for chunk in chunks]
    await asyncio.gather(*tasks)
    
    end_time = time.perf_counter()
    return max(end_time - start_time, 0.000001)


def compare_performance(times):
    print("\nPerformance Analysis:")
    print("------------------------")
    
    print(f"Mean Execution Time: {statistics.mean(times):.6f} seconds")
    print(f"Median Execution Time: {statistics.median(times):.6f} seconds")
    
    variance = statistics.variance(times)
    std_dev = statistics.stdev(times)
    print(f"Variance: {variance:.6f}")
    print(f"Standard Deviation: {std_dev:.6f}")
    
    fastest_time = min(times)
    performance_ratios = [fastest_time / max(t, 0.000001) for t in times]
    
    print("\nRelative Performance:")
    task_names = [
        "Sequential Write (Task 1)", 
        "Batch Processing (Task 2)", 
        "Parallel Sequential (Task 3)", 
        "Fastest Write (Task 4)",
        "Alphabetically Write (Task 5)"
    ]
    
    for name, time_val, ratio in zip(task_names, times, performance_ratios):
        print(f"{name}: {time_val:.6f} seconds (Speedup: {ratio:.2f}x)")
    
    visualize_performance(task_names, times, performance_ratios)

def visualize_performance(task_names, times, performance_ratios):
    # Ensure the number of names matches the number of times
    if len(task_names) != len(times):
        task_names = [f"Task {i+1}" for i in range(len(times))]  # Generate task names dynamically
    
    plt.figure(figsize=(12, 6))
    
    # Execution times comparison
    plt.subplot(1, 2, 1)
    plt.bar(task_names, times, color='skyblue')
    plt.title('Execution Times Comparison')
    plt.ylabel('Time (seconds)')
    plt.xticks(rotation=45, ha='right')
    for i, time_val in enumerate(times):
        plt.text(i, time_val, f'{time_val:.6f}', ha='center', va='bottom', fontsize=9)
    
    # Relative performance speedup
    plt.subplot(1, 2, 2)
    plt.bar(task_names, performance_ratios, color='lightgreen')
    plt.title('Relative Performance Speedup')
    plt.ylabel('Speedup Ratio')
    plt.xticks(rotation=45, ha='right')
    for i, ratio in enumerate(performance_ratios):
        plt.text(i, ratio, f'{ratio:.2f}x', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('performance_analysis.png')
    plt.close()


def main():
    print(f"Current working directory: {os.getcwd()}")
    print(f"Files in directory: {os.listdir()}")
    input_file = 'companies.txt'
    clean_file = 'companies_cleaned.txt'
    output_files = [
        'task1_output.txt',
        'task2_output.txt',
        'task3_output.txt',
        'task4_output.txt',
        'task5_output.txt',
        'task6_output.txt',
        'task7_output.txt',
        'task8_output.txt',
        'task9_output.txt',
        'task10_output.txt'
    ]
    
    # Clean the input file
    clean_companies_file(input_file, clean_file)

    try:
        clean_companies_file(input_file, clean_file)
        if not os.path.exists(clean_file):
            print(f"Error: Failed to create {clean_file}")
            return
    
        # Run synchronous tasks
        times = [
            task1_sequential_write(clean_file, output_files[0]),
            task2_batch_write(clean_file, output_files[1]),
            task3_parallel_sequential_write(clean_file, output_files[2]),
            task4_fastest_write(clean_file, output_files[3]),
            task5_sort_write(clean_file, output_files[4]),
            task7_threaded_queue_write(clean_file, output_files[6]),
            task8_thread_pool_write(clean_file, output_files[7]),
            task9_mixed_pool_write(clean_file, output_files[8])
        ]
        
        # Run async tasks
        async def run_async_tasks():
            task6_time = await task6_async_write(clean_file, output_files[5])
            task10_time = await task10_chunked_async_write(clean_file, output_files[9])
            return [task6_time, task10_time]
        
        # Add async tasks times to the list
        async_times = asyncio.run(run_async_tasks())
        times.extend(async_times)
        
        compare_performance(times)

    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please ensure the input file exists in the correct directory:")
        print(f"Current working directory: {os.getcwd()}")
        
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
