from flask import Flask, render_template, request, flash
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
#from spacy import en_core_web_sm
from string import punctuation
from heapq import nlargest

app = Flask(__name__)
app.secret_key = "manbearpig_MUDMAN888"

@app.route("/")
def index():
	flash("what's your name?")
	return render_template("index.html")

@app.route("/summarize", methods=['POST', 'GET'])
def summarize():
	text = str(request.form['name_input'])
	stopwords = list(STOP_WORDS)
	nlp = spacy.load('en_core_web_sm')
	doc = nlp(text)
	#tokens = [token.text for token in doc]
	word_freq = {}
	for word in doc:
		if word.text.lower() not in stopwords:
			if word.text.lower() not in word_freq.keys():
				if word.text not in word_freq.keys():
					word_freq[word.text] = 1
				else:
					word_freq[word.text] += 1
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
	summary = nlargest(select_len, sent_scores, key = sent_scores.get)
	final_sum = [ word.text for word in summary]
	summary = ' '.join(final_sum)
	print(summary)
	return render_template("index.html",output=summary)

if __name__ == '__main__':
 
    # run() method of Flask class runs the application
    # on the local development server.
    app.run(debug=True)