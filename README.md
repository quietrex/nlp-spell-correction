# nlp-spell-correction system - (jupyter for the data pre-processing then spyder for the interface)
The spell-checking system consists of two main steps, which are error detection and error correction. Considering the advantages, using a dictionary alongside n-gram analysis may be a more robust method in detecting errors, especially when real word errors are involved. Moving on to error correction, the generation and ranking of the candidate words can be performed through an array of algorithms. Among methods such as rule-based method, neural networks, and n-gram analysis, edit-distance based methods may be a more parsimonious solution on this issue.  
	Moreover, with a simpler system, the results produced will also be more interpretable. In addition to that, the advantages offered by various libraries can be utilized by using a combination of the libraries. In this case, spacy may be used as the main NLP library. Meanwhile, by taking advantage of the greater customizability of both Keras and Tensorflow, they may be used to build spell-checking system tuned for the chosen domain.  

## How to run the spyder interface
```
Connect with spyder/ or any python related interfaces, run the main.py.
```

## How to run ipynb file

```bash
pip install -r requirement.txt
jupyter lab 
```

## How to make path changes

```
make changes to config.py if necessarily.
```

## Domain and dataset
The domain of the current project was chosen with the primary task-spell checking in mind so there must be sufficient amount of texts for model training and evaluation. Therefore, several scientific domains were considered, and the field of forensic psychology was chosen. The field of Psychology was chosen as it is a very language-driven field as the most direct way for individuals to express or explain their behaviours is through language communication. In other words, the theories, findings, or concepts are explained primarily in words. However, considering the fact that psychology is a broad field with different focus, the current project has decided to narrow the focus to forensic psychology. 
	After domain is chosen, research articles and books were considered as potential sources of datasets. As different sources were reviewed, textbooks about forensic psychology was deemed as the most appropriate source for dataset in comparison to journals and other online articles. The choice was decided based on the following factors: (1) The presentation of the texts and (2) The amount of information covered. As research articles have a much narrower focus, typically with only few research objectives, the amount of information covered in the field may not be sufficient. Additionally, the formatting of research articles may also vary following each publishers’ formatting. Meanwhile, textbooks often have a set format throughout the entire text, which makes the extraction of data much more efficient. Besides, textbooks are often written to cover wide variety of important topics in the field. Hence, textbooks are more likely to contain wider variety of information and contains higher amount of unique terminology of the field. In this case, a textbook on forensic psychology titled: “Handbook of forensic psychology” was chosen as the source of the dataset.
	This can be found from the corpus/book section.
	
## Limitations and future implications
Upon the implementation of the model, a limitation is noticed, which is the model’s inability in detecting errors that occur at the first word of the text. In this case, the way to overcome such issue is the addition of an empty space before and after each sentence in the corpus. By doing so, it will inform the model regarding the words often used for the beginning and the end of each sentence.   
	In addition to that, the n-gram approach of the current project can also be further improved. Although n-gram is language agnostic as it conducts spell-checking by computing similarity, the order of the n-grams is often not considered. In the current project, an assumption was made whereby all the errors occur at the second word of any bi-gram pair. However, in real life, the error may occur in any position. In this case, the position of the bi grams should be considered for the spell-checker to model real life errors. 
	Besides that, the current system can also be further enhanced in terms of the ranking of the suggestions. As the current system ranks the suggestions based purely on edit distance and probability score. In this case, the incorporation of parts of speech (POS) tagging may help to make the ranking more accurate. As POS can recognize the roles played by each word in a sentence, such contextual information about the corpus can complement the edit distance and probabilistic methods.  




