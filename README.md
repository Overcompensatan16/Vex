My goal is to develop a personal AI personal assistant with a comprehensive mix between personality levels like Neuro-sama (not traits), hyper intelligence and data scanning, and being able to switch systems through networks and IOT whenever, while using NASA’s Power of 10 rules for developing safety critical code, because I can control the structure and auditability easier without a slog of debugging at every step. 

## Usage
run 'main.py' with Python 3.8+ and use 'Facts.txt' input file, for now

## Requirements
Standard Library so far. No external packages needed.

## Notes

This project was designed around NASA's Power of 10 Safety Standards

FILE DOWNLOADING UPDATE


FACT GENERATION OVERHAUL (Transformer-Assisted, Lightweight)

🔧 1. Sentence Preprocessing (Tokenizer: nltk, spacy, or tinybert)
Use:
python
CopyEdit
from nltk.tokenize import sent_tokenize
sentences = sent_tokenize(text)

➡️ Justification: no model inference, fast, proven.

🤖 2. Replace Regex with SPO Triplet Extractor (Tiny Transformer)
🔍 Use rebel-large or fine-tuned T5:
Model: Babelscape/rebel-large (110M, not LLM-size)


Task: turn sentence into one or more SPO triplets


Example usage:
python
CopyEdit
from transformers import pipeline
extractor = pipeline("text2text-generation", model="Babelscape/rebel-large")
output = extractor(f"extract relations: {sentence}")[0]['generated_text']

Then post-process output into:
python
CopyEdit
{
  "subject": "...",
  "predicate": "...",
  "value": "...",
}

➡️ One pass per sentence. Skip if sentence is too short.

🧠 3. Light NER Tagging (Transformer NER)
Use:
python
CopyEdit
ner = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")
entities = ner(sentence)

Map entity_group to topic tags:
ORG, MISC → science, tech


PER, LOC → history, geography


Update tags list accordingly.

📚 4. Type Inference (Topic from Entities/Keywords)
python
CopyEdit
if not rec["type"]:
    for k, words in TOPIC_KEYWORDS.items():
        if any(w in sentence.lower() for w in words):
            rec["type"] = k
            break

But also boost based on:
Entity tags


Subject text content



🚦 5. Avoid "general" flood
If rec["type"] == "fact" and not rec["tags"], assign "general".
Track ratio of "general" facts vs. total — log warning if >80%.

⚙️ Model Summary (All Below LLM-Threshold)
Purpose
Model
Size
Role
Sentence tokenizing
nltk / spacy
-
Sentence splitting
SPO Extraction
Babelscape/rebel-large
~110M
Subject–predicate–object triples
NER Tagging
dslim/bert-base-NER
~110M
Lightweight named entity tagging

No GPT, no LLaMA, no LLMs — all sub-150M and offline runnable.

✅ Final Output
Each generate_facts(text) call now:
Breaks paragraph to sentences


Runs SPO extractor on each


Classifies fact type via lightweight tags + keyword match


Emits structured, tagged, route-ready facts






🧪 3. TESTING + EVALUATION
✅ Write unit tests:
For:
extract_spo(text)


generate_from_language()


generate_facts(text) using Wikipedia paragraphs and ArXiv abstracts


✅ Add test samples:
https://en.wikipedia.org/wiki/Number_theory


https://en.wikipedia.org/wiki/Organic_chemistry


https://en.wikipedia.org/wiki/Indian_philosophy


ArXiv physics.bio-ph summary



📁 4. CODE ORGANIZATION
🧼 Modularize:
Move extract_spo(), tagging, and keyword maps to a fact_utils.py or fact_nlp.py


Separate chemistry tag logic into chemistry_classifier.py




SUBJECT PARSERS

STANDARD PARSER INTERFACE
Each parser module should export:
python
CopyEdit
def parse_<domain>_text(text: str) -> List[Dict[str, Any]]:
    # Structured fact dicts
    return [{
        "subject": "...",
        "predicate": "...",
        "value": "...",
        "tags": ["<domain>"],
        "confidence": 0.9,
    }]

Integrated into generate_facts() via loop:
python
CopyEdit
for parser in all_subject_parsers:
    facts.extend(parser(sentence))


🔬 CORE SCIENCE PARSERS
1. physics_parser.py
Covers: astrophysics, quantum, optics, etc.
 Detects: laws, constants, principles, physical quantities
 Patterns: "<X> states that <Y>", "The <law> describes..."

2. math_parser.py
Covers: algebra, geometry, number theory, etc.
 Detects: definitions, theorems, equations
 Patterns: "<term> is defined as...", "Theorem: <statement>"

3. chemistry_parser.py ✅ (already exists)
Covers: compounds, reactions, periodic elements
 Detects: formulas, naming patterns, reaction types

4. bio_parser.py
Covers: biology, physiology, genetics, neuroscience
 Detects: structures, processes, systems
 Patterns: "X is part of Y", "X regulates Y"

