import ast
import nltk
import difflib
import numpy as np
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st

# Initialize the transformer model for code classification
try:
    tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-mnli")
    model = AutoModelForSequenceClassification.from_pretrained("facebook/bart-large-mnli")
    nlp_model = pipeline("text-classification", model=model, tokenizer=tokenizer)
except Exception as e:
    print(f"Error loading model: {e}")
    nlp_model = None

def preprocess_code(code):
    # Remove comments and normalize whitespace
    code = '\n'.join(line for line in code.splitlines() if not line.strip().startswith('#'))
    return ' '.join(code.split())

def compute_ast_similarity(code1, code2):
    tree1 = ast.parse(code1)
    tree2 = ast.parse(code2)
    return difflib.SequenceMatcher(None, ast.dump(tree1), ast.dump(tree2)).ratio()

def compute_tfidf_similarity(code1, code2):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([code1, code2])
    return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

def calculate_code_metrics(code):
    tokens = nltk.word_tokenize(code)
    num_tokens = len(tokens)
    avg_token_length = np.mean([len(token) for token in tokens])
    lines_of_code = len(code.splitlines())
    num_functions = len([line for line in code.splitlines() if 'def ' in line])
    return num_tokens, avg_token_length, lines_of_code, num_functions

def is_generated_code(code):
    # Preprocess code
    preprocessed_code = preprocess_code(code)

    # Compute similarities
    ast_sim = compute_ast_similarity(code, code)
    tfidf_sim = compute_tfidf_similarity(preprocessed_code, preprocessed_code)

    # Calculate code metrics
    num_tokens, avg_token_length, lines_of_code, num_functions = calculate_code_metrics(code)

    # Classification using the pre-trained model
    if nlp_model:
        try:
            result = nlp_model(preprocessed_code)
            label = result[0]['label']
        except Exception as e:
            print(f"Error during model inference: {e}")
            label = "Unknown"
    else:
        label = "Unknown"

    # Define thresholds for classification
    ast_threshold = 0.7
    tfidf_threshold = 0.65
    num_tokens_threshold = 100
    avg_token_length_threshold = 3
    lines_of_code_threshold = 5
    num_functions_threshold = 0

    # Decision based on thresholds
    if (
            ast_sim > ast_threshold and
            tfidf_sim > tfidf_threshold and
            num_tokens > num_tokens_threshold and
            avg_token_length > avg_token_length_threshold and
            lines_of_code > lines_of_code_threshold and
            num_functions > num_functions_threshold
    ):
        return f"Likely generated by a language model (Label: {label})"
    else:
        return f"Not likely generated by a language model (Label: {label})"

def main():
    st.title("IntegrityAI")
    code = st.text_area("Enter the code you want to analyze", height=200)
    if st.button("Analyze"):
        if code:
            # Detect code type
            result = is_generated_code(code)

            # Display results
            st.write("Code Analysis Result:", result)

            # Display metrics
            num_tokens, avg_token_length, lines_of_code, num_functions = calculate_code_metrics(code)
            st.write("Number of Tokens:", num_tokens)
            st.write("Average Token Length:", avg_token_length)
            st.write("Lines of Code:", lines_of_code)
            st.write("Number of Functions:", num_functions)

            # (Optional) Display visualizations or additional analyses if needed

        else:
            st.warning("Please enter some code to analyze.")

if _name_ == "_main_":
    main()
