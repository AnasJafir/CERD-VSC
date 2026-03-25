from huggingface_hub import InferenceClient

token = "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"
models = [
    "Qwen/Qwen2.5-1.5B-Instruct",
    "Qwen/Qwen2.5-7B-Instruct",
    "google/gemma-2-2b-it",
    "meta-llama/Llama-3.2-1B-Instruct",
    "mistralai/Mistral-7B-Instruct-v0.3",
    "meta-llama/Llama-3.2-3B-Instruct"
]

for model in models:
    try:
        client = InferenceClient(model, token=token)
        res = client.text_generation("Say hi", max_new_tokens=5)
        print(f"✅ {model} WORKS!")
    except Exception as e:
        print(f"❌ {model} failed")
