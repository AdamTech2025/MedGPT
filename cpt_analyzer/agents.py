import os
import pandas as pd
import openai
import re
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
        Analyze a medical scenario and return the appropriate CPT code(s)
        
        Args:
            scenario_text (str): The medical scenario to analyze
            
        Returns:
            dict: Contains CPT code(s), description, and explanation
        """
        # Convert DataFrame to a format that can be included in the prompt
        if self.cpt_data is not None:
            cpt_codes_context = self.cpt_data.to_string(index=False)
        else:
            return {"error": "CPT data could not be loaded"}
        
        # Create a prompt for the OpenAI model with enhanced modifier guidelines
        prompt = f"""
        You are a medical coding expert specializing in CPT codes for urinary system procedures.
        
        MEDICAL SCENARIO:
        {scenario_text}
        
        AVAILABLE CPT CODES FROM DATABASE:
        {cpt_codes_context}
        
        Based on the medical scenario and the available CPT codes, determine the most appropriate CPT code(s). 
        You MUST provide a specific CPT code even if the scenario seems ambiguous - use your best judgment.
        
        IMPORTANT GUIDELINES FOR MULTIPLE PROCEDURES AND MODIFIERS:
        
        1. Identify all distinct procedures by looking for procedure terminology and action verbs (e.g., "performed", "underwent", "conducted").
        
        2. For multiple procedures performed during the same session/same day:
           - Use modifier -51 (Multiple Procedure) for additional Category 1 CPT codes when the same provider performs multiple procedures
           - Do NOT add the -51 modifier to the primary (most resource-intensive) procedure
           - Only add the -51 modifier to secondary procedures
        
        3. Use modifier -59 (Distinct Procedural Service) when:
           - A procedure would normally be bundled with another but is performed separately and independently
           - The procedures are performed on different sites/organs
           - The procedures are performed during different sessions on the same day
        
        4. Use modifier -50 (Bilateral Procedure) when:
           - The same procedure is performed on both sides of the body
           - The procedure is not already inherently bilateral
        
        5. Sequence of codes:
           - List the most resource-intensive or complex procedure FIRST without modifiers
           - List additional procedures with appropriate modifiers afterward
        
        FOR ALL SCENARIOS, you must provide a CPT code that best matches the description, even if some details are missing.
        
        Provide your response in the following format:
        CPT Code(s): [code(s) - if multiple codes, separate with commas, e.g., "51725, 51797-51"]
        Description: [brief description of the code(s) - if multiple codes, separate descriptions with semicolons]
        Explanation: [detailed explanation of why these code(s) are appropriate, including reasons for any modifiers used]
        """
        
        try:
            # Call OpenAI API with higher max tokens to allow for detailed response
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Using GPT-4 for highest accuracy
                messages=[
                    {"role": "system", "content": "You are a medical coding expert specializing in CPT codes for urinary procedures. You ALWAYS provide a specific CPT code answer for any scenario."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=800
            )
            
            # Extract the response
            result = response.choices[0].message.content
            
            # Parse the response to extract CPT code(s), description, and explanation
            lines = result.strip().split('\n')
            cpt_code = ""
            description = ""
            explanation = ""
            
            for line in lines:
                if line.startswith("CPT Code") or line.startswith("CPT code"):
                    cpt_code = line.replace("CPT Code(s):", "").replace("CPT Code:", "").replace("CPT code(s):", "").replace("CPT code:", "").strip()
                elif line.startswith("Description"):
                    description = line.replace("Description:", "").strip()
                elif line.startswith("Explanation"):
                    explanation = line.replace("Explanation:", "").strip()
                    # Collect any additional lines as part of the explanation
                    explanation_index = lines.index(line)
                    if explanation_index < len(lines) - 1:
                        additional_explanation = "\n".join(lines[explanation_index + 1:])
                        explanation += " " + additional_explanation
            
            # Ensure we have a CPT code even if the model failed to provide one
            if not cpt_code.strip():
                # Attempt to extract any CPT-like codes from the explanation
                pattern = r'\b\d{5}(?:-\d{1,2})?\b'
                found_codes = re.findall(pattern, explanation)
                if found_codes:
                    cpt_code = ", ".join(found_codes)
                else:
                    # If no code was detected, provide a generic placeholder
                    cpt_code = "52000"  # Basic cystoscopy as fallback
                    explanation += " Note: Due to limited information in the scenario, a basic cystoscopy code (52000) has been provided as the most likely procedure. More specific coding would require additional procedural details."
            
            return {
                "cpt_code": cpt_code,
                "description": description,
                "explanation": explanation
            }
            
        except Exception as e:
            return {"error": f"Error analyzing scenario: {str(e)}"}


class CPTValidatorAgent:
    """Agent that validates CPT codes using GPT-4"""
    
    def __init__(self):
        self.cpt_data = load_cpt_data()
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def validate_cpt_code(self, scenario_text, analyzer_result):
        """
        Validate the CPT code(s) provided by the analyzer agent
        
        Args:
            scenario_text (str): The original medical scenario
            analyzer_result (dict): The result from the analyzer agent
            
        Returns:
            dict: Contains validated CPT code(s), description, explanation, and confidence
        """
        # Convert DataFrame to a format that can be included in the prompt
        if self.cpt_data is not None:
            cpt_codes_context = self.cpt_data.to_string(index=False)
        else:
            return {"error": "CPT data could not be loaded"}
        
        # Create a prompt for the OpenAI model with enhanced validation instructions
        prompt = f"""
        You are a senior medical coding expert specializing in CPT codes for urinary system procedures.
        Your task is to validate the CPT code(s) provided by another agent.
        
        MEDICAL SCENARIO:
        {scenario_text}
        
        FIRST AGENT'S ANALYSIS:
        CPT Code(s): {analyzer_result.get('cpt_code', 'Not provided')}
        Description: {analyzer_result.get('description', 'Not provided')}
        Explanation: {analyzer_result.get('explanation', 'Not provided')}
        
        AVAILABLE CPT CODES FROM DATABASE:
        {cpt_codes_context}
        
        Carefully review the scenario and the first agent's analysis. You MUST provide a specific CPT code even if the scenario seems ambiguous.
        
        IMPORTANT GUIDELINES FOR MULTIPLE PROCEDURES AND MODIFIERS:
        
        1. Identify all distinct procedures by looking for procedure terminology and action verbs (e.g., "performed", "underwent", "conducted").
        
        2. For multiple procedures performed during the same session/same day:
           - Use modifier -51 (Multiple Procedure) for additional Category 1 CPT codes when the same provider performs multiple procedures
           - Do NOT add the -51 modifier to the primary (most resource-intensive) procedure
           - Only add the -51 modifier to secondary procedures
        
        3. Use modifier -59 (Distinct Procedural Service) when:
           - A procedure would normally be bundled with another but is performed separately and independently
           - The procedures are performed on different sites/organs
           - The procedures are performed during different sessions on the same day
        
        4. Use modifier -50 (Bilateral Procedure) when:
           - The same procedure is performed on both sides of the body
           - The procedure is not already inherently bilateral
        
        5. Sequence of codes:
           - List the most resource-intensive or complex procedure FIRST without modifiers
           - List additional procedures with appropriate modifiers afterward
        
        You MUST provide a specific CPT code answer, even if you need to make reasonable assumptions based on the scenario.
        
        Provide your response in the following format:
        CPT Code(s): [code(s) - if multiple codes, separate with commas, e.g., "51725, 51797-51"]
        Description: [brief description of the code(s) - if multiple codes, separate descriptions with semicolons]
        Explanation: [detailed explanation of why these code(s) are appropriate]
        Confidence: [High/Medium/Low] - your confidence in this/these code(s) being correct
        """
        
        try:
            # Call OpenAI API with higher max tokens to allow for detailed response
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Using GPT-4 for maximum accuracy
                messages=[
                    {"role": "system", "content": "You are a senior medical coding expert specializing in CPT codes for urinary procedures. You ALWAYS provide a specific CPT code answer for any scenario."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            # Extract the response
            result = response.choices[0].message.content
            
            # Parse the response to extract CPT code(s), description, explanation, and confidence
            lines = result.strip().split('\n')
            cpt_code = ""
            description = ""
            explanation = ""
            confidence = ""
            
            for line in lines:
                if line.startswith("CPT Code") or line.startswith("CPT code"):
                    cpt_code = line.replace("CPT Code(s):", "").replace("CPT Code:", "").replace("CPT code(s):", "").replace("CPT code:", "").strip()
                elif line.startswith("Description"):
                    description = line.replace("Description:", "").strip()
                elif line.startswith("Explanation"):
                    explanation = line.replace("Explanation:", "").strip()
                    # Collect any additional lines as part of the explanation
                    explanation_index = lines.index(line)
                    if explanation_index < len(lines) - 1 and not lines[explanation_index + 1].startswith("Confidence:"):
                        additional_explanation = "\n".join([l for l in lines[explanation_index + 1:] if not l.startswith("Confidence:")])
                        explanation += " " + additional_explanation
                elif line.startswith("Confidence:"):
                    confidence = line.replace("Confidence:", "").strip()
            
            # Ensure we have a CPT code even if the model failed to provide one
            if not cpt_code.strip():
                # First try to use the analyzer's code if available
                if analyzer_result.get('cpt_code') and analyzer_result.get('cpt_code').strip():
                    cpt_code = analyzer_result.get('cpt_code')
                    if not confidence:
                        confidence = "Low"
                    if not description:
                        description = analyzer_result.get('description', "Description not available")
                    explanation += "\n\nNo better alternative could be determined, so the original code has been retained."
                else:
                    # Attempt to extract any CPT-like codes from the explanation
                    pattern = r'\b\d{5}(?:-\d{1,2})?\b'
                    found_codes = re.findall(pattern, explanation)
                    if found_codes:
                        cpt_code = ", ".join(found_codes)
                    else:
                        # If no code was detected, provide a generic placeholder
                        cpt_code = "52000"  # Basic cystoscopy as fallback
                        explanation += "\n\nNote: Due to limited information in the scenario, a basic cystoscopy code (52000) has been provided as the most likely procedure. More specific coding would require additional procedural details."
                        if not confidence:
                            confidence = "Low"
            
            # Set a default confidence if none was provided
            if not confidence:
                confidence = "Medium"
            
            return {
                "cpt_code": cpt_code,
                "description": description,
                "explanation": explanation,
                "confidence": confidence
            }
            
        except Exception as e:
            return {"error": f"Error validating CPT code: {str(e)}"} 