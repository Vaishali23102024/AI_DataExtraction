import streamlit as st

st.set_page_config(page_title="Gemini_Student", page_icon=":material/edit:")

st.sidebar.title("Welcome to Gemeni")
selection = st.sidebar.radio("",["Image_QA_Gemini","chat_with_pdf"])

if selection == "Image_QA_Gemini":
    import Image_QA_Gemini
    Image_QA_Gemini.show()
    
elif selection == "chat_with_pdf":
    import chat_with_pdf
    chat_with_pdf.show()