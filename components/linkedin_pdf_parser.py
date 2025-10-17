import pdfplumber
import re
from statistics import mean

def extract_linkedin_info(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)

        # Split and clean lines
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        cleaned = [l for l in lines if not any(x in l.lower() for x in [
            "contact", "email", "linkedin.com", "page ", "resume"
        ])]

        # Defaults
        name, title, location = "N/A", "N/A", "N/A"
        summary, education, experience, skills = "", "", "", ""

        # --- Name: first proper two-word capitalized line ---
        for l in cleaned:
            if re.match(r"^[A-Z][a-z]+ [A-Z][a-z]+$", l):
                name = l
                break
        
        # -------------------------------------------------
        # 1️⃣  Detect name by largest font (≈26 pt)
        # -------------------------------------------------
        full_name = "N/A"
        largest_line = None
        largest_size = 0

        for page in pdf.pages:
            lines = {}
            for ch in page.chars:
                if not ch.get("text", "").strip():
                    continue
                top = round(ch["top"], 1)
                lines.setdefault(top, []).append(ch)

            for top, chars in lines.items():
                line_text = "".join(c["text"] for c in sorted(chars, key=lambda x: x["x0"])).strip()
                if not line_text:
                    continue
                avg_size = mean(c["size"] for c in chars)
                if avg_size >= 25:   # ~26pt name heuristic
                    full_name = line_text.strip()
                    break
            if full_name != "N/A":
                break  # stop after the first page with a valid name


        # --- Title: first line after name that contains common role words ---
        if name in cleaned:
            name_index = cleaned.index(name)
            for l in cleaned[name_index + 1 : name_index + 6]:
                if re.search(r"(engineer|developer|scientist|manager|analyst|designer|specialist)", l, re.I):
                    title = l
                    break

        # --- Location: find line containing region/city/country terms ---
        for l in cleaned:
            if any(k in l.lower() for k in [
                "area", "city", "usa", "united states", "california",
                "boston", "new york", "texas", "washington"
            ]):
                location = l
                break

        # --- Sections by headers ---
        text_lower = text.lower()
        def section_between(start, end=None):
            start_idx = text_lower.find(start)
            if start_idx == -1:
                return ""
            end_idx = text_lower.find(end) if end else None
            snippet = text[start_idx + len(start):end_idx].strip() if end_idx else text[start_idx + len(start):].strip()
            return re.sub(r"\n+", " ", snippet)

        summary = section_between("summary", "education")
        education = section_between("education", "experience")
        experience = section_between("experience", "skills")
        if not experience:
            experience = section_between("experience")

        # --- Skills: find known tech keywords ---
        tech_keywords = ["python","java","react","node","sql","docker","aws","kubernetes",
                         "javascript","typescript","machine learning","ai","flask","django","graphql"]
        found_skills = [kw.capitalize() for kw in tech_keywords if kw in text_lower]
        skills = ", ".join(sorted(set(found_skills)))

        return {
            "name": full_name.strip(),
            "title": title.strip(),
            "location": location.strip(),
            "summary": summary.strip(),
            "education": education.strip(),
            "experience": experience.strip(),
            "skills": skills.strip()
        }

    except Exception as e:
        print("Error parsing LinkedIn PDF:", e)
        return {
            "name": "N/A", "title": "N/A", "location": "N/A",
            "summary": "N/A", "education": "N/A",
            "experience": "N/A", "skills": "N/A"
        }
