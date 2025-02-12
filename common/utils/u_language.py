from common.utils.u_yaml import *
from common.comdata import CommonData
import os

def get_labels():
    label_path = os.path.join( CommonData.LANGUAGE_DIR,'label.yaml')
    labels = read_yaml_file(label_path) 
    
    return labels   

def get_label(labels,key):
    try:
        label = labels[key][labels['language']]
        return label
    except Exception:
        return key  


def get_texts():
    label_path = os.path.join( CommonData.LANGUAGE_DIR,'text.yaml')
    texts = read_yaml_file(label_path) 
    
    return texts   

def get_text(texts,key):
    try:
        text = texts[key][texts['language']]
        return text
    except Exception:
        return key  







