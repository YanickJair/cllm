import spacy
from clm_core import TurnClassifier

nlp = spacy.load("en_core_web_sm")
classifier = TurnClassifier(nlp=nlp)

text = "I noticed my account was charged twice this month — one on the 2nd and another on the 3rd"
tt = classifier.classify(text=text)
print(tt)
