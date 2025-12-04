import spacy

from src.components._target import TargetExtractor


prompt = "Summarize this 30-minute customer call transcript briefly."

nlp: spacy.Language = spacy.load("en_core_web_sm")
extractor = TargetExtractor(nlp)

print(extractor.extract(prompt))
