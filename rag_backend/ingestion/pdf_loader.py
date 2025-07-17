# PDF loader
import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    """
    Extracts text page-by-page from a PDF using PyMuPDF.
    Returns a list of dicts with page content and metadata.
    """
    doc = fitz.open(pdf_path)
    pages = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()
        pages.append({
            "page_number": page_num + 1,
            "text": text.strip(),
        })

    doc.close()
    return pages

pdf_path = "/content/drive/MyDrive/Colab Notebooks/RAG_Agent/Input/RTCU_Manual.pdf"
pages = extract_text_from_pdf(pdf_path)

for p in pages[:2]:  # Preview first 2 pages
    print(f"\n--- Page {p['page_number']} ---")
    print(p['text'][:500])  # Preview first 500 characters

import json

with open("/content/drive/MyDrive/Colab Notebooks/RAG_Agent/Input/extracted_pages.json", "w", encoding="utf-8") as f:
    json.dump(pages, f, ensure_ascii=False, indent=2)
import spacy
nlp = spacy.load("en_core_web_sm")

def split_into_sentences(text):
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents]

def chunk_text_from_pages(pages, chunk_size=300, overlap=50):
    all_chunks = []

    for page in pages:
        sentences = split_into_sentences(page["text"])
        current_chunk = []
        total_words = 0

        for sentence in sentences:
            words = sentence.split()
            total_words += len(words)
            current_chunk.append(sentence)

            if total_words >= chunk_size:
                chunk_text = " ".join(current_chunk)
                all_chunks.append({
                    "page_number": page["page_number"],
                    "text": chunk_text.strip()
                })

                # Overlap logic
                overlap_words = " ".join(current_chunk)[-overlap:]
                current_chunk = [overlap_words]
                total_words = len(overlap_words.split())

        # Add leftovers
        if current_chunk:
            all_chunks.append({
                "page_number": page["page_number"],
                "text": " ".join(current_chunk).strip()
            })

    return all_chunks

chunks = chunk_text_from_pages(pages)
print(f"Total chunks: {len(chunks)}")
print("Sample chunk:")
print(chunks[0]["text"][:200])
