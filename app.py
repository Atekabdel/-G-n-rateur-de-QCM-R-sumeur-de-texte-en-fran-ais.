# Loading all necessary libraries
import streamlit as st
import spacy
from collections import Counter
import random
import nltk
nltk.download('wordnet')
from nltk.corpus import wordnet as wn
#from PyPDF2 import PdfReader



st.markdown("# NLP Project : Revision ")
st.write("The purpose of this project is to generate MCQ based on an uploaded file , the file can be either in french or in english")

#def read_pdf(file): 
  #  text =""
  #  reader = PdfReader(file)
  #  for num in range(len(reader.pages)):
       # page= reader.pages[num].extract_text()
       # text += page
   # return text*/

def read_txt(file):
    text=""
    text = file.read().decode('utf-8')
    return text

def read_file(file,type):
    if type == "txt":
        return read_txt(file)
    if type == "Pdf": return read_pdf(file)

def map2list (map):
    list = []
    for i in range(len(map)):
        list.append(map[i])
    return list

def get_synonyms(word):
    synonyms = []
    for syn in wn.synsets(word):
        for lemma in syn.lemmas():
            synonyms.append(lemma.name())
    return synonyms

def get_distractors_wordnet(syn,word):
    distractors=[]
    word= word.lower()
    orig_word = word
    if len(word.split())>0:
        word = word.replace(" ","_")
    hypernym = syn.hypernyms()
    if len(hypernym) == 0: 
        return distractors
    for item in hypernym[0].hyponyms():
        name = item.lemmas()[0].name()
        if name == orig_word:
            continue
        name = name.replace("_"," ")
        name = " ".join(w.capitalize() for w in name.split())
        if name is not None and name not in distractors:
            distractors.append(name)
    return distractors


def generate_MCQ(text, nlp, num = 5):
    if text is None:
        return []
    doc = nlp(text)
    ques =[sent.text for sent in doc.sents]
    if (len(ques)<num): num = len(ques)
    if (len(ques)>10): num = random.randint(num,10)

    else: num = random.randint(num,len(ques))
    selected = random.sample(ques, num)
    qcm = []
    for sent in selected : 
        doc_sent = nlp(sent)
        nouns = [sent.text for sent in doc_sent if sent.pos_ == "NOUN"]
        if len(nouns)<2: continue

        noun_counts = Counter(nouns) ## To compute the occurence of each noun 

        ## We'll use the most frequent noun to generate the mcq 
        if noun_counts:
            chosen = noun_counts.most_common(1)[0][0]
            
            question = sent.replace(chosen,'______________')
            chosen = " ".join(w.capitalize() for w in chosen.split())
            choices = [chosen]
            syns = wn.synsets(chosen,'n')
            distractors = get_distractors_wordnet(syns[0],chosen)
            distractor = list(set(nouns) - {chosen})
            for i in range(len(distractor)):
                distractors.append(distractor[i])
           # syn = get_synonyms(chosen)
           # for i in range(len(syn)):
            #    distractors.append(syn[i])
            random.shuffle(distractors)
            for distractor in distractors[:4]:
                choices.append(distractor)

            random.shuffle(choices)
            correct_answer = chr(64 + choices.index(chosen) + 1)  # Convert index to letter
            qcm.append((question, choices, correct_answer))
    return qcm
def map_to_form(qcm):
    for i in range(len(qcm)):
        st.radio(qcm[i][0], map2list(qcm[i][1]), key=f"qcm_{i}")
    submitted = st.button("Display correct answers")  
    if submitted:
        for i in range(len(qcm)):
            st.write("Correct Answer: " + str(qcm[i][2]))


if 'qcm' not in st.session_state:
    st.session_state.qcm = None
if 'summary' not in st.session_state:
    st.session_state.summary = None 

st.subheader("Uploading a file")
file = st.file_uploader("Upload your file")

language = st.radio("Select a language:", ["Fr", "En"])
tr = st.radio("you want to generate :", ["MCQ", "Summary"])

submitted = st.button("Generate")

if submitted:
    if file:
        text = read_file(file,"txt")
        if language == "Fr":
            nlp = spacy.load("fr_core_news_md")
        else:
            nlp = spacy.load("en_core_web_md")
        if tr == "MCQ":
            st.session_state.qcm = generate_MCQ(text, nlp)
    else:
        st.write("Please upload your file")

if st.session_state.qcm:
    st.write("## QCM : ")
    map_to_form(st.session_state.qcm)
    if st.button("Restart"):
            st.session_state.qcm = None
            st.session_state.summary = None
            st.rerun()
