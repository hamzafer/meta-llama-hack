from transformers import LlamaForCausalLM, LlamaTokenizer, Trainer, TrainingArguments
from peft import LoraConfig, get_peft_model
from transformers import AutoTokenizer

# model_name = "meta-llama/Llama-3-70B"  # Change if using another size
# tokenizer = LlamaTokenizer.from_pretrained(model_name)
# model = LlamaForCausalLM.from_pretrained(model_name)

model_name = "meta-llama/Llama-3-70B"
hf_token = "your_huggingface_token_here"  # Replace with your token

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.3-70B", use_auth_token=hf_token)


# Apply LoRA
config = LoraConfig(r=8, lora_alpha=16, lora_dropout=0.1, task_type="CAUSAL_LM")
model = get_peft_model(model, config)

# Tokenize the dataset
from datasets import load_dataset

dataset = load_dataset("json", data_files="norges-bank-translations.json")

instruction = "Translate the following Norwegian text into English. ONLY OUTPUT the English text and nothing else:"

def tokenize_function(examples):
    return tokenizer(instruction + " " + examples["english"], text_target=examples["norwegian"])

tokenized_datasets = dataset.map(tokenize_function, batched=True)

# Training
training_args = TrainingArguments(
    output_dir="./llama_mt",
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    num_train_epochs=3,
    save_steps=500,
    save_total_limit=2,
    logging_dir="./logs",
    report_to="none"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets["train"]
)

trainer.train()
model.save_pretrained("./llama_mt_finetuned")
