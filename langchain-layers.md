mkdir -p python/lib/python3.12/site-packages
docker run -it --rm -v ${PWD}:/langchain-layer -w /langchain-layer public.ecr.aws/sam/build-python3.12:latest bash
pip install -r requirements.txt -t python/lib/python3.12/site-packages
pip install langchain pandas openpyxl -t python/lib/python3.12/site-packages
zip -r langchain-layer.zip python