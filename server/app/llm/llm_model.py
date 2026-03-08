import os
import torch
from dotenv import load_dotenv
from threading import Lock
from typing import Optional, Generator

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    TextIteratorStreamer
)

load_dotenv()

MODEL_NAME = os.getenv("MODEL_NAME", "HuggingFaceTB/SmolLM3-3B")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

_tokenizer: Optional[AutoTokenizer] = None
_model: Optional[AutoModelForCausalLM] = None
_model_lock = Lock()


# -----------------------------
# Quantization
# -----------------------------
def _bnb_config():
    return BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.float16
    )


# -----------------------------
# Model loader
# -----------------------------
def load_model():
    global _tokenizer, _model

    if _model is not None:
        return

    with _model_lock:

        if _model is not None:
            return

        use_cuda = torch.cuda.is_available()

        _tokenizer = AutoTokenizer.from_pretrained(
            MODEL_NAME,
            use_fast=False
        )

        if use_cuda:
            _model = AutoModelForCausalLM.from_pretrained(
                MODEL_NAME,
                device_map="auto",
                quantization_config=_bnb_config(),
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
        else:
            _model = AutoModelForCausalLM.from_pretrained(
                MODEL_NAME,
                torch_dtype=torch.float32,
                trust_remote_code=True
            ).to("cpu")

        _model.eval()


# -----------------------------
# Build chat messages
# -----------------------------
def build_messages(question: str, context: str, history: str = ""):

    system_prompt = (
        "/no_think\n"
        "Answer using ONLY the provided context.\n"
        "If the context does not contain the answer, respond exactly:\n"
        "I don't know."
    )

    messages = [
        {"role": "system", "content": system_prompt}
    ]

    if history:
        messages.append({"role": "assistant", "content": history})

    messages.append({
        "role": "user",
        "content": f"Context:\n{context}\n\nQuestion:\n{question}"
    })

    return messages


# -----------------------------
# Clean model output
# -----------------------------
import re

def clean_output(decoded: str, prompt: str) -> str:
    text = decoded

    # Remove the prompt if present
    if text.startswith(prompt):
        text = text[len(prompt):]

    text = text.strip()

    # Remove reasoning blocks
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)

    # Remove role markers
    text = re.sub(r"\bassistant\b", "", text, flags=re.IGNORECASE)

    # Remove prompt echoes
    text = re.sub(r"Context:.*?Question:", "", text, flags=re.DOTALL)
    text = re.sub(r"Question:.*", "", text)

    text = text.strip()

    # If model said "I don't know", enforce exact output
    if "i don't know" in text.lower():
        return "I don't know."

    # Keep only first paragraph
    text = text.split("\n\n")[0]

    return text.strip()

# -----------------------------
# Generate answer
# -----------------------------
def generate_answer(
    question: str,
    context: str,
    history: str = "",
    max_new_tokens: int = 128
) -> str:

    load_model()

    messages = build_messages(question, context, history)

    prompt = _tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    inputs = _tokenizer(
        prompt,
        return_tensors="pt"
    ).to(_model.device)

    with torch.no_grad():
        output = _model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.3,
            top_p=0.95,
            do_sample=True,
            eos_token_id=_tokenizer.eos_token_id,
            pad_token_id=_tokenizer.eos_token_id
        )

    decoded = _tokenizer.decode(output[0], skip_special_tokens=True)

    answer = clean_output(decoded, prompt)

    if answer.lower().startswith("i don't know"):
        return "I don't know."

    return answer


# -----------------------------
# Streaming version
# -----------------------------
def stream_answer(
    question: str,
    context: str,
    history: str = "",
    max_new_tokens: int = 128
) -> Generator[str, None, None]:

    load_model()

    messages = build_messages(question, context, history)

    prompt = _tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    inputs = _tokenizer(
        prompt,
        return_tensors="pt"
    ).to(_model.device)

    streamer = TextIteratorStreamer(
        _tokenizer,
        skip_prompt=True,
        skip_special_tokens=True
    )

    generation_kwargs = dict(
        **inputs,
        streamer=streamer,
        max_new_tokens=max_new_tokens,
        temperature=0.3,
        top_p=0.95,
        do_sample=True,
        eos_token_id=_tokenizer.eos_token_id,
        pad_token_id=_tokenizer.eos_token_id
    )

    import threading

    thread = threading.Thread(
        target=_model.generate,
        kwargs=generation_kwargs
    )
    thread.start()

    for token in streamer:
        yield token