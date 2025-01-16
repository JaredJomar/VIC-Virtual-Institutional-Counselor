from pypdf import PdfReader
from os import listdir
from langchain.text_splitter import RecursiveCharacterTextSplitter
from transformers import AutoTokenizer, AutoModel
import torch
import re
import json

MODEL_NAME = "facebook/dpr-question_encoder-single-nq-base"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)

FILES_DIR = "./syllabuses"
EMBEDDING_CACHE = "./embeddings_cache.json"

def normalize_text(text):
    """
    Cleans and normalizes text for consistent processing.
    """
    text = re.sub(r"\s+", " ", text)  # Replace multiple spaces/newlines with a single space
    text = text.strip()  # Remove leading/trailing spaces
    return text

def embed_text(text):
    """
    Generates embeddings for a given text using a Hugging Face DPR model.
    """
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=768, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
        embeddings = outputs.pooler_output.squeeze().tolist()  # Use pooler_output for embeddings
    return embeddings

def load_cache():
    """
    Loads the embedding cache from file.
    """
    try:
        with open(EMBEDDING_CACHE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_cache(cache):
    """
    Saves the embedding cache to file.
    """
    with open(EMBEDDING_CACHE, "w") as f:
        json.dump(cache, f)

def process_files():
    """
    Processes PDF files, extracts fragments, and embeds text.

    Returns:
        List[Dict]: A list of dictionaries containing embedding and chunk for each syllabus file.
    """
    files = listdir(FILES_DIR)
    all_syllabi_data = []
    cache = load_cache()

    for file_name in files:
        file_path = f"{FILES_DIR}/{file_name}"
        print(f"Processing file: {file_name}")

        reader = PdfReader(file_path)
        pdf_texts = [normalize_text(page.extract_text()) for page in reader.pages if page.extract_text()]
        if not pdf_texts:
            print(f"No text found in {file_name}. Skipping.")
            continue

        combined_text = f"{file_name[:4]} {file_name[5:9]}\n\n".join(pdf_texts)
        # print(combined_text)
        splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", ". ", " ", ""],
            chunk_size=800,  # Larger chunk size for better context
            chunk_overlap=100
        )
        text_chunks = splitter.split_text(combined_text)

        fragments = []
        for chunk in text_chunks:
            normalized_chunk = normalize_text(chunk)
            if normalized_chunk in cache:
                embedding = cache[normalized_chunk]  # Use cached embedding
            else:
                embedding = embed_text(normalized_chunk)
                cache[normalized_chunk] = embedding  # Save to cache
            
            fragments.append({
                "embedding": embedding,
                "chunk": normalized_chunk
            })

        # Extract metadata (e.g., course code and title from file name)
        course_name = re.search(r"(CIIC|INSO|ICOM)\s*\d{4}", file_name, re.IGNORECASE)
        course_code = file_name.split("-")[1] if "-" in file_name else "Unknown"

        all_syllabi_data.append({
            "file_name": file_name,
            "course_name": course_name.group(0) if course_name else "Unknown",
            "course_code": course_code,
            "fragments": fragments
        })

    save_cache(cache)
    return all_syllabi_data
