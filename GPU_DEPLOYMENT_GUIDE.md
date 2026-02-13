# GPU Deployment Guide - HPC and Local Machines

## Overview

This guide provides instructions for deploying Vecta AI on systems with GPU acceleration, including HPC clusters and local machines with NVIDIA GPUs.

---

## Hardware Requirements

### Minimum GPU Specifications
- **VRAM**: 16GB+ (for Llama3-Med42-8B model)
- **CUDA**: 11.7 or higher
- **GPU**: NVIDIA RTX 3090, A100, V100, or equivalent
- **System RAM**: 32GB+
- **Storage**: 50GB+ free space

### Recommended GPU Specifications
- **VRAM**: 24GB+ (A100, RTX 4090)
- **CUDA**: 12.0+
- **Multi-GPU**: Optional for faster inference
- **System RAM**: 64GB+

---

## Deployment Options

### Option 1: Local Machine with GPU

For researchers with local workstations equipped with NVIDIA GPUs.

### Option 2: HPC Cluster (SLURM)

For institutional HPC environments with job scheduling.

### Option 3: Docker with GPU

For containerized deployments with GPU passthrough.

### Option 4: Cloud GPU Instances

For AWS, Azure, or GCP with GPU instances.

---

## Option 1: Local Machine with GPU

### Prerequisites

```bash
# Check GPU availability
nvidia-smi

# Output should show your GPU(s):
# +-----------------------------------------------------------------------------+
# | NVIDIA-SMI 535.54.03    Driver Version: 535.54.03    CUDA Version: 12.2  |
# +-----------------------------------------------------------------------------+
```

### Installation Steps

#### Step 1: Install CUDA Toolkit

**For Ubuntu/Debian:**
```bash
# Add NVIDIA package repository
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt-get update

# Install CUDA
sudo apt-get install cuda-toolkit-12-2
```

**For RHEL/CentOS:**
```bash
# Add NVIDIA repository
sudo dnf config-manager --add-repo \
    https://developer.download.nvidia.com/compute/cuda/repos/rhel9/x86_64/cuda-rhel9.repo

# Install CUDA
sudo dnf install cuda-toolkit-12-2
```

#### Step 2: Install PyTorch with GPU Support

```bash
# Clone repository
git clone https://github.com/phindagijimana/vecta.git
cd vecta

# Install PyTorch with CUDA 12.1
pip3 install --user torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Verify GPU is available
python3 -c "import torch; print(f'GPU Available: {torch.cuda.is_available()}'); print(f'GPU Count: {torch.cuda.device_count()}')"
```

Expected output:
```
GPU Available: True
GPU Count: 1
```

#### Step 3: Install Dependencies

```bash
# Install required packages
pip3 install --user -r requirements.txt

# Install additional GPU-optimized packages
pip3 install --user accelerate bitsandbytes
```

#### Step 4: Configure GPU Settings

Create `config.yaml`:
```yaml
# GPU Configuration
device: cuda
gpu_id: 0  # Use first GPU (0-indexed)

# Model Settings
model_name: m42-health/Llama3-Med42-8B
load_in_8bit: false  # Set true for 8-bit quantization (less VRAM)
load_in_4bit: false  # Set true for 4-bit quantization (minimal VRAM)

# Inference Settings
max_length: 2048
temperature: 0.7
top_p: 0.9
batch_size: 1

# Memory Optimization
torch_dtype: float16  # Use half precision
device_map: auto      # Automatic device mapping
```

#### Step 5: Launch Application

```bash
# Start with GPU
./vecta start

# Or specify GPU ID
CUDA_VISIBLE_DEVICES=0 ./vecta start

# Monitor GPU usage
watch -n 1 nvidia-smi
```

---

## Option 2: HPC Cluster Deployment (SLURM)

### For Large-Scale Processing

#### Step 1: Load Modules

```bash
# Load required modules (adjust for your HPC)
module load cuda/12.2
module load python/3.9
module load gcc/11.2
```

#### Step 2: Create Job Script

Create `vecta_job.slurm`:
```bash
#!/bin/bash
#SBATCH --job-name=vecta-ai
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1              # Request 1 GPU
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=24:00:00
#SBATCH --output=logs/vecta_%j.out
#SBATCH --error=logs/vecta_%j.err

# Load modules
module load cuda/12.2
module load python/3.9

# Set environment
export CUDA_VISIBLE_DEVICES=$SLURM_JOB_GPUS
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

# Activate environment (if using virtualenv)
# source venv/bin/activate

# Navigate to project
cd $SLURM_SUBMIT_DIR

# Start service
python3 app.py --host 0.0.0.0 --port 8085

# Keep job alive
wait
```

