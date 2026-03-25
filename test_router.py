import requests
url = "https://router.huggingface.co/hf-inference/models/Qwen/Qwen2.5-7B-Instruct"
headers = {"Authorization": "Bearer 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"}
print("Result of router URL:", requests.post(url, headers=headers, json={"inputs": "Salut"}).status_code)
