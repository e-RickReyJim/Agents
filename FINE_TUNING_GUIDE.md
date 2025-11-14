# Fine-Tuning Guide: Hybrid Approach (Colab + Local Ollama)

**Goal**: Train Phi-3 Mini on Colab with free GPU, then use it locally with Ollama

**Your Hardware**: i5 8th Gen, 16GB RAM, No GPU  
**Training**: Google Colab (Free T4 GPU)  
**Inference**: Local with Ollama  
**Timeline**: 2-4 hours total

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Phase 1: Setup Local Ollama](#phase-1-setup-local-ollama)
3. [Phase 2: Test Baseline Phi-3 Mini](#phase-2-test-baseline-phi-3-mini)
4. [Phase 3: Prepare Training Data](#phase-3-prepare-training-data)
5. [Phase 4: Fine-Tune on Google Colab](#phase-4-fine-tune-on-google-colab)
6. [Phase 5: Export and Use Locally](#phase-5-export-and-use-locally)
7. [Phase 6: Integrate with Paper Writer](#phase-6-integrate-with-paper-writer)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### What You'll Need

✅ **Local (Windows):**
- Ollama installed
- 16GB RAM (you have this ✓)
- 10GB free disk space
- Python 3.11+ with virtual environment

✅ **Cloud (Colab):**
- Google account (free)
- Google Drive (5GB+ free space)
- Stable internet connection

✅ **Knowledge:**
- Basic Python
- Basic command line
- Understanding of your paper writer architecture

---

## Phase 1: Setup Local Ollama

### Step 1.1: Install Ollama

**Option A: Manual Download (Recommended - Most Reliable)**
1. Visit: https://ollama.com/download/windows
2. Download `OllamaSetup.exe` (latest version)
3. Run installer (right-click → Run as Administrator)
4. Follow installation wizard
5. Restart PowerShell after installation

**Option B: Using winget**
```powershell
# If winget is working on your system:
# Open PowerShell as Administrator
winget install Ollama.Ollama

# Restart PowerShell after installation
```

**Option B1: Fix winget if needed (common issue)**
```powershell
# Reset winget source
winget source reset --force

# Or update winget source
winget source update

# Then try installing
winget install Ollama.Ollama
```

**Option C: Using Chocolatey (if installed)**
```powershell
# If you have Chocolatey package manager
choco install ollama
```

### Step 1.2: Verify Installation

```powershell
# Check Ollama is installed
ollama --version

# Expected output: ollama version is 0.x.x
```

### Step 1.3: Start Ollama Service

```powershell
# Ollama on Windows runs on-demand (no Windows service needed)
# It starts automatically when you use any ollama command

# Test if Ollama is working:
ollama list

# Expected output (empty list if no models yet):
# NAME    ID    SIZE

# Or you might see:
# Error: could not connect to ollama app, is it running?
# If you see this error, start Ollama manually (see below)
```

**If you get "could not connect" error:**

```powershell
# Option 1: Start Ollama from Start Menu
# Press Windows key, type "Ollama", click the Ollama app

# Option 2: Start from command line
Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden

# Wait 5 seconds for service to start
Start-Sleep -Seconds 5

# Test again
ollama list
```

**Note**: After first install, you may need to restart your computer or start Ollama manually once. After that, it starts automatically.

### Step 1.4: Pull Baseline Phi-3 Mini

```powershell
# Pull the 3.8B parameter model (Q4_K_M quantization)
ollama pull phi3:mini

# This will download ~2.3GB
# Wait 5-10 minutes depending on your internet speed
```

**What just happened?**
- Downloaded Phi-3 Mini 3.8B model
- Quantized to 4-bit (Q4_K_M) for efficiency
- Stored in: `C:\Users\YourName\.ollama\models`

---

## Phase 2: Test Baseline Phi-3 Mini

### Step 2.1: Interactive Test

```powershell
# Start interactive chat
ollama run phi3:mini

# Try these prompts:
>>> Write an abstract for a paper on machine learning

>>> Explain chronic kidney disease in academic style

>>> Format this citation: Smith et al, 2023, Nature

# Exit with: /bye
```

### Step 2.2: Benchmark Speed

```powershell
# Time a generation (from PowerShell)
Measure-Command {
    ollama run phi3:mini "Write a 100-word introduction to AI" --verbose
}

# Note the tokens/second
# Expected on i5 8th gen: 2-5 tokens/sec
```

### Step 2.3: Python API Test

```powershell
# In your project directory
cd C:\GIT\Agents
.venv\Scripts\Activate.ps1

# Install LangChain Ollama support
pip install langchain-community
```

**Create test file: `test_ollama.py`**
```python
"""Test Ollama integration"""
from langchain_community.llms import Ollama

# Initialize Ollama
llm = Ollama(
    model="phi3:mini",
    base_url="http://localhost:11434"
)

# Test generation
prompt = "Write a one-sentence abstract about AI in healthcare."
response = llm.invoke(prompt)

print(f"Response: {response}")
print(f"✅ Ollama working!")
```

**Run test:**
```powershell
python test_ollama.py
```

**Expected output:**
```
Response: Artificial intelligence is revolutionizing healthcare by...
✅ Ollama working!
```

---

## Phase 3: Prepare Training Data

### Step 3.1: Understand What to Fine-Tune On

**Good training data for scientific papers:**
- ✅ Domain-specific scientific papers (your field)
- ✅ Paper structure examples (abstract, intro, methods)
- ✅ Citation formatting examples
- ✅ Academic writing style samples

**Size recommendations:**
- Minimum: 100 examples (~50MB)
- Recommended: 500-1000 examples (~100-200MB)
- Maximum (free Colab): 5000 examples (~1GB)

### Step 3.2: Data Format

**For instruction fine-tuning, use this format:**

```json
[
  {
    "instruction": "Write an abstract for a paper on machine learning in healthcare",
    "input": "Topic: Predicting chronic kidney disease using neural networks",
    "output": "This study presents a novel approach to predicting chronic kidney disease (CKD) using deep neural networks. We analyze environmental and clinical variables to develop a predictive model with 94% accuracy. Our findings suggest that AI-based early detection can significantly improve patient outcomes."
  },
  {
    "instruction": "Format this citation in IEEE style",
    "input": "Authors: John Smith, Jane Doe. Title: Deep Learning for Medical Diagnosis. Journal: Nature Medicine. Year: 2023. Volume: 29. Pages: 123-145.",
    "output": "[1] J. Smith and J. Doe, \"Deep Learning for Medical Diagnosis,\" Nature Medicine, vol. 29, pp. 123-145, 2023."
  }
]
```

### Step 3.3: Create Training Dataset

**Option A: Use Your Generated Papers**

```powershell
# In your project directory
python create_training_data.py
```

**Create: `create_training_data.py`**
```python
"""Extract training data from generated papers"""
import json
import os
from pathlib import Path

# Your existing papers
papers_dir = Path("./outputs/papers")
papers = list(papers_dir.glob("*.md"))

training_data = []

for paper in papers:
    with open(paper, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract sections (simple split by ##)
    sections = content.split('\n## ')
    
    for section in sections:
        if len(section) > 100:  # Skip very short sections
            lines = section.split('\n', 1)
            if len(lines) == 2:
                title, body = lines
                
                training_data.append({
                    "instruction": f"Write a scientific paper section on {title}",
                    "input": "",
                    "output": body.strip()[:1000]  # Limit length
                })

# Save to JSON
output_file = Path("./data/training_data.json")
output_file.parent.mkdir(exist_ok=True)

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(training_data[:1000], f, indent=2)  # Max 1000 examples

print(f"✅ Created {len(training_data[:1000])} training examples")
print(f"📁 Saved to: {output_file}")
```

**Option B: Use Public Datasets**

Popular scientific paper datasets:
- **arXiv Dataset**: 2M+ papers (https://www.kaggle.com/datasets/Cornell-University/arxiv)
- **PubMed Central**: Medical papers (https://www.ncbi.nlm.nih.gov/pmc/)
- **Semantic Scholar**: Cross-domain (https://www.semanticscholar.org/product/api)

**Download subset (example for arXiv):**
```python
# Use arXiv API to get papers in your domain
import requests
import json

def fetch_arxiv_papers(category='cs.AI', max_results=100):
    """Fetch papers from arXiv"""
    base_url = 'http://export.arxiv.org/api/query'
    
    params = {
        'search_query': f'cat:{category}',
        'start': 0,
        'max_results': max_results,
        'sortBy': 'relevance',
        'sortOrder': 'descending'
    }
    
    response = requests.get(base_url, params=params)
    # Parse XML response and extract abstracts
    # ... (implement XML parsing)
    
    return papers

# Fetch and save
papers = fetch_arxiv_papers('cs.AI', 500)
# Convert to training format...
```

### Step 3.4: Upload to Google Drive

**Prepare your data:**
```powershell
# Create a folder for Colab
mkdir colab_finetuning
cp data/training_data.json colab_finetuning/

# Manual upload to Google Drive:
# 1. Go to drive.google.com
# 2. Create folder: "Phi3_FineTuning"
# 3. Upload: training_data.json
```

---

## Phase 4: Fine-Tune on Google Colab

### Step 4.1: Open Google Colab

1. Go to: https://colab.research.google.com/
2. Click: **File → New Notebook**
3. Rename: `Phi3_FineTuning.ipynb`
4. **Important**: Runtime → Change runtime type → T4 GPU

### Step 4.2: Mount Google Drive

**Cell 1: Setup**
```python
# Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

# Navigate to your data
import os
os.chdir('/content/drive/MyDrive/Phi3_FineTuning')

# Verify data exists
!ls -lh training_data.json
```

### Step 4.3: Install Dependencies

**Cell 2: Install Libraries**
```python
# Install Unsloth for efficient fine-tuning
!pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
!pip install xformers trl peft accelerate bitsandbytes

# Verify GPU
import torch
print(f"GPU Available: {torch.cuda.is_available()}")
print(f"GPU Name: {torch.cuda.get_device_name(0)}")
```

**⚠️ Wait for installation to complete (~2-3 minutes) before continuing!**

---

### Step 4.4: Load Base Model

**Cell 3: Load Phi-3 Mini**

⚠️ **IMPORTANT**: Run this cell BEFORE Cell 4! This defines `FastLanguageModel`.

```python
from unsloth import FastLanguageModel
import torch

# Configuration
max_seq_length = 2048  # Adjust based on your data
dtype = None  # Auto-detect
load_in_4bit = True  # Use 4-bit quantization

# Load model (this takes ~2-3 minutes)
print("⏳ Loading Phi-3 Mini model...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/Phi-3-mini-4k-instruct",
    max_seq_length = max_seq_length,
    dtype = dtype,
    load_in_4bit = load_in_4bit,
)

print("✅ Model loaded!")
print(f"Model size: {sum(p.numel() for p in model.parameters()):,} parameters")
```

**Expected output:**
```
🦥 Unsloth: Will patch your computer to enable 2x faster free finetuning.
==((====))==  Unsloth 2024.11: Fast Mistral patching. Transformers = 4.45.2.
   \\   /|    GPU: Tesla T4. Max memory: 14.748 GB. Platform = Linux.
O^O/ \_/ \    Pytorch: 2.5.1+cu121. CUDA = 7.5. CUDA Toolkit = 12.1.
\        /    Bfloat16 = TRUE. FA [Xformers = 0.0.28.post2. FA2 = False]
 "-____-"     Free Apache license: http://github.com/unslothai/unsloth

⏳ Loading Phi-3 Mini model...
✅ Model loaded!
Model size: 3,821,079,552 parameters
```

**⚠️ This is normal!** The "🦥 Unsloth: Will patch..." message appears first, then the model loads.

**Wait for the full cell to complete** - it takes 2-3 minutes total.

---

### Step 4.5: Configure LoRA

**Cell 4: Setup LoRA Adapters**

⚠️ **PREREQUISITE**: Cell 3 must be completed first!
```python
# Add LoRA adapters (parameter-efficient fine-tuning)
model = FastLanguageModel.get_peft_model(
    model,
    r = 16,  # LoRA rank (higher = more parameters, better quality)
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                      "gate_proj", "up_proj", "down_proj"],
    lora_alpha = 16,
    lora_dropout = 0.05,
    bias = "none",
    use_gradient_checkpointing = "unsloth",  # Memory efficient
    random_state = 3407,
)

print("✅ LoRA configured!")
print(f"Trainable parameters: {sum(p.numel() for p in model.parameters() if p.requires_grad):,}")
```

### Step 4.6: Load Training Data

**Cell 5: Prepare Dataset**
```python
import json
from datasets import Dataset

# Load your data
with open('training_data.json', 'r') as f:
    data = json.load(f)

# Convert to Hugging Face dataset
dataset = Dataset.from_list(data)

# Format for instruction fine-tuning
alpaca_prompt = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{}

### Input:
{}

### Response:
{}"""

def format_prompts(examples):
    instructions = examples["instruction"]
    inputs = examples["input"]
    outputs = examples["output"]
    
    texts = []
    for instruction, input, output in zip(instructions, inputs, outputs):
        text = alpaca_prompt.format(instruction, input, output)
        texts.append(text)
    
    return {"text": texts}

# Apply formatting
dataset = dataset.map(format_prompts, batched=True)

print(f"✅ Dataset prepared: {len(dataset)} examples")
```

### Step 4.7: Fine-Tune

**Cell 6: Training**
```python
from trl import SFTTrainer
from transformers import TrainingArguments

# Training configuration
trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    dataset_text_field = "text",
    max_seq_length = max_seq_length,
    dataset_num_proc = 2,
    packing = False,  # Set True for shorter sequences
    args = TrainingArguments(
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,
        warmup_steps = 5,
        max_steps = 100,  # Adjust based on dataset size
        learning_rate = 2e-4,
        fp16 = not torch.cuda.is_bf16_supported(),
        bf16 = torch.cuda.is_bf16_supported(),
        logging_steps = 10,
        optim = "adamw_8bit",
        weight_decay = 0.01,
        lr_scheduler_type = "linear",
        seed = 3407,
        output_dir = "outputs",
        save_steps = 50,
    ),
)

# Start training
print("🚀 Starting fine-tuning...")
trainer_stats = trainer.train()

print("✅ Fine-tuning complete!")
print(f"Training time: {trainer_stats.metrics['train_runtime']:.2f} seconds")
```

**Expected output:**
```
🚀 Starting fine-tuning...
Step    Loss
10      2.345
20      1.892
...
100     0.456
✅ Fine-tuning complete!
Training time: 1234.56 seconds (~20-30 mins on T4)
```

### Step 4.8: Test Fine-Tuned Model

**Cell 7: Inference Test**
```python
# Enable fast inference
FastLanguageModel.for_inference(model)

# Test prompt
prompt = alpaca_prompt.format(
    "Write an abstract for a scientific paper",
    "Topic: Machine learning for chronic kidney disease prediction",
    ""  # Leave output empty for generation
)

inputs = tokenizer([prompt], return_tensors="pt").to("cuda")

# Generate
outputs = model.generate(
    **inputs,
    max_new_tokens = 256,
    temperature = 0.7,
    do_sample = True
)

# Decode
generated_text = tokenizer.batch_decode(outputs)[0]
print(generated_text)
```

### Step 4.9: Save Fine-Tuned Model

**Cell 8: Export Model**

**Option A: Save LoRA Adapters (Recommended - Small)**
```python
# Save only LoRA adapters (~50-100MB)
model.save_pretrained("phi3_finetuned_lora")
tokenizer.save_pretrained("phi3_finetuned_lora")

# Zip for download
!zip -r phi3_finetuned_lora.zip phi3_finetuned_lora

# Copy to Google Drive
!cp phi3_finetuned_lora.zip /content/drive/MyDrive/Phi3_FineTuning/

print("✅ LoRA adapters saved to Google Drive")
```

**Option B: Save Merged Model (Larger - Full Model)**
```python
# Merge LoRA with base model
model.save_pretrained_merged(
    "phi3_finetuned_merged",
    tokenizer,
    save_method = "merged_16bit"  # or "merged_4bit"
)

# Export to GGUF for Ollama
model.save_pretrained_gguf(
    "phi3_finetuned_gguf",
    tokenizer,
    quantization_method = "q4_k_m"  # Same as Ollama default
)

# Copy to Drive
!cp -r phi3_finetuned_gguf /content/drive/MyDrive/Phi3_FineTuning/

print("✅ GGUF model saved to Google Drive")
```

---

## Phase 5: Export and Use Locally

### Step 5.1: Download from Google Drive

**On your local machine:**

1. Go to: https://drive.google.com/
2. Navigate to: `Phi3_FineTuning/`
3. Download: `phi3_finetuned_lora.zip` or `phi3_finetuned_gguf/`
4. Save to: `C:\GIT\Agents\models\`

**Via PowerShell:**
```powershell
# Create models directory
cd C:\GIT\Agents
mkdir models

# Manual download from Drive, then extract:
Expand-Archive -Path "Downloads\phi3_finetuned_lora.zip" -DestinationPath "models\"
```

### Step 5.2: Import to Ollama

**Option A: Use GGUF Model Directly**

If you saved as GGUF, create a Modelfile:

**Create: `models/Modelfile`**
```
FROM ./phi3_finetuned_gguf/model.gguf

PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER stop "<|endoftext|>"
PARAMETER stop "<|im_end|>"

TEMPLATE """Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{{ .Prompt }}

### Response:
"""
```

**Import to Ollama:**
```powershell
cd C:\GIT\Agents\models

# Create Ollama model from Modelfile
ollama create phi3-scientific -f Modelfile

# Test
ollama run phi3-scientific "Write an abstract about AI in healthcare"
```

**Option B: Use with LangChain + LoRA**

If you only have LoRA adapters, you'll need to load them with base model in Python:

```python
# Will be used in Phase 6
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

base_model = AutoModelForCausalLM.from_pretrained("microsoft/phi-3-mini-4k-instruct")
model = PeftModel.from_pretrained(base_model, "models/phi3_finetuned_lora")
```

### Step 5.3: Verify Local Model

```powershell
# List Ollama models
ollama list

# Should show:
# NAME                    ID              SIZE
# phi3-scientific:latest  abc123          2.3GB
# phi3:mini              xyz789          2.3GB

# Test generation
ollama run phi3-scientific "Write a one-sentence abstract on CKD prediction"
```

---

## Phase 6: Integrate with Paper Writer

### Step 6.1: Update Settings

**Edit: `src/config/settings.py`**

Add LLM provider configuration:

```python
class Settings:
    """Centralized configuration for the Scientific Paper Writer"""
    
    # API Configuration
    GOOGLE_API_KEY: str = os.getenv('GOOGLE_API_KEY', '')
    
    # LLM Provider Selection
    LLM_PROVIDER: str = 'gemini'  # 'gemini' or 'ollama'
    
    # Gemini Configuration
    GEMINI_MODEL: str = 'gemini-1.5-flash'
    TEMPERATURE: float = 0.7
    MAX_RETRIES: int = 5
    REQUEST_TIMEOUT: int = 180
    
    # Ollama Configuration
    OLLAMA_MODEL: str = 'phi3-scientific'  # Your fine-tuned model
    OLLAMA_BASE_URL: str = 'http://localhost:11434'
    OLLAMA_TIMEOUT: int = 300  # Longer timeout for CPU inference
    
    # ... rest of settings
```

### Step 6.2: Update LLM Service

**Edit: `src/services/llm_service.py`**

```python
"""LLM Service for managing language model initialization"""

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.llms import Ollama
from ..config.settings import Settings


class LLMService:
    """Service for initializing and managing LLM instances"""
    
    def __init__(self):
        """Initialize LLM service with settings"""
        self.settings = Settings
        self._llm = None
    
    def get_llm(self):
        """
        Initialize and return LLM based on provider setting.
        
        Returns:
            LLM instance (Gemini or Ollama)
        
        Raises:
            ValueError: If provider is invalid or credentials missing
        """
        if self._llm is None:
            provider = self.settings.LLM_PROVIDER.lower()
            
            if provider == 'gemini':
                self._llm = self._get_gemini_llm()
            elif provider == 'ollama':
                self._llm = self._get_ollama_llm()
            else:
                raise ValueError(
                    f"Invalid LLM provider: {provider}. "
                    f"Must be 'gemini' or 'ollama'"
                )
        
        return self._llm
    
    def _get_gemini_llm(self):
        """Initialize Gemini LLM"""
        if not self.settings.GOOGLE_API_KEY:
            raise ValueError(
                "GOOGLE_API_KEY not found in environment variables.\n"
                "Please create a .env file with your Google API key."
            )
        
        return ChatGoogleGenerativeAI(
            model=self.settings.GEMINI_MODEL,
            temperature=self.settings.TEMPERATURE,
            google_api_key=self.settings.GOOGLE_API_KEY,
            max_retries=self.settings.MAX_RETRIES,
            request_timeout=self.settings.REQUEST_TIMEOUT
        )
    
    def _get_ollama_llm(self):
        """Initialize Ollama LLM"""
        print(f"🔧 Using Ollama: {self.settings.OLLAMA_MODEL}")
        print(f"⚠️  Note: CPU inference may be slow (2-5 tokens/sec)")
        
        return Ollama(
            model=self.settings.OLLAMA_MODEL,
            base_url=self.settings.OLLAMA_BASE_URL,
            temperature=self.settings.TEMPERATURE,
            timeout=self.settings.OLLAMA_TIMEOUT
        )
    
    @property
    def model_name(self) -> str:
        """Get the current model name"""
        provider = self.settings.LLM_PROVIDER.lower()
        if provider == 'gemini':
            return self.settings.GEMINI_MODEL
        elif provider == 'ollama':
            return self.settings.OLLAMA_MODEL
        return "unknown"
    
    @property
    def temperature(self) -> float:
        """Get the current temperature setting"""
        return self.settings.TEMPERATURE
```

### Step 6.3: Add Provider Selection to Input Handler

**Edit: `src/utils/input_handler.py`**

Add new method:

```python
class InputHandler:
    """Handles user input and validation"""
    
    # ... existing methods ...
    
    @staticmethod
    def select_llm_provider() -> str:
        """
        Prompt user to select LLM provider.
        
        Returns:
            'gemini' or 'ollama'
        """
        print("\nSelect LLM Provider:")
        print("  1. Gemini (Fast, cloud-based, requires API key)")
        print("  2. Ollama (Local, private, slower on CPU)")
        print()
        
        choice = input("Enter choice (1-2 or gemini/ollama): ").strip().lower()
        
        if choice in ['1', 'gemini']:
            return 'gemini'
        elif choice in ['2', 'ollama']:
            return 'ollama'
        
        # Default to Gemini
        print("⚠️  Invalid choice. Defaulting to Gemini.")
        return 'gemini'
```

### Step 6.4: Update Main Entry Point

**Edit: `scripts/paper_writer.py`**

Add provider selection:

```python
def main():
    """Main execution function"""
    
    print("="*80)
    print("ADVANCED SCIENTIFIC PAPER WRITER")
    print("Powered by Multi-Agent AI")
    print("="*80)
    print()
    
    try:
        # Get LLM provider choice
        from src.utils.input_handler import InputHandler
        from src.config.settings import Settings
        
        llm_provider = InputHandler.select_llm_provider()
        Settings.LLM_PROVIDER = llm_provider
        
        # Rest of your existing code...
        citation_format_key = InputHandler.select_citation_format()
        # ... etc
```

### Step 6.5: Test Integration

**Test with Ollama:**

```powershell
cd C:\GIT\Agents
.venv\Scripts\Activate.ps1

# Run paper writer
python scripts/paper_writer.py
```

**At prompts, choose:**
```
Select LLM Provider:
  1. Gemini (Fast, cloud-based, requires API key)
  2. Ollama (Local, private, slower on CPU)

Enter choice (1-2 or gemini/ollama): 2

Select citation format: 1 (IEEE)
Enter topic: Machine learning in healthcare
Filename: test_ollama_paper
Use RAG: n
Export PDF: y
```

**Expected behavior:**
- Uses your fine-tuned Phi-3 model
- Slower generation (2-5 tokens/sec)
- Generates complete paper
- Quality depends on your training data

### Step 6.6: Compare Results

**Generate same paper with both providers:**

```powershell
# Test 1: Gemini
python scripts/paper_writer.py
# Choose: Gemini, IEEE, "ML in healthcare", no RAG

# Test 2: Ollama
python scripts/paper_writer.py
# Choose: Ollama, IEEE, "ML in healthcare", no RAG

# Compare outputs
code outputs/papers/test_gemini_paper.md
code outputs/papers/test_ollama_paper.md
```

---

## Phase 7: Advanced Usage

### Hybrid Mode (Best of Both Worlds)

**Strategy 1: Task-Specific**
```python
# Use Ollama for research (factual, grounded)
# Use Gemini for writing (creative, fluent)

if task_type == 'research':
    Settings.LLM_PROVIDER = 'ollama'
elif task_type == 'writing':
    Settings.LLM_PROVIDER = 'gemini'
```

**Strategy 2: Cost Optimization**
```python
# Use Ollama for drafts (free, unlimited)
# Use Gemini for final polish (paid, high quality)

if draft_mode:
    Settings.LLM_PROVIDER = 'ollama'
else:
    Settings.LLM_PROVIDER = 'gemini'
```

**Strategy 3: Privacy-Sensitive**
```python
# Use Ollama for sensitive data (local, private)
# Use Gemini for public data (cloud, fast)

if contains_sensitive_data(topic):
    Settings.LLM_PROVIDER = 'ollama'
else:
    Settings.LLM_PROVIDER = 'gemini'
```

---

## Troubleshooting

### Common Issues

#### **Issue 1: Ollama Model Not Found**

```
Error: model 'phi3-scientific' not found
```

**Solution:**
```powershell
# List available models
ollama list

# If model missing, recreate from Modelfile
cd C:\GIT\Agents\models
ollama create phi3-scientific -f Modelfile

# Or pull base model
ollama pull phi3:mini
```

#### **Issue 2: Slow Generation (< 1 token/sec)**

```
⚠️  Generation very slow: 0.5 tokens/sec
```

**Solutions:**
1. **Reduce context length** in settings:
   ```python
   OLLAMA_MAX_TOKENS: int = 512  # Instead of 2048
   ```

2. **Use smaller batch in Crew**:
   ```python
   # Reduce agent verbosity
   agent.verbose = False
   ```

3. **Switch to Gemini for final generation**:
   ```python
   # Draft with Ollama, final with Gemini
   ```

#### **Issue 3: Out of Memory**

```
Error: failed to allocate memory
```

**Solutions:**
1. **Close other applications**
2. **Reduce model size**:
   ```powershell
   # Use smaller quantization
   ollama pull phi3:mini-q2_k  # Even more compressed
   ```

3. **Increase virtual memory** (Windows):
   - Settings → System → About → Advanced system settings
   - Performance → Settings → Advanced → Virtual memory
   - Set to 24GB (1.5x your RAM)

#### **Issue 4: Fine-Tuned Model Quality Poor**

```
Generated text is nonsensical or off-topic
```

**Solutions:**
1. **More training data** (< 100 examples is too few)
2. **Better data quality** (check for errors in training_data.json)
3. **More training steps**:
   ```python
   # In Colab, increase max_steps
   max_steps = 500  # Instead of 100
   ```

4. **Adjust LoRA rank**:
   ```python
   # Higher rank = more parameters = better quality
   r = 32  # Instead of 16
   ```

#### **Issue 5: Colab Disconnects During Training**

```
Runtime disconnected. You were idle for too long.
```

**Solutions:**
1. **Keep tab active** (don't switch tabs)
2. **Use Colab Pro** ($10/month, longer runtime)
3. **Save checkpoints** more frequently:
   ```python
   save_steps = 25  # Instead of 50
   ```

4. **Resume from checkpoint**:
   ```python
   # In Colab, if disconnected
   trainer = SFTTrainer(
       # ... same config ...
       args = TrainingArguments(
           # ... same args ...
           resume_from_checkpoint = "outputs/checkpoint-50"
       )
   )
   ```

---

## Performance Benchmarks

### Expected Performance on Your Hardware

**i5 8th Gen, 16GB RAM, No GPU:**

| Model | Setup | Speed | Quality | Use Case |
|-------|-------|-------|---------|----------|
| Gemini 1.5 Flash | Cloud | ⚡ ~50 tok/s | ⭐⭐⭐⭐⭐ | Production |
| Phi-3 Mini (Base) | Ollama | 🐌 2-5 tok/s | ⭐⭐⭐ | Learning |
| Phi-3 Mini (Fine-tuned) | Ollama | 🐌 2-5 tok/s | ⭐⭐⭐⭐ | Domain-specific |
| Phi-3 Medium | Too slow | ❌ <1 tok/s | ⭐⭐⭐⭐ | Not recommended |

**Paper Generation Time:**

| Provider | Research | Writing | Total |
|----------|----------|---------|-------|
| Gemini | 30 sec | 60 sec | ~2 min |
| Ollama (Phi-3) | 5 min | 10 min | ~15 min |

**Fine-Tuning Time:**

| Hardware | Data Size | LoRA Training | Full Training |
|----------|-----------|---------------|---------------|
| Colab T4 GPU | 500 examples | 20-30 min | N/A (too large) |
| Colab T4 GPU | 1000 examples | 40-60 min | N/A |
| Your i5 CPU | 500 examples | 6-12 hours ❌ | Not feasible |

**Verdict**: Use Colab for fine-tuning, use locally for inference.

---

## Cost Analysis

### Free Tier Limits

**Google Colab (Free):**
- GPU time: ~12-15 hours/week
- RAM: 12GB
- Storage: 100GB temporary
- **Cost**: $0

**Google Colab Pro:**
- GPU time: ~100 hours/month
- RAM: 25GB
- Storage: Persistent
- **Cost**: $10/month

**Ollama (Local):**
- Unlimited inference
- No API costs
- Electricity: ~$0.10/hour (100W × $0.10/kWh)
- **Cost**: ~$0 (negligible)

**Gemini API:**
- Free tier: 15 RPM, 1M tokens/day
- Paid tier: $0.35/1M input tokens, $1.05/1M output tokens
- Average paper: ~5000 tokens input + 10000 output = $0.12/paper
- **Cost**: ~$0.12/paper

### Hybrid Strategy Cost

**Scenario**: Generate 100 papers/month

| Strategy | Gemini Cost | Ollama Cost | Total |
|----------|-------------|-------------|-------|
| All Gemini | $12 | $0 | $12/month |
| All Ollama | $0 | ~$0 | $0/month |
| Hybrid (50/50) | $6 | ~$0 | $6/month |

**Best value**: Hybrid approach for quality + savings!

---

## Next Steps

### After Completing This Guide

1. **✅ You now have:**
   - Ollama running locally
   - Phi-3 Mini fine-tuned on your domain
   - Integrated with paper writer
   - Hybrid Gemini/Ollama mode

2. **🚀 Experiment with:**
   - Different training datasets
   - Larger models (Phi-3 Medium on better hardware)
   - Different LoRA configurations
   - Prompt engineering for better outputs

3. **📊 Evaluate:**
   - Compare Gemini vs Ollama quality
   - Measure cost savings
   - Assess speed trade-offs
   - Gather user feedback

4. **🔧 Optimize:**
   - Fine-tune more (more data = better results)
   - Adjust temperature/top_p parameters
   - Create specialized models (citation-only, abstract-only)
   - Build ensemble (multiple models voting)

---

## Resources

### Documentation
- **Ollama**: https://ollama.com/library/phi3
- **Unsloth**: https://github.com/unslothai/unsloth
- **Phi-3**: https://huggingface.co/microsoft/Phi-3-mini-4k-instruct
- **LangChain Ollama**: https://python.langchain.com/docs/integrations/llms/ollama

### Tutorials
- **Fine-tuning LLMs**: https://huggingface.co/blog/llama2
- **LoRA explained**: https://arxiv.org/abs/2106.09685
- **Quantization guide**: https://huggingface.co/docs/transformers/quantization

### Communities
- **Ollama Discord**: https://discord.gg/ollama
- **r/LocalLLaMA**: https://reddit.com/r/LocalLLaMA
- **Hugging Face Forums**: https://discuss.huggingface.co/

---

## Summary

**What You've Learned:**

1. ✅ Setup Ollama locally on Windows
2. ✅ Test baseline Phi-3 Mini performance
3. ✅ Prepare scientific paper training data
4. ✅ Fine-tune on Google Colab with free GPU
5. ✅ Export and import to Ollama
6. ✅ Integrate with your existing paper writer
7. ✅ Use hybrid Gemini/Ollama strategy

**Key Takeaways:**

- 🎯 Fine-tuning improves domain-specific quality
- ⚡ Colab GPU is 10-20x faster than local CPU
- 💰 Hybrid approach balances cost and quality
- 🔒 Ollama provides privacy for sensitive data
- 🚀 Gemini provides speed for production use

**Time Investment:**
- Setup: 1-2 hours
- Fine-tuning: 30-60 minutes (Colab)
- Integration: 30 minutes
- **Total**: 2-4 hours

**Result**: A powerful, flexible paper writing system that you fully control! 🎉

---

**Need Help?** Open an issue on GitHub or ask in the Ollama Discord!

**Happy Fine-Tuning!** 🚀✨
