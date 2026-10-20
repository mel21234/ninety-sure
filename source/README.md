# Rebuilding questions.js

You only need this if you want to regenerate the question bank. You'll need Python 3 and Node.js.

1. Put the two datasets in `data/`:
   - `countries.json` from https://github.com/mledoze/countries
   - `PeriodicTableJSON.json` from https://github.com/Bowserinator/Periodic-Table-JSON
2. Run `python3 build.py`. It writes a new `questions.js`.

`curated.py` holds the hand-picked facts, history years and conversions. `original_questions.html` holds the first 67 questions.

Rebuilding reshuffles the order. If the game is already live, add new questions to the end of the existing `questions.js` instead, so past days stay the same.
