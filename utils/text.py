from langchain.text_splitter import RecursiveCharacterTextSplitter
from pythainlp.tokenize import word_tokenize
import re

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
    
def clean_md(text):
    # Remove code blocks
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    # Remove inline code
    text = re.sub(r'`.*?`', '', text)
    # Remove headings
    text = re.sub(r'#+ ', '', text)
    # Remove markdown links, keep the text
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    # Remove lists markers
    text = re.sub(r'^[-*+] ', '', text, flags=re.MULTILINE)
    # Collapse multiple whitespaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()