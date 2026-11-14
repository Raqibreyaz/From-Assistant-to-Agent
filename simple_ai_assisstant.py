from openai import OpenAI
from dotenv import load_dotenv
from tools import TOOLS, FUNCTION_NAME_TO_FUNCTION_MAP
import os
import json

load_dotenv()

client = OpenAI(
        base_url=os.getenv("BASE_URL"), 
        api_key=os.getenv("API_KEY")
)

messages = [
    {
        "role": "system", 
        "content": "Act like a very humble agent and respond always under 20 words"
    }
]

# max no of model rounds for 1 user question
MAX_STEPS = 5

while True:
    message = input("\nYou: ").strip()

    if message.lower() in ["exit", "bye", "quit", "goodbye"]:
        break

    messages.append({"role":"user", "content":message})

    for _ in range(MAX_STEPS):
        print("feeding messages to LLM...")
        response = client.chat.completions.create(
            model = os.getenv("MODEL"),
            messages = messages,
            tools=TOOLS
        )

        msg = response.choices[0].message    
        if msg.content:
            messages.append({"role": msg.role, "content": msg.content})
            print(f"{msg.role}: {msg.content}")
            break
        
        tool_calls = msg.tool_calls
        messages.append({'role': msg.role, 'tool_calls': tool_calls})        

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)    

            print(f"invoking {function_name}()")

            try:
                function = FUNCTION_NAME_TO_FUNCTION_MAP[function_name]
                output = function(**args)
            except Exception as e:
                output = f"Error while running {function_name}: {e}"
            
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(output)
                })
    else:
        # Ran out of steps for tool calling, Model never got final answer...
        fallback = "Sorry, I could not finish this within the step limit."
        messages.append({"role": "assistant", "content": fallback})
    