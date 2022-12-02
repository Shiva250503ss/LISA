from flask import Flask,render_template,request,flash
import textwrap
import jinja2
import torch

from transformers import BertForQuestionAnswering
model=BertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')

from transformers import BertTokenizer
tokenizer = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')

from transformers import AutoModelWithLMHead, AutoTokenizer
from torch import tensor,argmax
from transformers import BertTokenizer
from transformers import BertForQuestionAnswering

tokenizer_q = AutoTokenizer.from_pretrained("mrm8488/t5-base-finetuned-question-generation-ap")
model_q = AutoModelWithLMHead.from_pretrained("mrm8488/t5-base-finetuned-question-generation-ap")
model_a = BertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
tokenizer_a = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')

import os
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from heapq import nlargest
import docx
from docx import Document

summarized_text = ""
text = ""
answer=""
input=""
summary=""

app = Flask(__name__)
app.secret_key = "manbearpig_MUDMAN888"

picFolder = os.path.join('static','pics')

app.config['UPLOAD_FOLDER'] = picFolder

@app.route("/")
def index():
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
    global summary
    summary = nlargest(select_len,sent_scores,key = sent_scores.get)
    final_sum = [word.text for word in summary]
    summary = ' '.join(final_sum)
    global summarized_text 
    summarized_text = summary
    print(summary)
    #answer 
    

    return render_template("live.html",output=summary)

def word2text(file_path):
    doc_obj=open(file_path,"rb")
    doc_reader=Document(doc_obj)
    data=""
    for p in doc_reader.paragraphs:
        data+=p.text+"\n"
    global text 
    text = data
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
        if tokens[i][0:20] == '' :
            answer += ' ' + tokens[i]
        else:
            answer += ' ' + tokens[i]
    print('Answer: '+ answer + "")
    return answer

def get_questions(context, max_length=64):
    qns=[]
    sentences=context.split('.')
    for sentence in sentences[:-1]:
        input_text = "answer: %s  context: %s </s>" % ('', sentence)
        features = tokenizer_q([input_text], return_tensors='pt')

        output = model_q.generate(input_ids=features['input_ids'], 
                   attention_mask=features['attention_mask'],
                   max_length=max_length)
        qns.append(tokenizer_q.decode(output[0]).replace('<pad> question: ','').replace('</s>',''))
    return qns
    
@app.route("/answer_question",methods=['GET','POST'])
def answer_question():
    global input
    input = str(request.form.get('question'))
    abstract = text
    global answer
    answer = answer_questions(input,abstract)
    print(answer)
    return render_template('live.html',output=summary,answer=answer,question=input)

@app.route("/question_generator",methods=['GET','POST'])
def question_generator():
    context_q_a = text
    print("\nGenerated Question and Answers",end='\n\n')
    question_q_a=list(set(get_questions(context_q_a)))
    answer_q_a=[]
    for qn in question_q_a:
        answer_q_a.append(answer_questions(qn,context_q_a))
    for i in range(len(question_q_a)):
        print('Qn.'+str(i+1)+'  '+question_q_a[i],sep='\n')
        print('Ans : '+answer_q_a[i],sep='\n',end='\n\n')
    length = len(answer_q_a)
    return render_template('live.html',question=input,output=summary, query = question_q_a,answer=answer)

#@app.route("/generate",methods=['GET','POST'])
#def generate():
    #context_q_a = text
    #print("\nGenerated Question and Answers",end='\n\n')
    #question_q_a=list(set(get_questions(context_q_a)))
    #answer_q_a=[]
    #for qn in question_q_a:
        #answer_q_a.append(answer_questions(qn,context_q_a))
    #for i in range(len(question_q_a)):
        #print('Qn.'+str(i+1)+'  '+question_q_a[i],sep='\n')
        #print('Ans : '+answer_q_a[i],sep='\n',end='\n\n')
    #length = len(answer_q_a)
    #return render_template('live.html',question=input,output=summary,solution=answer_q_a,query = question_q_a,answer=answer)





#speech=get_data(r"D:\REC\Word to text\sample.docx")
@app.route("/live", methods=['GET','POST'])
def live():
    return render_template("live.html")

@app.route("/home",methods=['GET','POST'])
def home():
    return render_template("index.html")

if __name__ == '__main__':
 
    # run() method of Flask class runs the application
    # on the local development server.
    app.run(use_reloader = True,  debug=True)

