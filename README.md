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

SYSTEM OVERVIEW

![1_HOMEPAGE](https://github.com/user-attachments/assets/80b83d33-dd80-4802-84b1-10ae799e460b)
![2_UPLOAD FILE](https://github.com/user-attachments/assets/728afc0b-407f-4350-bab2-3f20bb72b165)
![3_CHECKLIST RESULTS](https://github.com/user-attachments/assets/6d93611f-292f-4783-a671-7efe43d56f78)
![4_CONCLUSION](https://github.com/user-attachments/assets/4eac815f-a192-4b99-8412-b0937b6353de)






