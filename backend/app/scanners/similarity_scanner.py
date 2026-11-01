from typing import Dict, Any, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Corpus of known template job descriptions frequently scraped or recycled by scam rings
KNOWN_TEMPLATE_CORPUS = [
    {
        "id": "tpl_msft_ai_intern",
        "title": "Microsoft AI / Machine Learning Summer Internship Notification",
        "text": "Congratulations! You have been selected for Microsoft AI Internship. Role: AI Research Intern. Responsibilities include building machine learning models, python development. Selection confirmed. Pay registration fee to secure onboarding kit and laptop.",
        "known_type": "Recycled Fake Internship Template"
    },
    {
        "id": "tpl_google_scholarship",
        "title": "Google Generation Scholarship Opportunity",
        "text": "Selected for Google Scholarship award of $10,000. Congratulations. Immediate confirmation required within 24 hours. Submit processing and courier fee via wire or gift card.",
        "known_type": "Recycled Fake Scholarship Template"
    },
    {
        "id": "tpl_data_entry_task",
        "title": "Daily Data Entry / SMS Sending Work From Home",
        "text": "Earn Rs 2000 to 5000 per day by copying and pasting text from home. No experience needed. 2 hours daily work on mobile. Deposit refundable security money to receive assignment sheet.",
        "known_type": "Task / Freelance Scam Template"
    }
]

def analyze_job_description_similarity(submitted_text: str) -> Dict[str, Any]:
    """
    Computes TF-IDF vector similarity between submitted opportunity text
    and known template corpus.
    """
    if not submitted_text or len(submitted_text.strip()) < 20:
        return {"matched": False, "highest_similarity": 0.0, "flags": []}
        
    corpus_texts = [item["text"] for item in KNOWN_TEMPLATE_CORPUS]
    all_texts = [submitted_text] + corpus_texts
    
    try:
        vectorizer = TfidfVectorizer(stop_words='english', max_features=500)
        tfidf_matrix = vectorizer.fit_transform(all_texts)
        
        # Cosine similarity between submitted text (index 0) and corpus items (index 1..)
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]
        
        max_idx = similarities.argmax()
        max_score = float(similarities[max_idx])
        matched_template = KNOWN_TEMPLATE_CORPUS[max_idx]
        
        flags = []
        if max_score >= 0.40:
            flags.append({
                "code": "RECYCLED_TEMPLATE_DETECTED",
                "severity": "high" if max_score > 0.65 else "moderate",
                "message": f"Potentially copied job description detected ({round(max_score * 100, 1)}% semantic match).",
                "detail": f"Significant textual overlap with known '{matched_template['known_type']}'. Scammers frequently recycle job descriptions from other campaigns."
            })
            
        return {
            "matched": max_score >= 0.40,
            "highest_similarity": round(max_score, 3),
            "similarity_percentage": round(max_score * 100, 1),
            "matched_template_title": matched_template["title"] if max_score >= 0.40 else None,
            "flags": flags
        }
    except Exception:
        return {"matched": False, "highest_similarity": 0.0, "flags": []}
