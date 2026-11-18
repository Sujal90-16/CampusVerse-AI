import csv
import random
from pathlib import Path

import joblib
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

BASE = Path(__file__).resolve().parent
DATA_DIR = BASE / "data"
DATA_DIR.mkdir(exist_ok=True)

# Synthetic student questions for initial model development
examples = {
    "attendance": [
        "What is my attendance percentage?",
        "How many classes can I miss?",
        "What is the minimum attendance requirement?",
        "How do I check my attendance?",
        "Can I sit in exams with low attendance?",
        "My attendance is below 75 percent",
        "How many lectures have I attended?",
        "Where can I see my attendance record?",
        "How can I improve my attendance?",
        "Is attendance compulsory for every subject?",
        "Will I be detained due to attendance?",
        "How do I apply for attendance correction?",
    ],
    "timetable": [
        "Show me my class timetable",
        "When is my next lecture?",
        "What classes do I have tomorrow?",
        "When does the college day start?",
        "Where can I find the weekly schedule?",
        "Has the class schedule changed?",
        "Which lecture is scheduled at 10 AM?",
        "What is my Monday timetable?",
        "Tell me my lab timings",
        "Is there a class on Saturday?",
        "When is my next practical class?",
        "Show today's lecture schedule",
    ],
    "assignments": [
        "When is my assignment deadline?",
        "How do I submit my assignment?",
        "Where can I find the homework?",
        "What is the last date for submission?",
        "I need details about my pending assignments",
        "Has the assignment been uploaded?",
        "Can I submit my assignment late?",
        "Show me the current assignments",
        "What topics are included in the assignment?",
        "How many assignments are pending?",
        "Where do I upload my project?",
        "Tell me the project submission date",
    ],
    "exams": [
        "When are my semester exams?",
        "Show me the examination timetable",
        "What is the exam date for mathematics?",
        "When will practical exams begin?",
        "Where can I download my admit card?",
        "What is the exam reporting time?",
        "Has the date sheet been released?",
        "When is the next internal test?",
        "What is the syllabus for the exam?",
        "How do I apply for a re-examination?",
        "Are exams postponed?",
        "Tell me the university exam schedule",
    ],
    "fees": [
        "How much college fee is pending?",
        "What is the last date to pay fees?",
        "How can I pay my semester fees?",
        "Where can I download my fee receipt?",
        "Is there a late fee fine?",
        "How do I apply for a fee refund?",
        "What is the hostel fee?",
        "Can I pay fees online?",
        "My fee payment failed",
        "Show me my payment status",
        "What is the tuition fee for this semester?",
        "How do I get a fee payment confirmation?",
    ],
    "results": [
        "When will semester results be declared?",
        "How can I check my result?",
        "Show me my examination marks",
        "What is my CGPA?",
        "Where can I download my marksheet?",
        "I want to apply for revaluation",
        "When will internal marks be uploaded?",
        "How do I calculate my percentage?",
        "Has the result been announced?",
        "What happens if I fail a subject?",
        "How can I check my back paper result?",
        "My marks are incorrect",
    ],
    "events": [
        "What events are happening on campus?",
        "When is the college fest?",
        "How do I register for a college event?",
        "Show upcoming workshops",
        "Are there any technical competitions?",
        "Where can I find club activities?",
        "When is the next cultural program?",
        "How can I join a student club?",
        "Is there a seminar this week?",
        "Tell me about upcoming sports events",
        "Where is the event venue?",
        "Can I volunteer for the college fest?",
    ],
    "general": [
        "Where is the college library?",
        "What are the library opening hours?",
        "How can I contact the administration office?",
        "Where is the computer science department?",
        "Who should I contact for help?",
        "What facilities are available in college?",
        "Where can I find the hostel office?",
        "How do I get my student ID card?",
        "What are the college office timings?",
        "Where is the campus canteen?",
        "How can I contact my faculty advisor?",
        "Tell me about the college campus",
    ],
}

# Add a few natural variations to each example.
prefixes = ["", "Please help me. ", "Can you tell me, ", "I want to know, "]
suffixes = ["", " please.", " for this semester.", " urgently."]

rows = []
for label, questions in examples.items():
    for question in questions:
        rows.append({"text": question, "label": label})
        rows.append({"text": random.choice(prefixes) + question + random.choice(suffixes), "label": label})

random.seed(42)
random.shuffle(rows)

dataset_path = DATA_DIR / "student_queries.csv"
with dataset_path.open("w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["text", "label"])
    writer.writeheader()
    writer.writerows(rows)

texts = [row["text"] for row in rows]
labels = [row["label"] for row in rows]

X_train, X_test, y_train, y_test = train_test_split(
    texts, labels, test_size=0.25, random_state=42, stratify=labels
)

model = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1, 2), strip_accents="unicode")),
    ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced"))
])

model.fit(X_train, y_train)

predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)

print(f"\nDataset saved: {dataset_path}")
print(f"Total examples: {len(rows)}")
print(f"Training examples: {len(X_train)}")
print(f"Testing examples: {len(X_test)}")
print(f"\nTest accuracy: {accuracy:.2%}")
print("\nClassification report:")
print(classification_report(y_test, predictions, zero_division=0))

model_path = BASE / "student_intent_model.joblib"
joblib.dump(model, model_path)
print(f"Trained model saved: {model_path}")

print("\nSample predictions:")
for question in [
    "How many classes can I miss?",
    "When is my mathematics exam?",
    "Show me my pending assignments",
    "How much fee do I need to pay?"
]:
    prediction = model.predict([question])[0]
    confidence = max(model.predict_proba([question])[0])
    print(f"{question} -> {prediction} ({confidence:.2%})")
