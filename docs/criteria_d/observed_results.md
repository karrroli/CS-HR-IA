| Test ID | Success Criterion | Description | Test Data | Observed Results |
|---|---|---|---|---|
| T-01 | SC-01 | Valid login | hr@gmail.com / hr12345 | Redirected to Dashboard; upload and keywords sections visible. |
| T-02 | SC-01 | Invalid password | hr@gmail.com / wrong123 | Error message shown: Invalid email or password. User stayed on login page. |
| T-03 | SC-01 | Empty login fields | empty email and password | Error message shown: Please enter both email and password. |
| T-06 | SC-02 | Upload with no file | no file selected | Error message shown: No file selected. |
| T-05 | SC-02 | Invalid file type | resume.pdf | Error message shown: only .txt files are allowed. File was not stored. |
| T-12 | SC-05 | Process with no candidates | no candidates uploaded | Error message shown: No candidates to process. App did not crash. |
| T-04 | SC-02 | Valid .txt upload | 01_Karolina_Nowak.txt | File accepted; candidate Karolina Nowak appears on dashboard. |
| T-12c | SC-05 | Process with no keywords | 1 candidate, 0 keywords | Error message shown: No keywords to match. |
| T-08 | SC-03 | Add keyword | Python | Keyword Python appears in the keyword list. |
| T-08b | SC-03 | Empty keyword (invalid) | empty string | Error message shown: Keyword cannot be empty. |
| T-07 | SC-08 | 10+ file uploads | 12 valid .txt files | 12 candidates present after bulk upload (expected 12). |
| T-11 | SC-05 | Match score displayed | 12 candidates + 5 keywords | Leaderboard shows 12 candidates with a match score next to each name. |
| T-13 | SC-06 | Sorting highest to lowest | top scores [('Karolina Nowak', '17'), ('Daniel Kim', '14'), ('Lucas Meyer', '12'), ('Isabella Garcia', '9'), ('Oliver Smith', '8')] | Leaderboard ordered descending. Top 5: [('Karolina Nowak', '17'), ('Daniel Kim', '14'), ('Lucas Meyer', '12'), ('Isabella Garcia', '9'), ('Oliver Smith', '8')] |
| T-14 | SC-07 | Final leaderboard | full workflow | Numbered leaderboard with 12 candidates and scores displayed correctly. |
| T-15 | SC-07 | Top 3 highlighted | >=4 scored candidates | Ranks 1, 2 and 3 are highlighted in green (top-three class). |
| T-09b | SC-04 | Duplicate keyword (invalid) | python (already have Python) | Error message shown: Keyword is already in the list. |
