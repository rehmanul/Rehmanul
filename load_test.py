import requests
import time
import concurrent.futures
import statistics
from typing import List, Dict
import json

def make_request(url: str) -> Dict:
    start_time = time.time()
    try:
        response = requests.get(url)
        end_time = time.time()
        return {
            'status_code': response.status_code,
            'response_time': end_time - start_time,
            'success': response.status_code == 200
        }
    except Exception as e:
        end_time = time.time()
        return {
            'status_code': 0,
            'response_time': end_time - start_time,
            'success': False,
            'error': str(e)
        }

def run_load_test(url: str, num_requests: int = 100, concurrent: int = 10) -> Dict:
    print(f"Starting load test: {num_requests} requests, {concurrent} concurrent")
    
    results: List[Dict] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent) as executor:
        futures = [executor.submit(make_request, url) for _ in range(num_requests)]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    
    # Calculate statistics
    response_times = [r['response_time'] for r in results]
    successful_requests = sum(1 for r in results if r['success'])
    
    stats = {
        'total_requests': num_requests,
        'successful_requests': successful_requests,
        'failed_requests': num_requests - successful_requests,
        'success_rate': (successful_requests / num_requests) * 100,
        'min_response_time': min(response_times),
        'max_response_time': max(response_times),
        'avg_response_time': statistics.mean(response_times),
        'median_response_time': statistics.median(response_times)
    }
    
    # Print results
    print("\nLoad Test Results:")
    print("=================")
    print(f"Total Requests: {stats['total_requests']}")
    print(f"Successful Requests: {stats['successful_requests']}")
    print(f"Failed Requests: {stats['failed_requests']}")
    print(f"Success Rate: {stats['success_rate']:.2f}%")
    print(f"Min Response Time: {stats['min_response_time']:.3f}s")
    print(f"Max Response Time: {stats['max_response_time']:.3f}s")
    print(f"Average Response Time: {stats['avg_response_time']:.3f}s")
    print(f"Median Response Time: {stats['median_response_time']:.3f}s")
    
    # Save results to file
    with open('load_test_results.json', 'w') as f:
        json.dump(stats, f, indent=2)
    
    return stats

if __name__ == '__main__':
    run_load_test('http://localhost', num_requests=100, concurrent=10)
