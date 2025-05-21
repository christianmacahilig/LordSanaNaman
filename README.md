📝 Overview
This system is designed to assist students and faculty in accurately classifying research proposals according to their academic domain—CS or IT. By extracting keywords from key sections of the proposal (Title, Rationale, Objectives, Scope and Limitations), and applying a scoring formula, the system determines the most relevant classification. It enhances evaluation accuracy, reduces subjectivity, and supports faster review processes.

⚙️ Features
Automated Classification using weighted keyword analysis

Section-Based Scoring with normalization for fair evaluation

User Course Matching to detect classification mismatches

Visual Checklist Results for clarity and feedback

High Accuracy (97.5%) based on testing and validation

📌 How It Works
User Selects Course

On the homepage, users choose between CS or IT.

This serves as a benchmark for comparison with the system's output.

Proposal Submission

Users input the text from their research proposal including the Title, Rationale, Objectives, and Scope.

Keyword Extraction & Scoring

The system identifies keywords based on a curated list from CHED/IEEE.

Scores are calculated per section:

Title: SUM(keywords) × (25 / 50)

Rationale + Objectives + Scope: SUM(keywords) × (25 / 250)

Classification & Match Check

The system sums the scores for CS and IT. The higher total determines the classification.

The result is compared with the user's selected course to determine a match or mismatch.

Checklist Display

The result page shows which sections align with CS or IT, based on scoring.

Helps users identify areas needing alignment or revision.

