# components/LinkedinProfileFetcher.py
class LinkedInProfileFetcher:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def extract_profile(self):
        return {
            "name": "Sample Name",
            "title": "Software Engineer",
            "skills": ["Python", "Machine Learning"],
            "education": "M.S. Computer Science",
            "experience": ["Company A", "Company B"]
        }
