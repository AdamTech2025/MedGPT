import os
import pandas as pd
import openai
from django.conf import settings

# Load the Excel file with CPT codes
def load_cpt_data():
    """Load CPT codes data from Excel file"""
    try:
        excel_path = os.path.join('data', 'Urinery.xlsx')
        df = pd.read_excel(excel_path)
        return df
    except Exception as e:
        print(f"Error loading CPT data: {e}")
        return None

class CPTAnalyzerAgent:
    """Agent that analyzes medical scenarios and provides CPT codes"""
    
    def __init__(self):
        self.cpt_data = load_cpt_data()
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def analyze_scenario(self, scenario_text):
        """
        Analyze a medical scenario and return the appropriate CPT code
        
        Args:
            scenario_text (str): The medical scenario to analyze
            
        Returns:
            dict: Contains CPT code, description, and explanation
        """
        # Convert DataFrame to a format that can be included in the prompt
        if self.cpt_data is not None:
            cpt_codes_context = self.cpt_data.to_string(index=False)
        else:
            return {"error": "CPT data could not be loaded"}
        
        # Create a prompt for the OpenAI model
        prompt = f"""
        You are a medical coding expert specializing in CPT codes for urinary system procedures.
        
        MEDICAL SCENARIO:
        {scenario_text}
        
        AVAILABLE CPT CODES FROM DATABASE:
        {cpt_codes_context}
        
        Based on the medical scenario and the available CPT codes, determine the most appropriate CPT code.
        Follow these guidelines:
        1. Identify the specific procedure and anatomical location
        2. Match the procedure to the appropriate category
        3. Consider any modifiers or special circumstances
        4. Select the most specific code that matches the scenario
        
        Provide your response in the following format:
        CPT Code: [code]
        Description: [short description]
        Explanation: [detailed explanation of why this code is appropriate]
        """
        
        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a medical coding expert specializing in CPT codes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            # Extract the response
            result = response.choices[0].message.content
            
            # Parse the response to extract CPT code, description, and explanation
            lines = result.strip().split('\n')
            cpt_code = ""
            description = ""
            explanation = ""
            
            for line in lines:
                if line.startswith("CPT Code:"):
                    cpt_code = line.replace("CPT Code:", "").strip()
                elif line.startswith("Description:"):
                    description = line.replace("Description:", "").strip()
                elif line.startswith("Explanation:"):
                    explanation = line.replace("Explanation:", "").strip()
                    # Collect any additional lines as part of the explanation
                    explanation_index = lines.index(line)
                    if explanation_index < len(lines) - 1:
                        additional_explanation = "\n".join(lines[explanation_index + 1:])
                        explanation += " " + additional_explanation
            
            return {
                "cpt_code": cpt_code,
                "description": description,
                "explanation": explanation
            }
            
        except Exception as e:
            return {"error": f"Error analyzing scenario: {str(e)}"}


class CPTValidatorAgent:
    """Agent that validates CPT codes using GPT-4o"""
    
    def __init__(self):
        self.cpt_data = load_cpt_data()
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def validate_cpt_code(self, scenario_text, analyzer_result):
        """
        Validate the CPT code provided by the analyzer agent
        
        Args:
            scenario_text (str): The original medical scenario
            analyzer_result (dict): The result from the analyzer agent
            
        Returns:
            dict: Contains validated CPT code, description, explanation, and confidence
        """
        # Convert DataFrame to a format that can be included in the prompt
        if self.cpt_data is not None:
            cpt_codes_context = self.cpt_data.to_string(index=False)
        else:
            return {"error": "CPT data could not be loaded"}
        
        # Create a prompt for the OpenAI model
        prompt = f"""
        You are a senior medical coding expert specializing in CPT codes for urinary system procedures.
        Your task is to validate the CPT code provided by another agent.
        
        MEDICAL SCENARIO:
        {scenario_text}
        
        FIRST AGENT'S ANALYSIS:
        CPT Code: {analyzer_result.get('cpt_code', 'Not provided')}
        Description: {analyzer_result.get('description', 'Not provided')}
        Explanation: {analyzer_result.get('explanation', 'Not provided')}
        
        AVAILABLE CPT CODES FROM DATABASE:
        {cpt_codes_context}
        
        Carefully review the scenario and the first agent's analysis. Determine if the CPT code is correct.
        If it's correct, confirm it. If it's incorrect, provide the correct code.
        
        Follow these guidelines:
        1. Identify the specific procedure and anatomical location
        2. Match the procedure to the appropriate category
        3. Consider any modifiers or special circumstances
        4. Select the most specific code that matches the scenario
        
        Provide your response in the following format:
        CPT Code: [code]
        Description: [short description]
        Explanation: [detailed explanation of why this code is appropriate]
        Confidence: [High/Medium/Low] - your confidence in this code being correct
        """
        
        try:
            # Call OpenAI API with GPT-4o
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a senior medical coding expert specializing in CPT codes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=800
            )
            
            # Extract the response
            result = response.choices[0].message.content
            
            # Parse the response to extract CPT code, description, explanation, and confidence
            lines = result.strip().split('\n')
            cpt_code = ""
            description = ""
            explanation = ""
            confidence = ""
            
            for line in lines:
                if line.startswith("CPT Code:"):
                    cpt_code = line.replace("CPT Code:", "").strip()
                elif line.startswith("Description:"):
                    description = line.replace("Description:", "").strip()
                elif line.startswith("Explanation:"):
                    explanation = line.replace("Explanation:", "").strip()
                    # Collect any additional lines as part of the explanation
                    explanation_index = lines.index(line)
                    if explanation_index < len(lines) - 1 and not lines[explanation_index + 1].startswith("Confidence:"):
                        additional_explanation = "\n".join([l for l in lines[explanation_index + 1:] if not l.startswith("Confidence:")])
                        explanation += " " + additional_explanation
                elif line.startswith("Confidence:"):
                    confidence = line.replace("Confidence:", "").strip()
            
            return {
                "cpt_code": cpt_code,
                "description": description,
                "explanation": explanation,
                "confidence": confidence
            }
            
        except Exception as e:
            return {"error": f"Error validating CPT code: {str(e)}"} 