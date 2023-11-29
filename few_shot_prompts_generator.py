# Databricks notebook source
# MAGIC %pip install -U langchain==0.0.164 transformers==4.30.0 accelerate==0.19.0 bitsandbytes huggingface_hub

# COMMAND ----------

# MAGIC %sh huggingface-cli login --token $HUGGINGFACE_TOKEN

# COMMAND ----------

import torch
import re
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, AutoModelForSeq2SeqLM
from langchain import PromptTemplate, FewShotPromptTemplate 
from langchain.llms import HuggingFacePipeline
from langchain.chains.question_answering import load_qa_chain
from langchain.memory import ConversationSummaryBufferMemory
from huggingface_hub import login

def _build_hf_pipe(modelName='databricks/dolly-v2-7b'):
  instructPipeline = pipeline(model=modelName, torch_dtype=torch.bfloat16, trust_remote_code=True, device_map="auto", 
                            return_full_text=True, max_new_tokens=256, top_p=0.95, top_k=50)
  return HuggingFacePipeline(pipeline=instructPipeline)

def _ask_for_shots(input,output,context,num_shots,hfPipe):
  torch.cuda.empty_cache()
  template = """
  Example input -> output pair:
  {input} -> {output}

  Context:
  {context}

  Your response is to create {num_shots} OTHER similar input -> output pairs.
  You will also be given a context and all your input and output must relevant within this context.

  Response:
  """
  prompt = PromptTemplate(input_variables=['context', 'input', 'output', 'num_shots'], template=template)

  return hfPipe(prompt.format(input=input,output=output,context=context, num_shots=num_shots))

def _extract_shots(promptFromLlm):
  pattern = '([\d]+\. )(.*?)(?=(\n)|($))'
  extracted_shots = re.findall(pattern, promptFromLlm)
  return [group[1] for group in extracted_shots]


def generate_few_shots(exampleInput: str, exampleOutput: str, context: str, num_shots: int):
    modelName = "meta-llama/Llama-2-7b-chat-hf"
    hfPipe = _build_hf_pipe(modelName=modelName)
    promptFromLlm = _ask_for_shots(input=exampleInput, output=exampleOutput, context=context, num_shots=num_shots, hfPipe=hfPipe)
    return _extract_shots(promptFromLlm)


# COMMAND ----------

input = '1 + 3'
output = '4'
context = 'Math'
num_shots = 5

extracted_shots = generate_few_shots(input,output,context,num_shots)
print('\nExtracted:')
for i in extracted_shots:
    print(i)

# COMMAND ----------

input = 'Banana'
output = 'Yellow'
context = 'Fruits'
num_shots = 7

extracted_shots = generate_few_shots(input,output,context,num_shots)
print('\nExtracted:')
for i in extracted_shots:
    print(i)

# COMMAND ----------

input = 'Monitor'
output = 'Office'
context = 'Furniture'
num_shots = 3

extracted_shots = generate_few_shots(input,output,context,num_shots)
print('\nExtracted:')
for i in extracted_shots:
    print(i)

# COMMAND ----------

input = 'The delivery was fast'
output = 'Positive'
context = 'Sentiment'
num_shots = 4

extracted_shots = generate_few_shots(input,output,context,num_shots)
print('\nExtracted:')
for i in extracted_shots:
    print(i)
