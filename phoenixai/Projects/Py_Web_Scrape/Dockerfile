FROM python:3.10
SHELL ["/bin/bash", "-c"]
ADD . .
RUN apt update && apt install -y graphviz
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install pipdeptree pytest graphviz coverage
RUN pipdeptree --freeze --warn silence | grep -P '^[\w0-9\-=.]+' > requirements_pipdeptree.txt
RUN pip install --no-cache-dir -r requirements_pipdeptree.txt

# Copy the startup Python script
COPY startup.py /startup.py

# Use the Python script as entry point
CMD ["python", "/startup.py"]