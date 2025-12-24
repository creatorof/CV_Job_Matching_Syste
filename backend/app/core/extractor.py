from typing import Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from app.schemas.cvs import CVData
from app.core.config import settings

CV_CATEGORIES = [
    "Software Engineering",
    "Data Science & AI",
    "Product Management",
    "Design & UX",
    "Marketing & Sales",
    "Finance & Accounting",
    "Human Resources",
    "Customer Support",
    "Operations & Logistics",
    "Healthcare & Medical",
    "Education & Training",
    "Legal & Compliance",
    "Research & Development",
    "Other",]

class CVExtractor:
    """LLM-based CV information extraction"""

    def __init__(self, llm_model: str = "models/gemini-2.5-flash-lite"):
        self.llm = ChatGoogleGenerativeAI(
            model=llm_model,
            temperature=1.0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
        self.parser = PydanticOutputParser(pydantic_object=CVData)
        self.categories = CV_CATEGORIES

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert CV/Resume parser. Extract structured information from resumes.
            Be thorough but accurate. If information is not present, leave fields empty.

            {format_instructions}"""),
            ("user", "Extract information from this CV:\n\n{cv_text}")
        ])

    def extract(self, cv_text: str) -> CVData:
        """Extract structured data from CV text"""

        chain = self.prompt | self.llm | self.parser

        try:
            result = chain.invoke({
                "cv_text": cv_text,
                "format_instructions": self.parser.get_format_instructions()
            })

            cv_data = result.model_dump()
            cv_data['category'] = self._categorize_cv(cv_data, cv_text)
            return cv_data

        except Exception as e:
            print(f"Extraction error: {e}")
            return self._fallback_extraction(cv_text)

    def _categorize_cv(self, cv_data: Dict, cv_text: str) -> str:
        """
        Categorize CV using LLM with predefined categories
        
        Args:
            cv_data: Extracted CV data dictionary
            cv_text: Original CV text
        
        Returns:
            str: Category name
        """
        
        categories_str = "\n".join([f"- {cat}" for cat in self.categories])
        
        categorization_prompt = f"""Based on the following CV information, classify the candidate into ONE of these categories:
        {categories_str}
        CV Summary:
        - Skills: {', '.join(cv_data.get('skills', [])[:10])}
        - Work Experience: {cv_data.get('work', [])}

        Consider the candidate's:
        1. Primary skills and technical expertise
        2. Work experience and job titles
        4. Overall career focus

        Respond with ONLY the category name from the list above. No explanation needed.

        Category:"""

        try:
            response = self.llm.invoke(categorization_prompt)
            if response is None or not response.content:
                return "Other"
            category = response.content.strip()
            
            if category in CV_CATEGORIES:
                return category
            else:
                return "Other"
        except Exception as e:
            print(f"Categorization error: {e}")
            return "Other"


    def _fallback_extraction(self, cv_text: str) -> Dict:
        """Simple fallback extraction"""
        messages = [
            {"role": "system", "content": "Extract CV information as JSON. Include name, email, phone, skills, work experience, education."},
            {"role": "user", "content": cv_text}
        ]

        response = self.llm.invoke(messages)

        try:
            json_str = response.content.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            return json.loads(json_str)
        except:
            return {"name": "Unknown", "raw_text": cv_text}



cv_extractor = CVExtractor(settings.LLM_PROVIDER)
