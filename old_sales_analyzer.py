import json
import os
from typing import Dict, List, Optional
from openai import OpenAI
import docx
import PyPDF2
import io

class SalesAnalyzer:
    def __init__(self):
        """Initialize the Sales Analyzer with OpenAI client."""
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4-turbo"
    
    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text content from uploaded files."""
        try:
            file_extension = file_path.lower().split('.')[-1]
            
            if file_extension == 'txt':
                with open(file_path, 'r', encoding='utf-8') as file:
                    return file.read()
            
            elif file_extension == 'docx':
                doc = docx.Document(file_path)
                return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            
            elif file_extension == 'pdf':
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                    return text
            
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
                
        except Exception as e:
            raise Exception(f"Error extracting text from file: {str(e)}")
    
    def analyze_transcript(self, transcript: str) -> Optional[Dict]:
        """Analyze sales transcript using OpenAI API."""
        try:
            system_prompt = """You are an expert sales coach and analyst. Analyze the provided sales call transcript and provide detailed coaching feedback.

Your analysis should include:
1. **Overall Performance Assessment** - A summary of how the sales rep performed
2. **Strengths Demonstrated** - What the rep did well
3. **Areas for Improvement** - Specific areas that need work
4. **Objection Handling Analysis** - How objections were addressed
5. **Questioning Technique Evaluation** - Quality of questions asked
6. **Closing Opportunities** - Moments where closing could have been attempted
7. **Specific Coaching Recommendations** - Actionable advice
8. **Next Steps and Follow-up Strategy** - What should happen next

Provide detailed, actionable insights that will help improve sales performance."""

            user_prompt = f"""Please analyze this sales call transcript and provide comprehensive coaching feedback:

{transcript}

Focus on:
- Customer needs and pain points identified
- Sales rep performance and technique
- How objections were handled
- Missed opportunities for improvement
- Clear recommendations for next steps

Provide a detailed analysis with specific examples from the conversation."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=10000
            )
            
            content = response.choices[0].message.content
            
            # Return content with token usage information
            result = {
                'content': content
            }
            
            if hasattr(response, 'usage') and response.usage:
                result['token_usage'] = {
                    'input_tokens': response.usage.prompt_tokens,
                    'output_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens,
                    'max_tokens_limit': 10000
                }
            
            return result
            
        except json.JSONDecodeError as e:
            raise Exception(f"Error parsing AI response: {str(e)}")
        except Exception as e:
            raise Exception(f"Error analyzing transcript: {str(e)}")
    
    def get_sentiment_analysis(self, text: str) -> Dict:
        """Get detailed sentiment analysis for specific text segments."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a sentiment analysis expert specializing in sales conversations. 
                        Analyze the sentiment and provide a rating from 1-5 (1=very negative, 5=very positive) 
                        and confidence score between 0 and 1. Respond with JSON format:
                        {"rating": number, "confidence": number, "explanation": "detailed explanation"}"""
                    },
                    {"role": "user", "content": text}
                ],
                response_format={"type": "json_object"},
                temperature=0.2
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                "rating": max(1, min(5, round(result.get("rating", 3)))),
                "confidence": max(0, min(1, result.get("confidence", 0.5))),
                "explanation": result.get("explanation", "No explanation provided")
            }
        except Exception as e:
            return {
                "rating": 3,
                "confidence": 0.0,
                "explanation": f"Error analyzing sentiment: {str(e)}"
            }
    
    def identify_objections(self, transcript: str) -> List[Dict]:
        """Identify and categorize customer objections."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a sales expert. Identify customer objections in the transcript.
                        For each objection, provide:
                        - type: category of objection (price, product, timing, authority, need, etc.)
                        - concern: the specific customer concern
                        - response: suggested way to address this objection
                        
                        Respond with JSON format: {"objections": [list of objection objects]}"""
                    },
                    {"role": "user", "content": f"Analyze this transcript for objections:\n\n{transcript}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=2000
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("objections", [])
            
        except Exception as e:
            return [{"type": "Error", "concern": f"Could not analyze objections: {str(e)}", "response": "Please review transcript manually"}]
    
    def extract_action_items(self, transcript: str) -> List[Dict]:
        """Extract action items and next steps from the conversation."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a sales process expert. Extract action items and next steps from the transcript.
                        For each action item, provide:
                        - task: specific task to be completed
                        - priority: High, Medium, or Low
                        - timeline: when this should be completed
                        - owner: who should complete this (sales rep, customer, team, etc.)
                        
                        Respond with JSON format: {"action_items": [list of action objects]}"""
                    },
                    {"role": "user", "content": f"Extract action items from this transcript:\n\n{transcript}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=2000
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("action_items", [])
            
        except Exception as e:
            return [{"task": f"Review transcript manually due to analysis error: {str(e)}", "priority": "High", "timeline": "ASAP", "owner": "Sales Rep"}]
