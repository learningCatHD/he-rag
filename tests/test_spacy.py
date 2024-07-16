import spacy
from spacy.matcher import Matcher

# Load the spacy model
nlp = spacy.load("en_core_web_sm")

# Define the text
text = "Hawaii is a state in the United States. Barack Obama served as the 44th president of the United States. The Louvre Museum is located in Paris, France."

# Process the text with spacy
doc = nlp(text)

# Initialize the matcher with the shared vocab
matcher = Matcher(nlp.vocab)

# Define patterns
patterns = [
    [{"POS": "PROPN"}, {"LEMMA": "be"}, {"POS": "DET", "OP": "?"}, {"POS": "NOUN"}],
    [{"POS": "PROPN"}, {"LEMMA": "serve"}, {"POS": "ADP"}, {"POS": "DET", "OP": "?"}, {"POS": "NOUN"}],
    [{"POS": "PROPN"}, {"LEMMA": "locate"}, {"POS": "ADP"}, {"POS": "PROPN"}]
]

# Add patterns to matcher
matcher.add("RELATION_PATTERNS", patterns)

# Find matches in doc
matches = matcher(doc)

# Extract and format the relations
relations = []
for match_id, start, end in matches:
    span = doc[start:end]
    relations.append((span[0].text, span[1].lemma_, " ".join([token.text for token in span[2:]])))

print(relations)
