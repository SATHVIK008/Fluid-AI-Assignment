import os
import re
import streamlit as st
from io import BytesIO
from pypdf import PdfReader
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import google.generativeai as genai

# Set up API keys
google_api_key = 'AIzaSyD2_oxzOQQtcGDmW_Ul8E7mREi_LYYJO9I'
os.environ['GOOGLE_API_KEY'] = google_api_key

# Configure the Gemini API
genai.configure(api_key=google_api_key)

# Function to generate a prompt for analyzing company data
def generate_investor_prompt(pdf_text):
    prompt = (
        f"The following text contains information about a company's business, growth prospects, "
        f"and other key aspects. Analyze the text for an investor looking to evaluate the company. "
        f"Focus on future growth prospects, key changes in the business, triggers, and information "
        f"that could materially affect next year's earnings and growth:\n\n{pdf_text}"
    )
    return prompt

# Function to extract text from the uploaded PDF
def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = " ".join(page.extract_text() for page in reader.pages if page.extract_text())
    return text

# Function to generate insights using Gemini API
def generate_analysis(prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text

# Function to create a word cloud visualization
def generate_wordcloud(insights):
    wordcloud = WordCloud(background_color="white", width=800, height=400).generate(insights)
    plt.figure(figsize=(10, 6))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    st.pyplot(plt)

# Function to extract deltas from insights
def extract_deltas(insights):
    growth_delta = re.search(r"growth.*?(\d+%)", insights, re.IGNORECASE)
    stability_delta = re.search(r"stability.*?(\d+%)", insights, re.IGNORECASE)
    trends_delta = re.search(r"trends.*?(\d+%)", insights, re.IGNORECASE)

    growth = growth_delta.group(1) if growth_delta else "N/A"
    stability = stability_delta.group(1) if stability_delta else "N/A"
    trends = trends_delta.group(1) if trends_delta else "N/A"

    return growth, stability, trends

# Streamlit App
st.set_page_config(layout="wide", page_title="Investor Evaluation Tool")

# Sidebar for PDF upload
st.sidebar.title("Investor Evaluation Tool")
uploaded_file = st.sidebar.file_uploader("Upload a PDF containing company information:", type="pdf")

if uploaded_file is not None:
    # Extract text from the uploaded PDF
    st.sidebar.write("Extracting text from the PDF...")
    pdf_text = extract_text_from_pdf(uploaded_file)
    st.sidebar.write("Text successfully extracted.")

    # Generate the prompt and analyze the PDF content
    prompt = generate_investor_prompt(pdf_text)
    st.sidebar.write("Analyzing the document for key insights...")
    insights = generate_analysis(prompt)

    # Download insights as a text file
    download_button = BytesIO()
    download_button.write(insights.encode('utf-8'))
    download_button.seek(0)
    st.sidebar.download_button(
        label="Download Insights",
        data=download_button,
        file_name="investor_insights.txt",
        mime="text/plain",
    )

    # Main page layout
    col1, col2 = st.columns([1, 3])

    with col1:
        # Visualization: Word Cloud
        st.subheader("Word Cloud")
        generate_wordcloud(insights)

        # Interactive Dashboard
        st.subheader("Dashboard")
        growth_delta, stability_delta, trends_delta = extract_deltas(insights)
        st.metric("Growth Potential", "High", delta=growth_delta)
        st.metric("Revenue Stability", "Stable", delta=stability_delta)

    with col2:
        # Display the analysis results
        st.subheader("Key Insights for Investor")
        st.write(insights)
else:
    st.sidebar.write("Please upload a PDF to proceed.")
