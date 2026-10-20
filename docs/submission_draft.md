# Submission Draft

**Working title:** KikuLog: Less Typing After a Day Among Chrysanthemums — Fine-Tuned with Tinker, Deployed on Render

**Status:** draft — fill in measured results before publishing.

---

## 1. The problem (personal experience)

*(Write in first person. Describe a specific day at work: tired after cutting, needing to log several houses.)*

---

## 2. What KikuLog does

*(Describe the note-to-journal flow. Mention the review step. Explain why each house needs independent tracking.)*

---

## 3. Before and after (demo walkthrough)

*(Reference the demo script. Include screenshots of the draft review and the agenda.)*

---

## 4. Why house context and plant stage matter

*(Explain the ambiguity problems: "opened" can mean two different plastic stages, "tilling" can be 1st or 2nd.
Explain how cycle context resolves this.)*

---

## 5. Dataset, base model, and fine-tuning

*(Describe the dataset: size, composition, split strategy, leakage prevention.
Name the base model and confirm its availability.
Describe the Tinker SFT run: LoRA rank, learning rate, epochs, batch size.
Do not include numbers that have not been measured.)*

---

## 6. Results, failures, and limitations

*(Fill in from evaluation/reports/ after the locked test run.
Include the event exact match score with numerator/denominator.
Show at least one failure example.
Describe what the model still gets wrong.)*

---

## 7. Role of Tinker and Render

**Tinker:** *(Describe the actual training run. Include checkpoint ID and dataset hash.)*

**Render:** *(Describe the deployed web service. Include the live URL.)*

---

## 8. Why an open-weight model

- Terminology can be adjusted by adding examples in the language actually used.
- Evaluation is reproducible: same dataset, same script, same seed.
- Weight portability depends on base model license (see docs/model_card.md).

---

## 9. How to run it

```bash
git clone https://github.com/<username>/kikulog.git
cd kikulog
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your values
uvicorn app.main:app --reload
```

Evaluation:
```bash
python evaluation/run_eval.py --baseline-model <id> --finetuned-model <id>
python evaluation/score.py --baseline <file> --finetuned <file> --output <file>
```

---

## 10. Categories, credits, and AI use

- **Best Use of Tinker** — fine-tuning run documented in `training/runs/`.
- **Best Use of Render** — deployment documented in `render.yaml` and live URL.
- Concept and domain knowledge: Andriyanto.
- Code assistance: *(disclose AI tool used and extent of use per hackathon rules).*
- Third-party libraries: listed in `requirements.txt` with their respective licenses.

---

**Do not publish until:**
- [ ] Real evaluation results are filled in (not "not yet tested").
- [ ] Tinker run ID and dataset hash are recorded.
- [ ] Live Render URL is confirmed.
- [ ] No company data or API keys are in the repository.
- [ ] Article follows the official submission template.
