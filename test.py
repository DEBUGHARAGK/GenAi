import json
import time
import random
import boto3
from botocore.exceptions import ClientError
# from langchain_aws import BedrockLLM
from langchain.prompts import PromptTemplate
import os
from urllib.parse import parse_qs
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from botocore.exceptions import ClientError


# from langchain_aws import BedrockEmbeddings
from langchain_community.llms import Bedrock

# Data Ingestion
import numpy as np
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFDirectoryLoader

# Vector Embedding and Vector Store
from langchain_community.vectorstores import FAISS

# LLM Models and Chains
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA