from groq import Groq
import time
import streamlit as st

client = Groq(api_key= "GROQ_API_KEY")

def ask_llm(messages):
    system_prompt = {
        "role": "system",
        "content": "You are a business intelligence assistant answering questions about deals and work orders."
    }
    models=[
        "moonshotai/kimi-k2-instruct-0905",
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant"
    ]
    delay=1
    for model in models:
        for attempt in range(3):
            try:
                completion=client.chat.completions.create(
                    model=model,
                    messages=[system_prompt]+messages,
                    temperature=0.3,
                    max_completion_tokens=2048
                )
                return completion.choices[0].message.content

            except Exception as e:
                if "503" in str(e) or "over capacity" in str(e):
                    print(f"{model} overloaded, retrying in {delay}s")
                    time.sleep(delay)
                    delay*=2
                else:
                    raise e
    return "AI service temporarily unavailable. Please try again."