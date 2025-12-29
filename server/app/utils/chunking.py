def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list:
    """
    Splits text into chunks for embeddings.
    
    Args:
        text: full document text
        chunk_size: maximum number of characters per chunk
        overlap: number of characters to overlap between chunks
    
    Returns:
        List of text chunks
    """
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap  # slide window

    return chunks
