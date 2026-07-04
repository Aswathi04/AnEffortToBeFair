import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash')
def explain_bias(metrics: dict, stage: str) -> str:
    approval_lines = '\n'.join(
        f'  - {group}: {rate*100:.1f}% approval rate'
        for group, rate in metrics['approval_rates'].items()
    )

    if stage == 'baseline':
        context = 'This is the ORIGINAL model trained on historical data before any fairness intervention.'
        task = 'Explain what these numbers mean for fair lending compliance and whether this model is safe to deploy.'
    else:
        context = 'This is the model AFTER adversarial debiasing has been applied.'
        task = 'Explain how much the fairness improved, what the remaining risk is, and whether this model is now safer to deploy.'

    prompt = f"""You are a fair lending compliance analyst writing a brief audit note.
{context}

Model metrics:
- Overall accuracy: {metrics['accuracy']*100:.1f}%
- Demographic parity gap: {metrics['demographic_parity_gap']:.3f}
  (0 = perfect fairness, 1 = maximum disparity)
- Equalized odds gap: {metrics['equalized_odds_gap']:.3f}
- Approval rates by group:
{approval_lines}

{task}

Write exactly 3 sentences. Use plain English, no jargon. Be specific about the numbers.
Start with a direct verdict: either 'This model shows significant bias' or 'This model meets fair lending standards'.
Do not use bullet points. Do not add a heading. Just the 3 sentences."""

    response = model.generate_content(prompt)
    return response.text.strip()