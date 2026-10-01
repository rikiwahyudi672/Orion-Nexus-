import os
from dotenv import load_dotenv
load_dotenv('.env', override=True)
from groq import Groq
try:
    client = Groq(api_key=os.getenv('GROQ_API_KEY'), timeout=15.0, max_retries=0)
    r = client.chat.completions.create(model='openai/gpt-oss-120b', messages=[{'role': 'user', 'content': 'test'}], max_tokens=10)
    print('✅ Groq OK')
except Exception as e:
    print(f'❌ {str(e)[:200]}')
