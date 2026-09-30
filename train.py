from unsloth import FastLanguageModel
import torch
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments

print("🚀 Démarrage de l'entraînement avec Unsloth...")

max_seq_length = 2048
model_name = "unsloth/mistral-7b-instruct-v0.2-bnb-4bit" 

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = model_name,
    max_seq_length = max_seq_length,
    dtype = None,
    load_in_4bit = True,
)

model = FastLanguageModel.get_peft_model(
    model,
    r = 16,
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_alpha = 16,
    lora_dropout = 0,
    bias = "none",
    use_gradient_checkpointing = "unsloth",
)

dataset = load_dataset("json", data_files="sonatel_huggingface_dataset.jsonl", split="train")

def format_prompt(examples):
    texts = []
    for messages in examples["messages"]:
        text = ""
        for msg in messages:
            if msg["role"] == "system":
                text += f"<|system|>\n{msg['content']}</s>\n"
            elif msg["role"] == "user":
                text += f"<|user|>\n{msg['content']}</s>\n"
            elif msg["role"] == "assistant":
                text += f"<|assistant|>\n{msg['content']}</s>\n"
        texts.append(text)
    return {"text": texts}

dataset = dataset.map(format_prompt, batched=True)

trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    dataset_text_field = "text",
    max_seq_length = max_seq_length,
    dataset_num_proc = 2,
    args = TrainingArguments(
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,
        warmup_steps = 10,
        max_steps = 100,
        learning_rate = 2e-4,
        fp16 = not torch.cuda.is_bf16_supported(),
        bf16 = torch.cuda.is_bf16_supported(),
        logging_steps = 10,
        optim = "adamw_8bit",
        output_dir = "outputs",
    ),
)

print("🔥 Début de l'entraînement...")
trainer.train()

model.save_pretrained("modele_wechat_sonatel")
tokenizer.save_pretrained("modele_wechat_sonatel")
print("✅ Entraînement terminé et modèle sauvegardé dans le dossier 'modele_wechat_sonatel' !")
