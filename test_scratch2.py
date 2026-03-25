import os
from huggingface_hub import InferenceClient

token = "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"

# Test InferenceClient using chat_completion (OpenAI compatible)
try:
    client = InferenceClient(token=token)
    response = client.chat_completion(
        model="Qwen/Qwen2.5-7B-Instruct",
        messages=[{"role": "user", "content": "Hi"}],
        max_tokens=10
    )
    print("Test Qwen OK:", response.choices[0].message.content)
except Exception as e:
    print("Test Qwen Error:", e)

try:
    client = InferenceClient(token=token)
    response = client.chat_completion(
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        messages=[{"role": "user", "content": "Hi"}],
        max_tokens=10
    )
    print("Test Mixtral OK:", response.choices[0].message.content)
except Exception as e:
    print("Test Mixtral Error:", e)
