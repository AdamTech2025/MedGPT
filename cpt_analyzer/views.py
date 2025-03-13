from django.shortcuts import render
from django.http import JsonResponse
from .agents import CPTAnalyzerAgent, CPTValidatorAgent
import json

def index(request):
    """Render the main page of the application"""
    return render(request, 'index.html')

def analyze_cpt(request):
    """
    Analyze a medical scenario and return the appropriate CPT code
    
    This view handles the AJAX request from the frontend, processes the
    medical scenario using both agents, and returns the results as JSON.
    """
    if request.method == 'POST':
        try:
            # Get the medical scenario from the request
            data = json.loads(request.body)
            scenario_text = data.get('scenario', '')
            
            if not scenario_text:
                return JsonResponse({'error': 'No scenario provided'}, status=400)
            
            # Initialize the agents
            analyzer_agent = CPTAnalyzerAgent()
            validator_agent = CPTValidatorAgent()
            
            # Get the analysis from the first agent
            analyzer_result = analyzer_agent.analyze_scenario(scenario_text)
            
            # Check if there was an error with the first agent
            if 'error' in analyzer_result:
                return JsonResponse({'error': analyzer_result['error']}, status=500)
            
            # Validate the result with the second agent
            validator_result = validator_agent.validate_cpt_code(scenario_text, analyzer_result)
            
            # Check if there was an error with the second agent
            if 'error' in validator_result:
                return JsonResponse({'error': validator_result['error']}, status=500)
            
            # Combine the results
            result = {
                'analyzer_result': analyzer_result,
                'validator_result': validator_result,
                'final_cpt_code': validator_result['cpt_code'],
                'final_description': validator_result['description'],
                'final_explanation': validator_result['explanation'],
                'confidence': validator_result['confidence']
            }
            
            return JsonResponse(result)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
