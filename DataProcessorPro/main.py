import pandas as pd
import time
import asyncio
# import threading
from concurrent.futures import ThreadPoolExecutor
from faker import Faker
import matplotlib.pyplot as plt
from typing import List, Dict

class DataGenerator:
    def __init__(self):
        self.fake = Faker()
        
    def generate_dataset(self, size: int) -> List[Dict]:
        data = []
        departments = ['HR', 'IT', 'Sales', 'Marketing', 'Finance']
        batch_names = ['Morning', 'Afternoon', 'Evening', 'Night']
        
        for _ in range(size):
            data.append({
                'Company Name': self.fake.company(),
                'Company URL': self.fake.url(),
                'Email': self.fake.email(),
                'Dept': self.fake.random_element(departments),
                'Phone Number': self.fake.phone_number(),
                'Batch Name': self.fake.random_element(batch_names),
                'First Name': self.fake.first_name(),
                'Last Name': self.fake.last_name()
            })
        return data

class FileWritingDemo:
    def __init__(self, total_records: int = 10000):
        self.total_records = total_records
        self.data_generator = DataGenerator()
        self.results = {}

    def sequential_write(self) -> float:
        """Sequential writing - one record at a time"""
        start_time = time.time()
        
        data = self.data_generator.generate_dataset(self.total_records)
        df = pd.DataFrame(data)
        df.to_excel('testing_vis.xlsx', index=False)
        
        return time.time() - start_time

    def threaded_write(self) -> float:
        """ThreadPoolExecutor to parallelize data generation and writing"""
        def generate_chunk(size: int) -> List[Dict]:
            return self.data_generator.generate_dataset(size)

        start_time = time.time()
        chunk_size = self.total_records // 5
        
        # Generate data in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(generate_chunk, chunk_size)
                for _ in range(5)
            ]
            chunks = [future.result() for future in futures]
        
        # Combine chunks and write to file
        all_data = []
        for chunk in chunks:
            all_data.extend(chunk)
        
        df = pd.DataFrame(all_data)
        df.to_excel('testing_vis.xlsx', index=False)
        
        return time.time() - start_time

    def batch_write(self) -> float:
        """Batch processing - generate and write in batches"""
        start_time = time.time()
        batch_size = 2000
        all_data = []
        
        for i in range(0, self.total_records, batch_size):
            # Generate batch
            batch_data = self.data_generator.generate_dataset(
                min(batch_size, self.total_records - i)
            )
            all_data.extend(batch_data)
            
        # Write complete dataset
        df = pd.DataFrame(all_data)
        df.to_excel('testing_vis.xlsx', index=False)
        
        return time.time() - start_time

    async def async_write(self) -> float:
        """Asynchronous writing using asyncio"""
        async def generate_async_chunk(size: int) -> List[Dict]:
            # Simulate async data generation
            return self.data_generator.generate_dataset(size)

        start_time = time.time()
        chunk_size = self.total_records // 5
        
        # Generate data chunks asynchronously
        tasks = [
            generate_async_chunk(chunk_size)
            for _ in range(5)
        ]
        chunks = await asyncio.gather(*tasks)
        
        # Combine chunks and write to file
        all_data = []
        for chunk in chunks:
            all_data.extend(chunk)
            
        df = pd.DataFrame(all_data)
        df.to_excel('testing_vis.xlsx', index=False)
        
        return time.time() - start_time

    def run_comparison(self):
        print("\nRunning performance comparison...")
        
        # Sequential Write
        print("\nTesting Sequential Write...")
        self.results['Sequential'] = self.sequential_write()
        
        # Threaded Write
        print("Testing Threaded Write...")
        self.results['Threaded'] = self.threaded_write()
        
        # Batch Write
        print("Testing Batch Write...")
        self.results['Batch'] = self.batch_write()
        
        # Async Write
        print("Testing Async Write...")
        self.results['Async'] = asyncio.run(self.async_write())
        
        self.create_visualization()
        self.print_results()

    def create_visualization(self):
        plt.figure(figsize=(10, 6))
        
        # Create bars
        methods = list(self.results.keys())
        times = list(self.results.values())
        bars = plt.bar(methods, times)
        
        # Customize plot
        plt.title(f'File Writing Performance Comparison\n({self.total_records:,} records)')
        plt.xlabel('Method')
        plt.ylabel('Time (seconds)')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}s',
                    ha='center', va='bottom')
        
        # Add method descriptions
        descriptions = {
            'Sequential': 'Single-threaded\nwrite',
            'Threaded': 'Parallel data\ngeneration',
            'Batch': 'Batch-by-batch\nprocessing',
            'Async': 'Asynchronous\nprocessing'
        }
        
        # Add descriptions under bars
        for i, method in enumerate(methods):
            plt.text(i, -0.1, descriptions[method],
                    ha='center', va='top',
                    transform=plt.gca().get_xaxis_transform())
        
        plt.tight_layout()
        plt.savefig('writing_performance.png', bbox_inches='tight', dpi=300)
        plt.close()

    def print_results(self):
        print("\nPerformance Results:")
        print("-" * 50)
        for method, duration in self.results.items():
            print(f"{method:12} : {duration:.2f} seconds")
        print("\nVisualization saved as 'writing_performance.png'")

if __name__ == "__main__":
    demo = FileWritingDemo(10000)
    demo.run_comparison()
    
# python main.py
