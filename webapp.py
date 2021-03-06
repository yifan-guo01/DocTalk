import langid
import streamlit as st
import csv
import os
from doctalk.talk import *


def main():
    #SUPPORTED_LANGUAGES = get_supported_langs('StanzaSupportedLanguages.csv')
    st.sidebar.title('DocTalk')
    msg = '''A Multilingual STANZA-based Summary and Keyword Extractor and Question-Answering \
    System using TextGraphs and Neural Networks'''
    st.sidebar.write(msg)
    text_file = st.sidebar.file_uploader('Select a File', type=['txt','pdf'])
    talker = None
    title = None
    #selected_lang = st.sidebar.selectbox('Language', tuple(SUPPORTED_LANGUAGES.keys()), index=17)
    #lang = SUPPORTED_LANGUAGES[selected_lang]

    if text_file is not None:
        text = text_file.getvalue().decode("utf-8")
        lang = langid.classify(text)[0]
        st.sidebar.write(f'Language: {lang}')

        if not title or title != text_file.name:
            talker = Talker(from_text=text)
            title = text_file.name
            # talker.show_all()
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


if __name__ == "__main__":
    main()
