import asyncio
from functools import lru_cache
import statistics
import aiohttp
import concurrent.futures
from matplotlib import pyplot as plt
import requests
import re
from typing import List, Dict, Tuple
import time

class WebsiteChecker:
    def __init__(
        self,
        timeout: int = 3,
        max_concurrent: int = 10,
        rate_limit: float = 0.2  # Delay between requests in seconds
    ):
        """
        Initialize WebsiteChecker with configurable parameters.

        Args:
            timeout (int): Request timeout in seconds
            max_concurrent (int): Maximum concurrent connections
            rate_limit (float): Minimum delay between requests
        """
        self.timeout = timeout
        self.max_concurrent = max_concurrent
        self.rate_limit = rate_limit
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.last_request_time = 0
        # self.session = requests.Session()

    @staticmethod
    @lru_cache(maxsize=1000)
    def clean_company_name(name: str) -> str:
        """
        Optimized company name cleaning with caching and comprehensive normalization.
        """
        name = name.strip('\ufeff"\'') # Remove any BOM (\ufeff) character at the start or end of the name.

        # Pre-compiled regex for suffix removal
        suffixes = [ # These patterns are designed to match various company suffixes in text, such as "Inc.", "Corp.", "Ltd.", and others, with optional variations in spacing and case.
            re.compile(r'\s+Inc\.?$', re.IGNORECASE),
            re.compile(r'\s+Corp\.?$', re.IGNORECASE),
            re.compile(r'\s+Incorporated$', re.IGNORECASE),
            re.compile(r'\s+Corporation$', re.IGNORECASE),
            re.compile(r'\s+Limited$', re.IGNORECASE),
            re.compile(r'\s+Ltd\.?$', re.IGNORECASE)
        ]

        for suffix in suffixes:
            name = suffix.sub('', name)

        # Remove special characters spCharRmv
        name = name.translate(str.maketrans('', '', '!@#$%^&*()_+-=[]{}|;:,.<>?')) # ()

        return ' '.join(name.split()) # Remove extra spaces
    
    def generate_website_urls(self, name: str) -> List[str]:
        """
        Generate multiple URL variations with intelligent guessing.
        """
        cleaned_name = self.clean_company_name(name).lower().replace(' ', '')
        
        url_variations = [
            f"https://www.{cleaned_name}.com",
            f"https://{cleaned_name}.com",
            f"http://www.{cleaned_name}.com",
            f"http://{cleaned_name}.com",
            f"https://{cleaned_name}.net",
            f"https://www.{cleaned_name}.org"
        ]

        return url_variations
    
    async def rate_limit(self):
        """
        Implement simple rate limiting to prevent overwhelming servers.
        """
        current_time = time.time()
        elapsed = current_time - self.last_request_time

        if elapsed < self.rate_limit:
            await asyncio.sleep(self.rate_limit - elapsed)

        self.last_request_time = time.time()

    async def check_website_async(self, session: aiohttp.ClientSession, company_name: str) -> Dict:
        """
        Asynchronous website status check with rate limiting and robust error handling.
        """
        start_time = time.time()
        cleaned_name = self.clean_company_name(company_name)

        async with self.semaphore:
            # Apply rate limiting
            await self.rate_limit()

            for url in self.generate_website_urls(company_name):
                try:
                    async with session.get(url, timeout=self.timeout) as response:
                        total_time = time.time() - start_time
                        return {
                            'original_name': company_name,
                            'cleaned_name': cleaned_name,
                            'url': url,
                            'status_code': response.status,
                            'time_taken': total_time
                        }
                    
                except (aiohttp.ClientError, asyncio.TimeoutError):
                    continue
        
        # If no URL works
        total_time = time.time() - start_time
        return {
            'original_name': company_name,
            'cleaned_name': cleaned_name,
            'url': 'N/A',
            'status_code': None,
            'time_taken': total_time
        }
    async def check_websites_async(self, companies: List[str]) -> List[Dict]:
        """
        Asynchronously check websites with improved concurrency management.
        """
        async with aiohttp.ClientSession() as session:
            task = [self.check_website_async(session, company) for company in companies]
            return await asyncio.gather(*task)
        
    def run_async(self, companies: List[str]) -> List[Dict]:
        """
        Run async website checks.
        """
        start_time = time.time()
        results = asyncio.run(self.check_websites_async(companies))
        total_execution_time = time.time() - start_time

        print(f"\nAsync Execution Total Time: {total_execution_time:.2f} seconds")
        return results
    
