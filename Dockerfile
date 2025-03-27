FROM ollama/ollama:0.5.13-rc0 

# Install required dependencies
RUN apt-get update && apt-get install -y \
    software-properties-common \
    curl \
    gnupg \
&& add-apt-repository ppa:deadsnakes/ppa \
&& apt-get update && apt-get install -y \
    python3.12 \
    python3.12-venv \
    python3.12-dev \
    python3-pip \
&& rm -rf /var/lib/apt/lists/*

# Add NVIDIA Container Toolkit repository
RUN curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
    && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
      sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
      tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# Install NVIDIA Container Toolkit and nvidia-utils
RUN apt-get update && apt-get install -y \
    nvidia-container-toolkit \
    nvidia-utils-470  # Adjust version based on your GPU/drivers \
    && rm -rf /var/lib/apt/lists/*
 
# Install qwen2.5 latest from ollama
RUN ollama serve & sleep 5 && ollama pull nomic-embed-text

# Set working directory
WORKDIR /my_app
 
# Copy project files
COPY . /my_app
 
# Create and activate virtual environment
RUN python3.12 -m venv venv
RUN echo "source venv/bin/activate" >> ~/.bashrc

# Upgrade pip
RUN venv/bin/pip install --upgrade pip
 
# Copy requirements file and install dependencies
COPY requirements.txt /my_app/requirements.txt
RUN venv/bin/pip install --no-cache-dir -r requirements.txt
 
EXPOSE 8501

ENTRYPOINT ["/bin/bash", "-c", "ollama serve & sleep 5 && source venv/bin/activate && python -m streamlit run app.py --server.address=0.0.0.0"]

# qwen2.5 : 7B ==> 32,782 ==> 10-20 GRAM

# ollama ==> 2048 ==/ 6-8 GRAM