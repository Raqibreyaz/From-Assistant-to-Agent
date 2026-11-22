import os
import json

from openai import OpenAI
from dotenv import load_dotenv

from tools import TOOLS, run_tool
from utils.utils import log

load_dotenv()

client = OpenAI(
        base_url=os.getenv("BASE_URL"), 
        api_key=os.getenv("API_KEY")
)

messages = [
    {
        "role": "system", 
        "content": 
            "You are a helpful, humble assistant." 
            "Answer general questions (programming, science, advice) from your own knowledge."
            "Use a tool only when the user asks for the current time, weather or their city"
            "Keep answers under 100 words."
    }
]

# max no of model rounds for 1 user question
MAX_STEPS = 5

while True:
    message = input("\nYou: ").strip()

    if message.lower() in ["exit", "bye", "quit", "goodbye"]:
        break

    messages.append({"role":"user", "content":message})

    for step in range(MAX_STEPS):
        stream = client.chat.completions.create(
            model = os.getenv("MODEL"),
            messages = messages,
            tools=TOOLS,
            stream=True
        )

        content = ""
        tool_calls = []
        
        for chunk in stream:
            piece = chunk.choices[0].delta

            if piece.tool_calls:
                tool_calls.append(piece.tool_calls[0])
            if piece.content: 
                content += piece.content
                print(piece.content, end = "", flush=True)
            
        if content:
            messages.append({"role": "assistant", "content": content})
            break
        
        messages.append({'role': "assistant", 'tool_calls': tool_calls})        

        log(f"Step {step+1}: model requested {len(tool_calls)} tool call(s)")

        for tool_call in tool_calls:
            output = run_tool(tool_call=tool_call)
            
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(output)
                })
    else:
        # Ran out of steps for tool calling, Model never got final answer...
        fallback = "Sorry, I could not finish this within the step limit."
        messages.append({"role": "assistant", "content": fallback})
    