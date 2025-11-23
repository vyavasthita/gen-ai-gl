from openai import OpenAI
import os

client = OpenAI()

try:
    models = client.models.list()
    print("Your API key is valid!")
    print("Available models:")
    for m in models.data[:5]:
        print("-", m.id)
except Exception as e:
    print("Failed to validate API key:")
    print(e)

