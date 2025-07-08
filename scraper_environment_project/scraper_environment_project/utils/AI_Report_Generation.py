import os
import requests
from dotenv import load_dotenv
from general_utils import find_latest_file
from pathlib import Path
from diff_batch_compressor import *

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
API_URL = os.getenv("GEMINI_API_URL")

HEADERS = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": API_KEY
}


def call_gemini(text: str) -> dict:
    """Send a prompt to the Gemini API"""
    prompt = f"""
Context:
{text}

Question:
Le contexte ci-dessous présente un diff mettant en évidence les changements dans la section principale d’une page web décrivant le REAFIE (Règlement sur l’encadrement d’activités en fonction de leur impact sur l’environnement). Ce diff reflète les différences entre la version récemment récupérée et la version précédente.

Sur la base de ces informations, veuillez rédiger un rapport clair et concis résumant les modifications apportées au REAFIE. Mettez en évidence ce qui a été ajouté, supprimé ou modifié, et soulignez toute implication réglementaire significative.

Si les changements sont purement éditoriaux ou n’affectent pas le règlement lui-même, veuillez répondre par : « Aucun changement réglementaire ce mois-ci. »
"""

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    response = requests.post(API_URL, headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()


def generate_batched_reafie_report(kb_folder: str = "../data/diffs", keyword: str = "REAFIE_html_diff_", token_limit: int = 10000) -> list[dict]:
    """Generates batched update reports based on diff file compression"""
    folder = Path(kb_folder)
    latest_file_path = find_latest_file(folder, keyword, extension=".txt")
    print(latest_file_path)

    with open(latest_file_path, "r", encoding="utf-8") as f:
        diff_lines = f.readlines()
        print("📄 Preview of the diff file:")
        for line in diff_lines[:20]:
            print(line.strip())

    changed_lines = extract_changed_lines(diff_lines)
    batches = batch_lines(changed_lines, token_limit=token_limit)

    results = []
    print(f"📦 Sending {len(batches)} compressed batch(es) to Gemini...")

    for i, batch in enumerate(batches, 1):
        print(f"🔹 Processing batch {i} with ~{estimate_tokens(batch)} tokens")
        response = call_gemini(batch)
        total_tokens = response.get("usageMetadata", {}).get("totalTokenCount", 0)
        print(f"📊 Tokens used for batch {i}: {total_tokens}")
        results.append((response, total_tokens))

    return results


# Example usage
result = generate_batched_reafie_report()

summaries = []
total_token_usage = 0

for res, token_count in result:
    try:
        text = res["candidates"][0]["content"]["parts"][0]["text"]
        summaries.append(text)
        total_token_usage += token_count
    except Exception as e:
        print(f"❌ Error parsing batch: {e}")



def summarize_global_outcome(batch_summaries: list[str]) -> str:
    full_summary = "\n\n".join(batch_summaries)

    prompt = f"""
    Voici les résumés d'analyse des lots extraits du diff du REAFIE. En te basant uniquement sur ce contenu, analyse s'il y a eu des changements qui ont un **impact réel sur la réglementation**.

    Si **aucune modification n'affecte la réglementation** (c'est-à-dire uniquement des changements éditoriaux, de formatage ou de liens), répond uniquement par :

    « Aucun changement réglementaire ce mois-ci. »

    Sinon, rédige un **rapport complet et structuré** présentant **tous les changements réglementaires détectés**. Pour chaque changement, indique :
    - Les **articles impactés**
    - Le **type de changement** (ajout, suppression, modification)
    - Les **implications réglementaires concrètes**
    - Toute **nouvelle exigence** ou **exemption** introduite

    N’inclus aucune partie des résumés initiaux dans la réponse. Résume uniquement ce qui a un **impact réglementaire**, de manière claire et synthétique.

    Voici les résumés batch par batch :

    {full_summary}
    """

    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    response = requests.post(API_URL, headers=HEADERS, json=payload)
    response.raise_for_status()

    summary_text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
    summary_tokens = response.json().get("usageMetadata", {}).get("totalTokenCount", 0)
    return summary_text, summary_tokens


for i, (res, token_count) in enumerate(result, 1):
    print(f"\n📝 Gemini response for batch {i}:\n")

    try:
        candidates = res.get("candidates", [])
        if not candidates:
            print("❌ No candidates returned.")
            print("Full response:", res)
            continue

        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            print("❌ No parts in candidate.")
            print("Full response:", res)
            continue

        print("✅", parts[0]["text"])


    except Exception as e:
        print(f"❌ Error parsing response for batch {i}: {e}")
        print("Raw response:", res)
print("\n📦 All batch responses collected. Generating global summary...\n")

global_summary, global_summary_tokens = summarize_global_outcome(summaries)
total_token_usage += global_summary_tokens


print("\n📢 Résumé général des changements réglementaires :\n")
print(global_summary)
print("\n📊 Total token usage (prompt + output):", total_token_usage, "tokens")
estimated_cost = (total_token_usage / 1_000_000) * 0.35  # for Gemini 1.5 Flash input
print(f"💰 Estimated cost (Gemini 1.5 Flash): ~${estimated_cost:.4f} USD")




















"""
Other prompts that can added and tested:
"This Chat should be used to Answer any questions concerning the REAFIE regulations (please refer to REAFIE.txt in the knowledge base). "
                         "Every time you generate a response, please also include the passage it refers to within the REAFIE regulations as well as its ID. "
Also please take into consideration other laws such as LQE, RAMHHS, LCMVF, LP, LEP, Loi sur les eaux navigables canadiennes (LENC, art. 5.1) and LENC when answering the questions. Do a web search for each prompt as well to check the relevancy of these other laws. 

This Chat should be used to Answer any questions concerning the REAFIE regulations (please refer to REAFIE.txt in the knowledge base). Every time you generate a response, please also include the passage it refers to within the REAFIE regulations as well as its ID. Also please take into consideration other laws such as LQE, RAMHHS, LCMVF, LP, LEP, Loi sur les eaux navigables canadiennes (LENC, art. 5.1) and LENC when answering the questions. Do a web search for each prompt as well to check the relevancy of these other laws. 

For all statements in the prompt related to the regulations, please ALWAYS state the passage it got the information from and refers to in any of these regulations/laws

Exemple parfaite:
Règlementation pertinente
Article 336, paragraphe 2° :

« Sont admissibles à une déclaration de conformité [...] les travaux suivants : la construction d’ouvrages temporaires nécessitant des remblais ou des déblais requis pour réaliser des travaux de construction ou d’entretien d’une infrastructure, d’un ouvrage, d’un bâtiment ou d’un équipement associé à une activité qui ne fait pas l’objet d’une autorisation ministérielle. »
Référence : Q-2, r. 17.1, art. 336 (2°)

Exception importante (toujours selon l’article 336) :

« Si l’ouvrage temporaire est un bassin de sédimentation dans une rive, il ne peut être situé dans un milieu humide. »
"""