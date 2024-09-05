import streamlit as st
import nltk
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
import string
import numpy as np
from transformers import pipeline

# Initialize the transformer model for text classification
classifier = pipeline("text-classification", model="facebook/bart-large-mnli")

def preprocess_text(text):
    if not isinstance(text, str):
        raise ValueError("Input must be a string")
    tokens = nltk.word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words and token not in string.punctuation]
    return tokens

def plot_most_common_words(tokens):
    word_freq = nltk.FreqDist(tokens)
    most_common_words = word_freq.most_common(10)

    words, counts = zip(*most_common_words)

    plt.figure(figsize=(10, 6))
    plt.bar(words, counts)
    plt.xlabel('Words')
    plt.ylabel('Frequency')
    plt.title('Most Common Words')
    plt.xticks(rotation=45)
    st.pyplot(plt)

def plot_repeated_words(tokens):
    word_freq = nltk.FreqDist(tokens)
    repeated_words = [word for word, count in word_freq.items() if count > 1]

    if not repeated_words:
        st.write("No repeated words found.")
        return

    # Ensure there are enough repeated words for plotting
    repeated_words = repeated_words[:10]  # Limit to the top 10 repeated words
    words, counts = zip(*[(word, word_freq[word]) for word in repeated_words])

    plt.figure(figsize=(10, 6))
    plt.bar(words, counts)
    plt.xlabel('Words')
    plt.ylabel('Frequency')
    plt.title('Repeated Words')
    plt.xticks(rotation=45)
    st.pyplot(plt)

def calculate_burstiness(text):
    tokens = preprocess_text(text)
    word_freq = nltk.FreqDist(tokens)
    avg_freq = np.mean(list(word_freq.values()))
    variance = np.var(list(word_freq.values()))
    burstiness_score = variance / (avg_freq ** 2) if avg_freq != 0 else 0
    return burstiness_score

def calculate_entropy(text):
    tokens = preprocess_text(text)
    token_counts = nltk.FreqDist(tokens)
    total_tokens = len(tokens)
    if total_tokens == 0:
        return 0
    entropy = -sum((count / total_tokens) * np.log2(count / total_tokens) for count in token_counts.values())
    return entropy

def calculate_avg_sentence_length(text):
    sentences = nltk.sent_tokenize(text)
    if len(sentences) == 0:
        return 0
    avg_length = np.mean([len(nltk.word_tokenize(sentence)) for sentence in sentences])
    return avg_length

def calculate_lexical_diversity(tokens):
    if len(tokens) == 0:
        return 0
    lexical_diversity = len(set(tokens)) / len(tokens)
    return lexical_diversity

def is_generated_text(text):
    tokens = preprocess_text(text)
    avg_sentence_length = calculate_avg_sentence_length(text)
    lexical_diversity = calculate_lexical_diversity(tokens)
    burstiness_score = calculate_burstiness(text)
    entropy = calculate_entropy(text)

    # Classification using the high-end model
    result = classifier(text)
    label = result[0]['label']

    # Conditions to classify text
    if (
            burstiness_score < 0.5 < lexical_diversity and
            avg_sentence_length > 15 and
            entropy > 5
        ):
            return "Likely generated by a language model"
    else:
            return "Not likely generated by a language model"

def main():
    st.title("IntegrityAI")
    text = st.text_area("Enter the text you want to analyze", height=200)
    if st.button("Analyze"):
        if text:
            # Calculate features
            tokens = preprocess_text(text)
            burstiness_score = calculate_burstiness(text)
            entropy = calculate_entropy(text)
            avg_sentence_length = calculate_avg_sentence_length(text)
            lexical_diversity = calculate_lexical_diversity(tokens)
            generated_cue = is_generated_text(text)

            # Display results
            st.write("Burstiness Score:", burstiness_score)
            st.write("Entropy:", entropy)
            st.write("Average Sentence Length:", avg_sentence_length)
            st.write("Lexical Diversity:", lexical_diversity)
            st.write("Text Analysis Result:", generated_cue)

            # Plot most common words
            plot_most_common_words(tokens)

            # Plot repeated words
            plot_repeated_words(tokens)

        else:
            st.warning("Please enter some text to analyze.")

if _name_ == "_main_":
    main()
