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

class FewShotsGenerator:
  def __init__(self, modelName='meta-llama/Llama-2-7b-chat-hf'):
    torch.cuda.empty_cache()
    self.hfPipe = self._build_hf_pipe(modelName=modelName)

  def _build_hf_pipe(self, modelName):
    instructPipeline = pipeline(model=modelName, torch_dtype=torch.bfloat16, trust_remote_code=True, device_map="auto", 
                              return_full_text=True, max_new_tokens=256, top_p=0.95, top_k=50)
    return HuggingFacePipeline(pipeline=instructPipeline)

  def _ask_for_shots(self,):
    template = """
    Example input -> output pair:
    {input} -> {output}

    Context:
    {context}

    Your response is to create {num_shots} OTHER similar input -> output pairs.
    You will also be given a context and all your input and output must relevant within this context.

    Response:
    """
    prompt = PromptTemplate(input_variables=[ 'input', 'output','context','num_shots'], template=template)
    self.instruction2Llm = prompt.format(input=self.exampleInput,output=self.exampleOutput,context=self.context, num_shots=self.num_shots)
    return self.hfPipe(self.instruction2Llm)

  def _extract_shots(self,):
    pattern = '([\d]+\. )(.*?)(?=(\n)|($))'
    extractedShots = re.findall(pattern, self.promptFromLlm)
    return [group[1] for group in extractedShots]
  
  def _format_draft_prompt(self,):
    if len(self.extractedShots) == 0:
      return 'Unable to derive more shots. Please revise your example'
    
    numberedShots = ['{}. {}\n'.format(i+1,shot) for i, shot in enumerate(self.extractedShots)]
    userExample = '0. {} -> {}\n'.format(self.exampleInput, self.exampleOutput)
    numberedShots.insert(0,userExample)
    numberedShots = "".join([item for item in numberedShots])
    template = f"""
    Based on the following examples:
    {numberedShots}

    Complete the relationship below:
    replace_this_with_your_input ->
    """
    return template

  def generate_few_shots(self, exampleInput, exampleOutput, context, num_shots):
    self.exampleInput = exampleInput
    self.exampleOutput = exampleOutput
    self.context = context
    self.num_shots = num_shots
    torch.cuda.empty_cache()
    self.promptFromLlm = self._ask_for_shots()
    self.extractedShots = self._extract_shots()
    return self._format_draft_prompt()

# COMMAND ----------

fewShotsGenerator = FewShotsGenerator()

# COMMAND ----------

input = '1 + 3'
output = '4'
context = 'Math'
num_shots = 5

promptTemplate = fewShotsGenerator.generate_few_shots(input,output,context,num_shots)
print(promptTemplate)

# COMMAND ----------

input = 'Banana'
output = 'Yellow'
context = 'Fruits'
num_shots = 7

promptTemplate = fewShotsGenerator.generate_few_shots(input,output,context,num_shots)
print(promptTemplate)

# COMMAND ----------

input = 'Monitor'
output = 'Office'
context = 'Furniture'
num_shots = 3

promptTemplate = fewShotsGenerator.generate_few_shots(input,output,context,num_shots)
print(promptTemplate)

# COMMAND ----------

input = 'The delivery was fast'
output = 'Positive'
context = 'Sentiment'
num_shots = 4

promptTemplate = fewShotsGenerator.generate_few_shots(input,output,context,num_shots)
print(promptTemplate)