5. environment_parser.py
Covers: ecology, climate, sustainability
 Detects: processes (e.g., carbon cycle), systems (biosphere), regulations
 Patterns: "X affects Y", "The ecosystem includes..."

6. conservation_parser.py
Covers: wildlife, endangered species, protection methods
 Detects: organizations (WWF, IUCN), species protection status
 NER: conservation orgs, species names, treaties














🧠 ABSTRACT / SOCIAL SCIENCE PARSERS
7. philosophy_parser.py
Covers: ethics, epistemology, metaphysics
 Detects: abstract concepts, named philosophers, "is a branch of"
 Patterns: "X is the study of Y"


psychology_parser.py
🧠 Domain: Psychology
Covers:
Cognitive psychology


Behavioral psychology


Emotions, motivation


Mental disorders (DSM-5 terms)


Learning & memory theories


Detects:
"X is a mental disorder characterized by..."


"Y theory explains learning as..."


NER patterns:
Named psychologists (e.g., Freud, Piaget, Skinner)


Mental states (e.g., anxiety, motivation, memory)


Common terms: reinforcement, stimulus, therapy, unconscious, cognition


Example fact:
json
CopyEdit
{
  "subject": "Classical conditioning",
  "predicate": "is a learning process involving",
  "value": "association between a neutral stimulus and a stimulus that evokes a response",
  "tags": ["psychology"]
}


➕ Addendum: sociology_parser.py
🌐 Domain: Sociology
Covers:
Social structures and stratification


Race, gender, class


Culture and norms


Institutions (family, religion, education)


Sociological theories (e.g., functionalism, conflict theory)


Detects:
"X is a social institution that..."


"Y refers to the process of..."


NER patterns:
Group behavior terms: class, norms, roles, deviance


Founders and theorists: Durkheim, Weber, Marx


Theories: symbolic interactionism, functionalism


Example fact:
{
  "subject": "Socialization",
  "predicate": "is the process through which",
  "value": "individuals learn the norms and values of their society",
  "tags": ["sociology"]
}


8. history_parser.py
Covers: major events, leaders, time periods
 Detects: "X occurred in Y", "The Battle of Z..."
 NER: places, dates, names

9. geo_parser.py
Covers: rivers, countries, borders, continents
 Detects: "X is located in Y", "capital of"
 Sources: use infobox-friendly entries

10. law_parser.py
Covers: US Constitution, SCOTUS, federal laws
 Detects: "The First Amendment guarantees..."
 Tags: amendment, clause, act, decision

11. econ_parser.py
Covers: macroeconomics, markets, models, trade
 Detects: "Inflation is...", "GDP measures..."
 Patterns: definition + causal relationships

12. game_theory_parser.py
Covers: strategies, equilibrium, payoff matrices
 Detects: "Nash equilibrium is...", "dominant strategy"
 NER: Prisoner's Dilemma, zero-sum

💻 COMPUTING / ENGINEERING PARSERS
13. cs_parser.py
Covers: AI, ML, cryptography, programming, HCI
 Detects: model types, algorithmic patterns
 NER: Transformer, SHA-256, gradient descent

14. stats_parser.py
Covers: probability, regression, inference
 Detects: statistical laws, distributions, test types
 NER: Bayes, mean, standard deviation

15. eess_parser.py
Covers: signal processing, hardware systems
 Detects: "X amplifies Y", "A circuit performs..."

🗃️ Summary: Parsers to Implement
Parser File
Domain Focus
physics_parser.py
Classical & quantum physics
math_parser.py
All math branches
chemistry_parser.py
Chemical facts & formulas
bio_parser.py
Biology & physiology
environment_parser.py
Environmental science
conservation_parser.py
Wildlife & policy
philosophy_parser.py
Metaphysics, ethics
geo_parser.py
Geography, borders, places
history_parser.py
Timelines & historic events
law_parser.py
US Constitution, Supreme Court
econ_parser.py
Economics & finance
game_theory_parser.py
Game-theoretic strategies
cs_parser.py
AI, ML, software & crypto
stats_parser.py
Statistics & inference
eess_parser.py
Electrical Engineering & Systems




📦 Deployment Steps
Refactor generate_facts() and helpers as per above


Add test cases for generate_facts(), extract_spo(), and classify_fact()


Run your existing pipeline (manual_inspector.py, batch_scheduler.py) on a small dataset


Monitor output ratios — goal: <50% into general, >30% into target domains


Gradually expand topic tagging dictionary and refine SPO patterns



Update the following test script to print any warnings that are triggered during the execution of `generate_facts` or `tag_facts`, instead of ignoring them.

Ensure:
- Any warnings from the standard `warnings` module (e.g., DeprecationWarning, UserWarning) are captured.
- Each test prints a clear message if a warning was raised, including the warning message and where it came from.
- The structure of the current tests is preserved.
- Output still includes assert failures as normal, but also prints captured warnings even if the test passes.

Use `warnings.catch_warnings(record=True)` and `warnings.simplefilter("always")` to capture warnings during each test.

