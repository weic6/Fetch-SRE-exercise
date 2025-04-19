import yaml
import time
import json
from collections import defaultdict
import aiohttp
import asyncio

# Function to load configuration from the YAML file
def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

# Function to perform health checks
async def check_health(endpoint, domain_stats, session):
    url = endpoint['url']
    method = endpoint.get('method', 'GET') # default is GET
    headers = endpoint.get('headers')
    body = endpoint.get('body') # body is a string(!!), or None
    body = json.loads(body) if body else None # convert JSON string into a Python dict

    try:
        time_start = time.time()        
        async with session.request(method, url, headers=headers, json=body, timeout=5) as response:
            time_taken = time.time() - time_start
            # print(f"response time: {time_taken:.3f} s, status code: {response.status}")
            if 200 <= response.status < 300 and time_taken <= 0.5:
                res = "UP"
            else:
                res = "DOWN"
    except asyncio.TimeoutError:
        res = "DOWN"
    
    domain = url.split("//")[-1].split("/")[0].split(":")[0] # ignore port numbers when determining domain
    domain_stats[domain]["total"] += 1
    if res == "UP":
        domain_stats[domain]["up"] += 1

# Main function to monitor endpoints
async def monitor_endpoints(file_path):
    config = load_config(file_path)
    # num_endpoints = len(config)
    domain_stats = defaultdict(lambda: {"up": 0, "total": 0})
    async with aiohttp.ClientSession() as session:
        while True:
            tasks = []
            time_start = time.time()     
            # print(f"---checking {num_endpoints} endpoints health at {time.strftime('%Y/%m/%d %H:%M:%S')}---") 
            
            for endpoint in config:
                task = asyncio.create_task(coro = check_health(endpoint, domain_stats, session))
                tasks.append(task)
            await asyncio.gather(*tasks)

            # Log cumulative availability percentages
            for domain, stats in domain_stats.items():
                availability = round(100 * stats["up"] / stats["total"])
                print(f"{domain} has {availability}% availability percentage")

            print("---")
            
            cycle_time = 15 # health check runs every 15 seconds
            time_taken = time.time() - time_start
            time_sleep = cycle_time - time_taken
            if time_sleep > 0:
                await asyncio.sleep(time_sleep)

# Entry point of the program
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python monitor.py <config_file_path>")
        sys.exit(1)

    config_file = sys.argv[1]
    try:
        asyncio.run(monitor_endpoints(config_file))
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")