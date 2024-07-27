def chunk_text(text, chunk_size, overlap_size):
    """
    Splits text into chunks with overlap.

    Parameters:
    text (str): The text to be chunked.
    chunk_size (int): The size of each chunk.
    overlap_size (int): The size of the overlap between chunks.

    Returns:
    list: A list of text chunks.
    """
    chunks = []
    i = 0
    while i < len(text):
        chunk = text[i:i + chunk_size]
        chunks.append(chunk)
        i += chunk_size - overlap_size

    return chunks
