# Databricks notebook source
# # # Natural Language Processing
# !pip install langchain==0.0.164
# !pip install llama-cpp-python==0.1.66
# !pip install sentence-transformers
# !pip install huggingface_hub
# !pip install auto-gptq==0.2.2
# !pip install termcolor
# !pip install loguru
# !pip install llamacpp

# COMMAND ----------

from loguru import logger
import torch
import transformers
import os
import re
from auto_gptq import AutoGPTQForCausalLM
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, AutoModelForSeq2SeqLM, LlamaForCausalLM, LlamaTokenizer, LongformerTokenizer, GenerationConfig
from langchain import PromptTemplate 
from tqdm import tqdm
from langchain.llms.huggingface_pipeline import HuggingFacePipeline
from huggingface_hub import hf_hub_download
from langchain.llms import LlamaCpp
from langchain.chains import LLMChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pandas as pd

# COMMAND ----------


class content_summarizer:
    def __init__(self):
        self.model_id = "TheBloke/Llama-2-7B-Chat-GGML"
        self.model_basename = "llama-2-7b-chat.ggmlv3.q4_0.bin"
        self.DEVICE_TYPE = "cuda" if torch.cuda.is_available() else "cpu"
        # SHOW_SOURCES = True
        self.LLM = self.load_model(device_type=self.DEVICE_TYPE, model_id=self.model_id, model_basename=self.model_basename)

    def load_model(self, device_type, model_id, model_basename=None):

        logger.info(f"Loading Model: {model_id}, on: {device_type}")
        logger.info("This action can take a few minutes!")

        if self.model_basename is not None:
            if ".ggml" in self.model_basename:
                logger.info("Using Llamacpp for GGML quantized models")
                model_path = hf_hub_download(repo_id=self.model_id, filename=self.model_basename)
                max_ctx_size = 4096
                verbose = False
                kwargs = {
                    "model_path": model_path,
                    "n_ctx": max_ctx_size,
                    "max_tokens": max_ctx_size,
                    "verbose":verbose,
                }
                # if device_type.lower() == "mps":
                #     kwargs["n_gpu_layers"] = 1000
                if device_type.lower() == "cuda":
                    # kwargs["n_gpu_layers"] = 1000
                    kwargs["n_batch"] = max_ctx_size
                return LlamaCpp(**kwargs)

            else:
                logger.info("Using AutoGPTQForCausalLM for quantized models")

                if ".safetensors" in self.model_basename:
                    # Remove the ".safetensors" ending if present
                    model_basename = self.model_basename.replace(".safetensors", "")

                tokenizer = AutoTokenizer.from_pretrained(self.model_id, use_fast=True)
                logger.info("Tokenizer loaded")

                model = AutoGPTQForCausalLM.from_quantized(
                    self.model_id,
                    model_basename=self.model_basename,
                    use_safetensors=True,
                    trust_remote_code=True,
                    device="cuda:0",
                    use_triton=False,
                    quantize_config=None,
                )
        elif (
            device_type.lower() == "cuda"
        ):  
            logger.info("Using AutoModelForCausalLM for full models")
            tokenizer = AutoTokenizer.from_pretrained(self.model_id)
            logger.info("Tokenizer loaded")

            model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                device_map="auto",
                torch_dtype=torch.float16,
                low_cpu_mem_usage=True,
                trust_remote_code=True,
                # max_memory={0: "15GB"} # Uncomment this line with you encounter CUDA out of memory errors
            )
            model.tie_weights()
        else:
            logger.info("Using LlamaTokenizer")
            tokenizer = LlamaTokenizer.from_pretrained(self.model_id)
            model = LlamaForCausalLM.from_pretrained(self.model_id)

        self.generation_config = GenerationConfig.from_pretrained(self.model_id)

        # Create a pipeline for text generation
        self.pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_length=2048,
            temperature=0,
            top_p=0.95,
            repetition_penalty=1.15,
            generation_config=self.generation_config,
        )

        local_llm = HuggingFacePipeline(pipeline=self.pipe)
        logger.info("Local LLM Loaded")

        return local_llm
    
    def generate_persona_text(self, persona):
        # Defining the template to generate summary
        template = """
        Given a persona, act as a prompt generator and return a description of the persona and the tone and style in which they would respond (i.e. formal, informal, academic, humorous, etc.). Next indicate the knowledge level of the persona (i.e. expert, beginner, etc.). Lastly, list the persona's interests and biases. 
        ----------
        Two examples provided are as follows:

        Persona --> Steve Jobs
        Output --> You are Steve Jobs, the co-founder of Apple Inc. You are known for your innovative and visionary approach to technology. You have a charismatic and persuasive speaking style, always striving for simplicity and elegance. Your persona is marked by a blend of formality and a touch of showmanship. You are an expert in technology and design. You are passionate about user experience and design and have a bias towards minimalist and sleek product designs.
        
        Persona --> Software engineer
        Output --> You are a skilled and dedicated software engineer with a knack for problem-solving and coding. You communicate with clarity and conciseness, using technical terms when necessary but making an effort to explain concepts in a straightforward manner. You are an expert in software engineering and are passionate about clean code, efficient algorithms, and fostering a collaborative work environment. You are biased toward well-documented and maintainable code.

        Persona --> Bill Nye
        Output --> You are Bill Nye, a beloved science communicator. You are known for your enthusiasm and ability to make complex scientific concepts accessible to a broad audience. Your speaking style is energetic, and you often employs humor and real-world examples to convey scientific principles. You are at an intermediate level in various scientific disciplines. You are passionate about promoting scientific literacy and critical thinking. You are biased towards evidence-based thinking and the scientific method.
        ---------

        Your response must only have one paragraph, be a persona prompt and contain more than 20 words. It must not include any of the examples given above.
        Persona --> {persona}
        Output -->
        """
        prompt = PromptTemplate(template=template, input_variables=["persona"])
        self.llm_chain = LLMChain(prompt=prompt, llm=self.LLM)

        persona_description = self.llm_chain.run(persona)
        return persona_description.strip()
    
    def generate_summary_prompt(self, persona, word_limit, focus):
        base_template = f'Write a concise summary of the text, return your response within {word_limit} words but only focus on {focus}.\n\n ```<Paste text to summarize here>```\n SUMMARY:'
        if persona != None:
            persona_description = self.generate_persona_text(persona)
            return f'{persona_description}\n' + base_template
        else:
            return base_template

# COMMAND ----------

content_summarizer = content_summarizer()

# COMMAND ----------

persona = dbutils.widgets.get("persona")
word_limit = dbutils.widgets.get("word_limit")
focus = dbutils.widgets.get("focus")

promptTemplate = content_summarizer.generate_summary_prompt(persona, word_limit, focus)
dbutils.notebook.exit(promptTemplate)

# COMMAND ----------

content_summarizer.generate_persona_text("Painter")

# COMMAND ----------

input = "Baldur's Gate 3 is a role-playing video game developed and published by Larian Studios. It is the third main installment in the Baldur's Gate series, based on the tabletop role-playing system of Dungeons & Dragons. A partial version of the game was released in early access format for macOS and Windows 6 October 2020. The game remained in early access until its full release on Windows on 3 August 2023. The PlayStation 5 version was released on 6 September 2023,[a] with the macOS version released shortly thereafter on 22 September. The Xbox Series X/S version is planned for release in late 2023. The game received critical acclaim, with praise for its gameplay, narrative, and production quality. It won multiple awards including the Golden Joystick Award for Game of the Year."

promptTemplate = content_summarizer.generate_summary_prompt('Elon Musk', 5, 'release dates')
print(promptTemplate)
