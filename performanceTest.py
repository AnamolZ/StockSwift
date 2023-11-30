import time
import requests

def test_performance():
    url = "http://localhost:8000/"
    num_requests = 10

    start_time = time.time()

    for _ in range(num_requests):
        response = requests.get(url)
        print(_)

    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"\nNumber of requests: {num_requests}")
    print(f"Total elapsed time: {elapsed_time:.2f} seconds")
    print(f"Average time per request: {elapsed_time / num_requests:.2f} seconds")

if __name__ == "__main__":
    test_performance()

