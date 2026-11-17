# Viva preparation — CampusVerse + SHAAN AI

## 60-second explanation
CampusVerse is a role-based campus portal built with React and FastAPI. It organizes campus events, notices, courses, timetable, attendance, assignments and examinations. SHAAN is the AI assistant layer. A locally trained TF-IDF + Logistic Regression model classifies the student's intent; the backend retrieves relevant campus records and, optionally, asks a configured Gemini model to phrase an answer. Uploaded public campus documents can be text-extracted and searched using TF-IDF similarity. The application uses password hashing, signed JWTs and server-side role checks.

## Likely questions

**1. Why separate frontend and backend?**  
The frontend handles interaction and presentation; the API centralizes business logic, validation, authentication and data access.

**2. What does the trained model do?**  
It classifies text into intents such as attendance, timetable, exam, assignment, event, notice, placement, facilities, policy, club or general. It does not generate the final response itself.

**3. What is TF-IDF?**  
Term Frequency–Inverse Document Frequency weights terms by their frequency in a text and how distinctive they are across the corpus. Here it represents query text for intent classification and document retrieval.

**4. Why Logistic Regression?**  
It is a lightweight supervised classifier that works well as a baseline with sparse TF-IDF features and provides class probabilities for a confidence threshold.

**5. Is this an LLM trained from scratch?**  
No. The project trains its own intent classifier. Optional Gemini is a separate pre-trained language model used for response generation.

**6. What is RAG in this build?**  
The backend extracts text from uploaded PDF/TXT/Markdown documents, chunks it, retrieves relevant passages by TF-IDF similarity, and can include them as context. This is a lexical retrieval baseline, not dense-vector RAG.

**7. How is security handled?**  
Passwords are hashed with scrypt and salted. JWTs authenticate requests. Server-side role dependencies protect faculty/admin routes, and students can only read their own attendance and submissions.

**8. What is the measured model performance?**  
On the included synthetic starter dataset, the current deterministic 25% stratified holdout scored about 0.81 accuracy. That is only a development baseline; it does not establish performance on real student queries.

**9. What are the limitations?**  
Demo academic data is not official, the intent dataset is synthetic, the retrieval is lexical, Gemini requires an API key, PostgreSQL migrations and college SSO are not included, and deployment has not been performed here.

**10. What would be the next production step?**  
Replace seed records with verified data, design PostgreSQL migrations, add rate limiting and account recovery, conduct privacy/security reviews, build a representative evaluation set, and deploy with HTTPS, managed secrets and backups.
