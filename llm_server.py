
from llama_cpp import Llama
from fastapi import FastAPI
from pydantic import BaseModel

import uvicorn

app = FastAPI()
#model = Llama(model_path="models/mistral-7b-instruct-v0.1.Q4_K_M.gguf")
model = Llama(model_path="models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf")


@app.get("/healthcheck")
async def healthcheck():
    response = model.create_completion('Given a sentance  - A person was disabled, and now he is walking,- was his health improved?', max_tokens=512)
    print("Result:",len(response["choices"]),'choices')
    for choice in response["choices"]:
        print(choice["text"].replace("\n"," "),"\n")
    return {"status": response}

class QueryInput(BaseModel):
    text: str

@app.post("/query")
async def query(input: QueryInput):
    try:
        print('Processing:',input.text)
        response = model.create_completion(input.text,max_tokens=512,temperature=0.5)
        print(response,response["choices"][0])
        return {"response": response}
    except Exception as e:
        return {"error": str(e)}

uvicorn.run(app, host="0.0.0.0", port=8000)
