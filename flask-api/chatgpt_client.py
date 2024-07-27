from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv('CHATGPT_API_KEY')

)

def call(prompt, max_tokens=150, model='gpt-4o', custom_default_role_message='You are a highly skilled AI assistant.'):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": custom_default_role_message},
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens
    )
    return response.choices[0].message.content
