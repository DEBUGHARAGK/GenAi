import boto3
import json
import logging
import pandas as pd
from io import BytesIO
from langchain.prompts import PromptTemplate
from botocore.exceptions import ClientError

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize Bedrock client
client = boto3.client("bedrock-runtime", region_name="us-west-2")

class BedrockLLM:
    def __init__(self, model_id):
        self.model_id = model_id

    def generate_code(self, prompt: str) -> str:
        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 200,
            "top_k": 250,
            "stop_sequences": [],
            "temperature": 1,
            "top_p": 0.999,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        }

        try:
            # Log the payload for debugging
            logger.info("Payload: %s", payload)

            # Send the request to the Bedrock model
            response = client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(payload),
                contentType="application/json",
                accept="application/json"
            )

            # Parse the response from Bedrock
            response_body = response["body"].read()
            response_json = json.loads(response_body)
            response_text = response_json["content"][0]["text"]
            return response_text
        except (ClientError, Exception) as e:
            logger.error("Error invoking Bedrock model: %s", e)
            return "Error generating code. Please check the STT file and try again."

def lambda_handler(event, context):
    try:
        # S3 bucket and key information for input and output
        input_bucket = "genius-llm-test"
        input_key = "input/STT-sample.xlsx"
        output_bucket = "genius-llm-test"
        output_key = "output/python-etl-mapping-output-pradeep.py"

        # Initialize S3 client
        s3 = boto3.client('s3')
        
        # Download the Excel file from S3
        response = s3.get_object(Bucket=input_bucket, Key=input_key)
        file_content = response['Body'].read()

        # Read the Excel file into a DataFrame
        df = pd.read_excel(BytesIO(file_content))

        # Dynamically detect key columns in the STT structure
        source_table_col = next((col for col in df.columns if "source" in col.lower() and "table" in col.lower()), None)
        target_table_col = next((col for col in df.columns if "target" in col.lower() and "table" in col.lower()), None)
        source_column_col = next((col for col in df.columns if "source" in col.lower() and "column" in col.lower()), None)
        target_column_col = next((col for col in df.columns if "target" in col.lower() and "column" in col.lower()), None)
        transformation_logic_col = next((col for col in df.columns if "transformation" in col.lower()), None)

        # Ensure required columns are found, or log an error
        if not all([source_table_col, target_table_col, source_column_col, target_column_col, transformation_logic_col]):
            raise ValueError("One or more required columns are missing or named unexpectedly.")

        # Define a prompt template for each row's transformation
        prompt_template = PromptTemplate(
            input_variables=["source_table", "source_column", "target_table", "target_column", "transformation_logic"],
            template="Generate Python code to transform data from '{source_table}.{source_column}' to '{target_table}.{target_column}' using the following logic: {transformation_logic}"
        )

        # Initialize Bedrock LLM
        model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"
        llm = BedrockLLM(model_id=model_id)

        # Generate Python code dynamically for each row in the DataFrame
        generated_code = []
        for _, row in df.iterrows():
            prompt = prompt_template.format(
                source_table=row[source_table_col],
                source_column=row[source_column_col],
                target_table=row[target_table_col],
                target_column=row[target_column_col],
                transformation_logic=row[transformation_logic_col]
            )
            response = llm.generate_code(prompt)
            generated_code.append(response)

        # Combine the generated code into a single string
        final_code = "\n".join(generated_code)

        # Save the generated Python code to the output S3 file
        s3.put_object(Body=final_code.encode("utf-8"), Bucket=output_bucket, Key=output_key)

        # Return success message
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Code generation and upload successful"})
        }

    except Exception as e:
        # Log the error and return a failure message
        logger.error(f"An error occurred: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
