import streamlit as st
import boto3
import json
import base64
 
# Initialize the Boto3 client for AWS Lambda
client = boto3.client(
    'lambda',
    region_name='us-west-2',  # Adjust to your region
    aws_access_key_id='',
    aws_secret_access_key=''
)
 
# Set the background image
def set_background(png_file):
    st.markdown(
        f"""
        <style>
       
        .stApp {{
            background: url(data:image/png;base64,{png_file}) no-repeat center center fixed;
            background-size: cover;
        }}
      

        </style>
        """,
        unsafe_allow_html=True
    )



 
def invoke_lambda_function(text):
    response = client.invoke(
        FunctionName='sandy',  
        InvocationType='RequestResponse',
        Payload=json.dumps({'prompt': text})
    )
    response_payload = json.load(response['Payload'])
    return response_payload
 
 
 
# Streamlit app
st.title("Serverless e-learning")

    # Load your image and convert it to base64
with open("nature-6565499_1280.jpg", "rb") as img_file:
    my_string = base64.b64encode(img_file.read()).decode()
 
 # Set the background image
set_background(my_string)


user_input = st.text_area("Enter your text here:")
 
if st.button("Submit"):
    if user_input:
        with st.spinner("Invoking request..."):
            try:
                response = invoke_lambda_function(user_input)
                st.success("Response received!")
                print(response)
                fnl=response['body']
                #print(fnl)
                #st.write("Lambda response:", response['body'])
                st.markdown(f'<div style="background-color: #333; padding: 50px; color: white;">{fnl} </div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.warning("Please enter some text to submit.")