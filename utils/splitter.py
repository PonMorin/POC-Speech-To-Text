from langchain.text_splitter import RecursiveCharacterTextSplitter
from pythainlp.tokenize import word_tokenize

def text_splitter(chunk_size: int, chunk_overlap) -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, 
            chunk_overlap=chunk_overlap,
            length_function=lambda text: len(word_tokenize(text, engine='newmm')),
            separators=[
                "\n\n",
                "\n",
                " ",
                ".",
                ",",
                "\u200b",  # Zero-width space
                "\uff0c",  # Fullwidth comma
                "\u3001",  # Ideographic comma
                "\uff0e",  # Fullwidth full stop
                "\u3002",  # Ideographic full stop
                "",
            ],
        )