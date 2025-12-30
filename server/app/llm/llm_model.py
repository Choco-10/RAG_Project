from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Small free model
MODEL_NAME = "tiiuae/falcon-7b-instruct"  # replace with small variant if low RAM

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, device_map="auto", torch_dtype=torch.float16)

def generate_answer(question: str, context: str, max_length: int = 512) -> str:
    """
    Combines question + retrieved context and generates an LLM answer.
    """
    prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    output = model.generate(
        **inputs,
        max_new_tokens=max_length,
        temperature=0.2,
        do_sample=True,
        top_p=0.9
    )

    answer = tokenizer.decode(output[0], skip_special_tokens=True)
    # Remove the repeated prompt
    return answer.replace(prompt, "").strip()