#### Step 3: Submit Job

```bash
# Create logs directory
mkdir -p logs

# Submit job
sbatch vecta_job.slurm

# Check job status
squeue -u $USER

# View output
tail -f logs/vecta_*.out
```

#### Step 4: Interactive Session (for testing)

```bash
# Request interactive GPU session
salloc --partition=gpu --gres=gpu:1 --mem=64G --time=02:00:00

# Once allocated, load modules and run
module load cuda/12.2 python/3.9
cd vecta
python3 app.py
```

#### Step 5: Access from Login Node

```bash
# From login node, forward port
ssh -L 8085:compute-node:8085 username@login-node

# Access from local browser
http://localhost:8085
```

---

## Option 3: Docker with GPU Support

### For Reproducible Deployments

#### Step 1: Install NVIDIA Container Toolkit

```bash
# Add NVIDIA container repository
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

# Install nvidia-container-toolkit
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

#### Step 2: Create Dockerfile

Create `Dockerfile.gpu`:
```dockerfile
FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

# Set environment
ENV DEBIAN_FRONTEND=noninteractive
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=$CUDA_HOME/bin:$PATH
ENV LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH

# Install Python and dependencies
RUN apt-get update && apt-get install -y \
    python3.9 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy application
COPY . /app

# Install Python packages
RUN pip3 install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8085

# Start application
CMD ["python3", "app.py"]
```

#### Step 3: Build and Run

```bash
# Build image
docker build -f Dockerfile.gpu -t vecta-ai:gpu .

# Run with GPU
docker run --gpus all -p 8085:8085 vecta-ai:gpu

# Or specify GPU device
docker run --gpus '"device=0"' -p 8085:8085 vecta-ai:gpu

# Run in background
docker run -d --gpus all -p 8085:8085 --name vecta vecta-ai:gpu

# View logs
docker logs -f vecta
```

#### Step 4: Docker Compose (with GPU)

Create `docker-compose.gpu.yml`:
```yaml
version: '3.8'

services:
  vecta-ai:
    build:
      context: .
      dockerfile: Dockerfile.gpu
    ports:
      - "8085:8085"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    environment:
      - CUDA_VISIBLE_DEVICES=0
    restart: unless-stopped
```

Launch:
```bash
docker-compose -f docker-compose.gpu.yml up -d
```

---

## Option 4: Cloud GPU Instances

### AWS (using EC2 with GPU)

#### Step 1: Launch GPU Instance

```bash
# Choose instance type
# - g4dn.xlarge: T4 GPU, 16GB VRAM ($0.526/hr)
# - g5.xlarge: A10G GPU, 24GB VRAM ($1.006/hr)
# - p3.2xlarge: V100 GPU, 16GB VRAM ($3.06/hr)
# - p4d.24xlarge: A100 GPU, 40GB VRAM ($32.77/hr)

# Launch via AWS CLI
aws ec2 run-instances \
    --image-id ami-0c55b159cbfafe1f0 \
    --instance-type g4dn.xlarge \
    --key-name your-key \
    --security-groups vecta-sg
```

#### Step 2: Setup Instance

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@instance-ip

# Install NVIDIA drivers
sudo apt-get update
sudo apt-get install -y nvidia-driver-535

# Install Docker with GPU support
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt-get install -y nvidia-container-toolkit

# Clone and run
git clone https://github.com/phindagijimana/vecta.git
cd vecta
./vecta start
```

### Azure (using NC-series VMs)

```bash
# Create resource group
az group create --name vecta-rg --location eastus

# Create VM with GPU
az vm create \
  --resource-group vecta-rg \
  --name vecta-vm \
  --image UbuntuLTS \
  --size Standard_NC6s_v3 \
  --admin-username azureuser \
  --generate-ssh-keys

# Install NVIDIA drivers
ssh azureuser@vm-ip
sudo apt-get update
sudo ubuntu-drivers autoinstall
sudo reboot
```

### GCP (using Compute Engine with GPU)

```bash
# Create instance with GPU
gcloud compute instances create vecta-instance \
  --zone=us-central1-a \
  --machine-type=n1-standard-8 \
  --accelerator=type=nvidia-tesla-t4,count=1 \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --maintenance-policy=TERMINATE \
  --metadata=install-nvidia-driver=True
```

---

## Performance Optimization

### 1. Model Quantization (Reduce VRAM)

**8-bit Quantization** (halves VRAM usage):
```python
# In app.py, update model loading:
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    load_in_8bit=True,
    device_map="auto",
    torch_dtype=torch.float16
)
```

**4-bit Quantization** (minimal VRAM):
```python
from transformers import BitsAndBytesConfig

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16
)

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=quantization_config,
    device_map="auto"
)
```