def check_websites_sequential(companies: List[str], timeout: int = 3) -> List[Dict]:
    """
    Sequential website status checking method.
    """
    start_time = time.time()
    results = []

    for company in companies:
        cleaned_name = WebsiteChecker.clean_company_name(company)
        urls = WebsiteChecker(timeout=timeout).generate_website_urls(company)

        for url in urls:
            try:
                response = requests.get(url, timeout=timeout)
                results.append({
                    'original_name': company,
                    'cleaned_name': cleaned_name,
                    'url': url,
                    'status_code': response.status_code,
                    'time_taken': response.elapsed.total_seconds()
                })
                break  # If successful, move to the next company

            except requests.RequestException:
                continue
    
    total_execution_time = time.time() - start_time
    print(f"\nSequential Execution Total Time: {total_execution_time:.2f} seconds")
    return results

def check_websites_parallel(companies: List[str], max_workers: int = 10, timeout: int = 3) -> List[Dict]:
    """
    Parallel website status checking method using ThreadPoolExecutor.
    """
    start_time = time.time()
    results = []

    def check_single_company(company):
        cleaned_name = WebsiteChecker.clean_company_name(company)
        urls = WebsiteChecker(timeout=timeout).generate_website_urls(company)
        
        for url in urls:
            try:
                response = requests.get(url, timeout=timeout)
                return {
                    'original_name': company,
                    'cleaned_name': cleaned_name,
                    'url': url,
                    'status_code': response.status_code,
                    'time_taken': time.time() - start_time
                }
            except requests.RequestException:
                continue

        return {
            'original_name': company,
            'cleaned_name': cleaned_name,
            'url': 'N/A',
            'status_code': 0,
            'time_taken': time.time() - start_time
        }
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(check_single_company, companies))

    total_execution_time = time.time() - start_time
    print(f"\nParallel Execution Total Time: {total_execution_time:.2f} seconds")
    return results

def analyze_performance(results: List[Dict]) -> Dict:
    """
    Analyze performance of website checking methods.
    """
    # Compute performance metrics
    status_codes = [result['status_code'] for result in results]
    response_times = [result['time_taken'] for result in results]
    
    performance_metrics = {
        'total_companies': len(results),
        'successful_checks': sum(1 for code in status_codes if code > 0),
        'success_rate': sum(1 for code in status_codes if code > 0) / len(results) * 100,
        'average_response_time': statistics.mean(response_times),
        'median_response_time': statistics.median(response_times),
        'min_response_time': min(response_times),
        'max_response_time': max(response_times)
    }
    
    return performance_metrics

def visualize_performance(metrics: Dict):
    """
    Create visualizations for performance analysis.
    """
    plt.figure(figsize=(12, 5))

    # Success Rate Pie Chart
    plt.subplot(1, 2, 1)
    success_labels = ['Successful', 'Failed']
    success_sizes = [metrics['success_rate'], 100 - metrics['success_rate']]
    plt.pie(success_sizes, labels=success_labels, autopct='%1.1f%%', colors=['green', 'red'])
    plt.title('Website Check Success Rate')

    # Response Time Histogram
    plt.subplot(1, 2, 2)
    plt.hist(metrics['response_times'], bins=20, color='skyblue', edgecolor='black')
    plt.title('Response Time Distribution')
    plt.xlabel('Response Time (seconds)')
    plt.ylabel('Frequency')
    
    plt.tight_layout()
    plt.savefig('website_check_performance.png')
    plt.close()

def main():
    # Read companies from file
    with open('companies.txt', 'r', encoding='utf-8') as f:
        companies = f.read().splitlines()
    
    # Check methods and their performance
    checking_methods = [
        ('Sequential', check_websites_sequential),
        ('Parallel', check_websites_parallel),
        ('Async', WebsiteChecker(timeout=3, max_concurrent=50).run_async)
    ]
    
    for method_name, checking_method in checking_methods:
        print(f"\n{method_name} Method Performance:")
        print("-" * 40)
        
        # Run the method
        start_time = time.time()
        results = checking_method(companies)
        total_time = time.time() - start_time
        
        # Analyze performance
        performance = analyze_performance(results)
        
        # Print detailed metrics
        print(f"Total Companies: {performance['total_companies']}")
        print(f"Successful Checks: {performance['successful_checks']}")
        print(f"Success Rate: {performance['success_rate']:.2f}%")
        print(f"Average Response Time: {performance['average_response_time']:.4f} seconds")
        print(f"Median Response Time: {performance['median_response_time']:.4f} seconds")
        print(f"Min Response Time: {performance['min_response_time']:.4f} seconds")
        print(f"Max Response Time: {performance['max_response_time']:.4f} seconds")

if __name__ == "__main__":
    main()
