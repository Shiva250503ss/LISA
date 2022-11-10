from flask import Flask,render_template,request,flash
import textwrap

import torch

from transformers import BertForQuestionAnswering
model=BertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')

from transformers import BertTokenizer
tokenizer = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')

import os
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from heapq import nlargest
import docx
from docx import Document

app = Flask(__name__)
app.secret_key = "manbearpig_MUDMAN888"

@app.route("/")
def index():
    flash("whats your name?")
    return render_template("index.html")

@app.route("/summarize",methods=['POST','GET'])
def summarize():
    if request.method == "POST":
        result = request.files['file_input']
        result.save(result.filename)
    text = word2text(result.filename)
    stopwords = list(STOP_WORDS)
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)
    print(text)
    word_freq = {}
    for word in doc:
        if word.text.lower() not in stopwords:
            if word.text.lower() not in word_freq.keys():
                if word.text not in word_freq.keys():
                    word_freq[word.text]= 1
                else:
                    word_freq[word.text] += 1
    print(word_freq.values())
    max_freq = max(word_freq.values())
    for word in word_freq.keys():
        word_freq[word] = word_freq[word]/max_freq
    sentence_tok = [sent for sent in doc.sents]
    sent_scores = {}
    for sent in sentence_tok:
        for word in sent:
            if word.text.lower() in word_freq.keys():
                if sent not in sent_scores.keys():
                    sent_scores[sent] = word_freq[word.text.lower()]
                else:
                    sent_scores[sent] += word_freq[word.text.lower()]
    select_len = int(len(sentence_tok) * 0.3)
    summary = nlargest(select_len,sent_scores,key = sent_scores.get)
    final_sum = [word.text for word in summary]
    summary = ' '.join(final_sum)
    print(summary)
    return render_template("live.html",output=summary)

def word2text(file_path):
    doc_obj=open(file_path,"rb")
    doc_reader=Document(doc_obj)
    data=""
    for p in doc_reader.paragraphs:
        data+=p.text+"\n"
    return data

def answer_questions(question,answer_text):
    wrapper = textwrap.TextWrapper(width=80) 
    #bert_abstract = "We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations from Transformers. Unlike recent language representation models (Peters et al., 2018a; Radford et al., 2018), BERT is designed to pretrain deep bidirectional representations from unlabeled text by jointly conditioning on both left and right context in all layers. As a result, the pre-trained BERT model can be finetuned with just one additional output layer to create state-of-the-art models for a wide range of tasks, such as question answering and language inference, without substantial taskspecific architecture modifications. BERT is conceptually simple and empirically powerful. It obtains new state-of-the-art results on eleven natural language processing tasks, including pushing the GLUE score to 80.5% (7.7% point absolute improvement), MultiNLI accuracy to 86.7% (4.6% absolute improvement), SQuAD v1.1 question answering Test F1 to 93.2 (1.5 point absolute improvement) and SQuAD v2.0 Test F1 to 83.1 (5.1 point absolute improvement)."
    print(wrapper.fill(answer_text))
    input_ids = tokenizer.encode(question,answer_text)
    print('Query has {:,} tokens.\n'.format(len(input_ids)))
    sep_index = input_ids.index(tokenizer.sep_token_id)
    num_seg_a = sep_index + 1
    num_seg_b = len(input_ids) - num_seg_a
    segment_ids = [0]*num_seg_a + [1]*num_seg_b
    assert len(segment_ids) == len(input_ids)
    outputs = model(torch.tensor([input_ids]),token_type_ids=torch.tensor([segment_ids]),return_dict=True)
    start_scores = outputs.start_logits
    end_scores = outputs.end_logits
    answer_start = torch.argmax(start_scores)
    answer_end = torch.argmax(end_scores)
    answer_end = torch.argmax(end_scores)
    tokens = tokenizer.convert_ids_to_tokens(input_ids)
    answer = tokens[answer_start]
    for i in range(answer_start + 1, answer_end + 1):
        if tokens[i][0:20] == '##' :
            answer += ' ' + tokens[i]
        else:
            answer += ' ' + tokens[i]
    print('Answer: '+ answer + "")
    return answer

@app.route("/answer_question",methods=['GET','POST'])
def answer_question():

    input = str(request.form['name_input'])
    bert_abstract = "Social engineering is the process of convincing an authorized individual to provide confidential information or access to an unauthorized individual.  It is a technique in which the attacker uses various deceptive practices to convince the targeted person to divulge information they normally would not divulge or to convince the target of the attack to do something they normally wouldn’t do. Social engineering is very successful for two general reasons. The first is the basic desire of most people to be helpful. When somebody asks a question for which we know the answer, our normal response is not to be suspicious but rather to answer the question."

    answer = answer_questions(input,bert_abstract)
    print(answer)
    return answer

#speech=get_data(r"D:\REC\Word to text\sample.docx")
@app.route("/live", methods=['GET','POST'])
def live():
    return render_template("live.html")

if __name__ == '__main__':
 
    # run() method of Flask class runs the application
    # on the local development server.
    app.run(debug=True)

