from typing import Dict, List
from app.core.vector_store import vector_store
from app.schemas.jobs import JobResponse

class JobRecommender:
    """Match CVs with relevant jobs"""
        
    def calculate_skills_match(self, cv_skills: List[str], job_skills: List[str]) -> Dict:
        """Calculate skill overlap"""
        cv_skills_lower = [s.lower() for s in cv_skills]
        job_skills_lower = [s.lower() for s in job_skills]

        matched = [s for s in job_skills_lower if s in cv_skills_lower]
        missing = [s for s in job_skills_lower if s not in cv_skills_lower]

        score = len(matched) / len(job_skills_lower) if job_skills_lower else 0

        return {
            "score": round(score, 3),
            "matched_skills": matched,
            "missing_skills": missing
        }

    def calculate_experience_match(self, candidate_exp: int, required_years) -> float:
        """Calculate experience match score"""
        min_exp, max_exp = required_years

        if max_exp is None:
          if candidate_exp >= min_exp:
              return 1.0

        if min_exp <= candidate_exp <= max_exp:
            return 1.0

        elif candidate_exp < min_exp:
            return max(0, 1 - (min_exp - candidate_exp) / (min_exp))

        elif candidate_exp > max_exp:
            return max(0, 1 - (candidate_exp - max_exp) / (max_exp))


    def calculate_education_match(self, cv_education: List[Dict], required_edu: dict) -> tuple:
        """Calculate education match with detailed explanation"""

        score = 0.0

        lines = []

        for edu in cv_education:
            institution = edu.get("institution", "")
            degree = edu.get("degree", "")
            field = edu.get("field", "")
            gpa = f"GPA: {edu['gpa']}" if edu.get("gpa") else ""
            start = edu.get("startDate") or ""
            end = edu.get("endDate") or ""
            date_range = f"{start} to {end}".strip() if start or end else ""
                
            line = " ".join(filter(None, [institution, degree, field, gpa, date_range]))
            lines.append(line)
            
        candidate_education = "\n".join(lines)

        required_degree = required_edu.get("required_degree", "")
        restriction = required_edu.get("degree_restriction", "")
        required_field = required_edu.get("required_field", "")

        job_parts = []

        if required_degree:
            degree_part = f"Required Degree {required_degree}"
            if restriction:
                degree_part += f" (Restriction: {restriction})"
            job_parts.append(degree_part)

        if required_field:
            job_parts.append(f"Required Field {required_field}")

        job_education = " ".join(job_parts)

        candidate_education_embeddings = vector_store.generate_embedding(candidate_education)
        job_education_embeddings = vector_store.generate_embedding(job_education)

        score = vector_store.cosine_similarity(candidate_education_embeddings, job_education_embeddings)

        return score

    def match_cv_to_jobs(self, cv_data: Dict, jobs: List[Dict], top_k: int = 10) -> List[Dict]:
        """Generate job recommendations for a CV"""
        try:
            recommendations = []
            semantic_scores = vector_store.find_similar_jobs_for_cv(
                    cv_id = cv_data['id'],
                    job_ids = [job['id'] for job in jobs]
                )
            
            for job in jobs:
                skills_match = self.calculate_skills_match(
                    cv_data.get('skills', []),
                    job.get('skills', [])
                )
                cv_years = cv_data.get("total_experience", 0)
                exp_score = self.calculate_experience_match(
                    cv_years,
                    job.get('experience_years', 0)
                )
                edu_score = self.calculate_education_match(
                    cv_data.get('education', []),
                    job.get('education_required', '')
                )

                semantic_scores = dict(semantic_scores)
                semantic_score = semantic_scores.get(job['id'], 0.0)

                match_score = (
                    0.45 * semantic_score +
                    0.30 * skills_match['score'] +
                    0.15 * exp_score +
                    0.10 * edu_score
                )
                print("Match Score:", match_score)

                explanation = self._generate_explanation(
                    match_score, skills_match, cv_years
                )
                job.pop('_sa_instance_state', None)
                recommendations.append({
                    "job" : JobResponse(**job),
                    "match_score": round(match_score, 3),
                    "matching_factors": {
                        "skills_match": round(skills_match['score'], 3),
                        "experience_match": round(exp_score, 3),
                        "education_match": round(edu_score, 3),
                        "semantic_similarity": round(semantic_score, 3)
                    },
                    "matched_skills": skills_match['matched_skills'],
                    "missing_skills": skills_match['missing_skills'],
                    "explanation": explanation
                })

            recommendations.sort(key=lambda x: x['match_score'], reverse=True)
            return recommendations[:top_k]
        except Exception as e:
            print("Error in matching CV to jobs:", str(e))
            return []
        
    def _generate_explanation(self, match_score: float, skills_match: Dict,
                            cv_years: int) -> str:
        """Generate human-readable explanation"""
        if match_score >= 0.9:
            return f"Excellent match with {len(skills_match['matched_skills'])} matching skills and {cv_years}+ years experience"
        elif match_score >= 0.7:
            return f"Strong match with {len(skills_match['matched_skills'])} core skills aligned"
        else:
            return f"Potential match but may need development in {len(skills_match['missing_skills'])} areas"
        

job_recommender = JobRecommender()