### 2. Batch Processing

```python
# Process multiple cases at once
batch_size = 4
texts = [text1, text2, text3, text4]
results = model.generate(texts, batch_size=batch_size)
```

### 3. Flash Attention (faster inference)

```bash
pip3 install flash-attn --no-build-isolation

# Use in model loading:
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    attn_implementation="flash_attention_2",
    device_map="auto"
)
```

### 4. Multi-GPU Support

```python
# Automatic device placement
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto"  # Distributes across available GPUs
)

# Or manual placement
device_map = {
    "model.embed_tokens": 0,
    "model.layers.0-15": 0,
    "model.layers.16-31": 1,
    "lm_head": 1
}
```

---

## Monitoring & Troubleshooting

### GPU Monitoring

```bash
# Real-time GPU usage
watch -n 1 nvidia-smi

# Detailed GPU info
nvidia-smi -l 1

# GPU utilization log
nvidia-smi --query-gpu=timestamp,name,utilization.gpu,utilization.memory,memory.used,memory.total --format=csv -l 1 > gpu_usage.log
```

### Memory Issues

**Out of Memory (OOM) Error:**
```bash
# Reduce batch size
# Enable gradient checkpointing
# Use quantization (8-bit or 4-bit)
# Reduce max sequence length
```

**Solution**:
```python
# In app.py, add memory optimization:
torch.cuda.empty_cache()  # Clear cache between inferences

# Enable memory-efficient attention
model.config.use_memory_efficient_attention = True
```

### Performance Benchmarking

```bash
# Create benchmark script
python3 << 'EOF'
import torch
import time
from transformers import AutoTokenizer, AutoModelForCausalLM

# Load model
model_name = "m42-health/Llama3-Med42-8B"
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Benchmark
text = "Patient with recurrent seizures..."
inputs = tokenizer(text, return_tensors="pt").to("cuda")

# Warm-up
_ = model.generate(**inputs, max_length=100)

# Measure
start = time.time()
for _ in range(10):
    output = model.generate(**inputs, max_length=500)
end = time.time()

print(f"Average time per generation: {(end-start)/10:.2f}s")
print(f"GPU Memory Used: {torch.cuda.max_memory_allocated()/1e9:.2f} GB")
EOF
```

---

## Cost Comparison

### Local GPU (One-time)
| Component | Cost |
|-----------|------|
| RTX 4090 | $1,599 |
| Power (500W @ $0.12/kWh, 24/7, 1 year) | $526 |
| **Total Year 1** | **$2,125** |

### Cloud GPU (Pay-as-you-go)
| Provider | Instance | GPU | $/hour | $/month (24/7) |
|----------|----------|-----|--------|----------------|
| AWS | g4dn.xlarge | T4 | $0.526 | $380 |
| AWS | g5.xlarge | A10G | $1.006 | $727 |
| Azure | NC6s_v3 | V100 | $1.03 | $744 |
| GCP | n1-gpu-t4 | T4 | $0.48 | $347 |

**Break-even**: Local GPU pays for itself in ~3 months of 24/7 use.

---

## Security Considerations

### For HPC/Shared Systems
- Use private virtual environments
- Don't expose ports publicly
- Use SSH tunneling for access
- Encrypt sensitive data at rest
- Follow institutional policies

### For Cloud Deployments
- Use security groups/firewall rules
- Enable HTTPS with SSL certificates
- Implement authentication
- Use private VPCs
- Regular security updates

---

## Quick Start Commands

### Local GPU
```bash
git clone https://github.com/phindagijimana/vecta.git
cd vecta
pip3 install --user torch --index-url https://download.pytorch.org/whl/cu121
pip3 install --user -r requirements.txt
./vecta start
```

### HPC (SLURM)
```bash
sbatch vecta_job.slurm
squeue -u $USER
```

### Docker GPU
```bash
docker run --gpus all -p 8085:8085 vecta-ai:gpu
```

---

## Support & Resources

### Documentation
- PyTorch GPU: https://pytorch.org/get-started/locally/
- CUDA Toolkit: https://developer.nvidia.com/cuda-downloads
- HuggingFace Accelerate: https://huggingface.co/docs/accelerate

### Troubleshooting
- CUDA version mismatch: Reinstall PyTorch with matching CUDA
- OOM errors: Use quantization or reduce batch size
- Slow inference: Check GPU utilization, enable Flash Attention

### Getting Help
- GitHub Issues: https://github.com/phindagijimana/vecta/issues
- Check logs: `./vecta logs`
- GPU diagnostics: `nvidia-smi`

---

**Deployment Guide Version**: 1.0  
**Last Updated**: 2026-02-13  
**Status**: Production Ready
