import docx
from docx import Document

def get_data(file_path):
    doc_obj=open(file_path,"rb")
    doc_reader=Document(doc_obj)
    data=""
    for p in doc_reader.paragraphs:
        data+=p.text+"\n"
    return data

speech=get_data(r"D:\REC\Word to text\sample.docx")

print(speech)