pages = extract_pages(pdf_path)

chunks = chunk_pages(pages)

for chunk in chunks:

    metadata = build_metadata(chunk, uploaded_file.filename)

    save_chunk(chunk, uploaded_file.filename, metadata)
