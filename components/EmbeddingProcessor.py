# components/EmbeddingProcessor.py

from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class EmbeddingProcessor:
    def __init__(self, model):
        self.model = model

    def find_top_roles(self, user_input, job_df, top_n=3):
        if 'Description' not in job_df.columns or 'Occupation' not in job_df.columns:
            raise ValueError("job_df must have 'Occupation' and 'Description' columns")

        user_embedding = self.model.encode(user_input, convert_to_tensor=False)
        job_embeddings = self.model.encode(job_df['Description'].tolist(), convert_to_tensor=False)

        similarities = cosine_similarity([user_embedding], job_embeddings)[0]
        top_indices = np.argsort(similarities)[-top_n:][::-1]

        top_roles = []
        for idx in top_indices:
            role = job_df.iloc[idx]['Occupation']
            score = round(float(similarities[idx]), 4)
            top_roles.append((role, score))

        return top_roles
