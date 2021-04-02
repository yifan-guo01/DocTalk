import langid
import streamlit as st
from doctalk.talk import *
import os

UPLOAD_DIRECTORY = "uploads"


def main():
    st.sidebar.title('DocTalk')
    msg = '''A Multilingual STANZA-based Summary and Keyword Extractor and Question-Answering \
    System using TextGraphs and Neural Networks'''
    st.sidebar.write(msg)
    uploaded_file = st.sidebar.file_uploader('Select a File', type=['txt', 'pdf'])
    talker = None
    title = None

    if uploaded_file is not None:
        print(f"New file uploaded: {uploaded_file.name}")
        fpath = save_uploaded_file(uploaded_file)
        if fpath[-4:] == '.pdf':
            pdf2txt(fpath[:-4])
        text = file2string(fpath[:-4] + '.txt')

        lang = langid.classify(text)[0]
        st.sidebar.write(f'Language: {lang}')

        if not title or title != uploaded_file.name:
            talker = Talker(from_text=text)
            title = uploaded_file.name

        action = st.sidebar.selectbox("Choose an action", ["Summarize", "Ask a question"])
        if action == "Summarize":
            summarizer(talker)
            pass
        elif action == "Ask a question":
            answerer(talker, lang)
    else:
        st.info("Please select a text file to upload")


def summarizer(talker):
    notice = st.empty()
    notice.empty()
    st.header("Summary")
    st.write('\n\n'.join(talker.show_summary()))
    st.header("Keywords")
    st.write(', '.join(talker.get_keys()))


def answerer(talker, lang):
    notice = st.empty()
    notice.info("Analyzing text")
    notice.empty()
    question = st.text_input("Enter a question")
    if question:
        long_answers, short_answer = interact(question, talker)
        if lang == 'en':
            st.write(f"Long Answer:\n" + '\n\n'.join(long_answers))
            st.write(f"Short Answer: " + short_answer[:short_answer.rfind(',')])
        else:
            st.write('\n\n'.join(long_answers))


def save_uploaded_file(uploaded_file, fname=None):
    if not fname:
        fname = uploaded_file.name
    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY)
    fpath = os.path.join(UPLOAD_DIRECTORY, fname)
    with open(fpath, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return fpath


if __name__ == "__main__":
    main()
