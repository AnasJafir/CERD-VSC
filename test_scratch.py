import requests
from huggingface_hub import InferenceClient

token = "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"

# Test 1: Direct requests.post on gpt2
url = "https://api-inference.huggingface.co/models/gpt2"
headers = {"Authorization": f"Bearer {token}"}
print("Test 1 requests on gpt2:", requests.post(url, headers=headers, json={"inputs": "Hi"}).status_code)

# Test 2: InferenceClient
try:
    client = InferenceClient("HuggingFaceH4/zephyr-7b-beta", token=token)
    print("Test 2 Zephyr InferenceClient:", client.text_generation("Hi there!", max_new_tokens=10)[:30])
except Exception as e:
    print("Test 2 error:", e)

try:
    client2 = InferenceClient("mistralai/Mistral-Nemo-Instruct-2407", token=token)
    print("Test 3 Nemo InferenceClient:", client2.text_generation("Hi there!", max_new_tokens=10)[:30])
except Exception as e:
    print("Test 3 error:", e)
