from transformers import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_text(text: str):
    return summarizer(text, max_length=150, min_length=50, do_sample=False)[0]['summary_text']
