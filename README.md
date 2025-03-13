# Medical CPT Code Analyzer

A Django-based web application that uses dual AI agents to analyze medical scenarios and provide accurate CPT codes for urinary system procedures.

## Features

- **Dual AI Agent Architecture**: Uses two AI agents for analysis and validation
- **First Agent (Analyzer)**: Analyzes medical scenarios using GPT-4 for high accuracy
- **Second Agent (Validator)**: Validates results using GPT-4 with specialized validation prompts
- **Modern UI**: Clean, responsive interface with clear input and output sections
- **Confidence Levels**: Provides confidence ratings for the suggested CPT codes
- **Multiple CPT Code Support**: Handles complex scenarios requiring multiple codes with modifiers
- **Structured Guideline-Based Analysis**: Implements sequential CPT coding guidelines
- **Visual Enhancements**:
  - Highlighted modifiers for better visibility
  - Numbered guidelines in explanations
  - Styled output for multiple CPT codes
- **Information Requests**: Identifies when more information is needed and provides specific queries

## Structured CPT Coding Guidelines

The application follows these structured guidelines in sequence for CPT coding:

1. **Break Down the Scenario into Distinct Procedures**: Identifies each individual procedure performed and anatomical locations
2. **Match Each Procedure to the Most Specific CPT Code**: Selects codes that accurately describe each procedure
3. **Identify When Multiple Codes Are Necessary**: Determines when distinct procedures require separate codes
4. **Apply Modifiers for Special Circumstances**: Uses modifiers like -51 (multiple procedures), -59 (distinct procedures), and -50 (bilateral)
5. **Check for Bundled Services**: Avoids reporting services bundled into a more comprehensive code
6. **Sequence Multiple Codes Correctly**: Lists primary procedures first, followed by secondary procedures with modifiers
7. **Ensure Documentation Supports the Codes**: Verifies scenario provides enough detail to justify each code

## Technical Stack

- **Backend**: Django 5.1.7
- **Data Processing**: Pandas 2.2.3
- **Excel Handling**: OpenPyXL 3.1.5
- **Environment Variables**: Python-dotenv 1.0.1
- **AI Integration**: OpenAI API 1.66.3 (GPT-4)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd Medical\ urinary\ system
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv .venv
   # On Windows
   .venv\Scripts\activate.bat
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your OpenAI API key:
   - Create a `.env` file in the project root
   - Add your OpenAI API key: `OPENAI_API_KEY=your_api_key_here`

5. Run the development server:
   ```
   python manage.py runserver
   ```

6. Access the application at `http://127.0.0.1:8000/`

## Usage

1. Enter a detailed medical scenario describing a urinary system procedure
2. Click "Analyze Scenario"
3. The system will process the scenario using two AI agents:
   - First agent analyzes the scenario and suggests CPT code(s)
   - Second agent validates the first agent's suggestion
4. If more information is needed, the system will display a specific query
5. View the results, including:
   - CPT Code(s) with any applicable modifiers highlighted
   - Description
   - Detailed explanation addressing each guideline in sequence
   - Confidence level
   - List of coding guidelines applied

## Example Scenarios

### Simple Scenario
"Patient underwent a simple cystometrogram to evaluate bladder function."
- Expected result: CPT code 51725 (Simple cystometrogram)

### Complex Scenario
"Patient underwent a complex cystometrogram with voiding pressure studies and urethral pressure profile. Additionally, electromyography was performed during the study."
- Expected result: CPT code 51729 (Complex cystometrogram with voiding pressure studies and urethral pressure profile) and 51797-51 (Voiding pressure studies, intra-abdominal)

### Bilateral Procedure
"Patient underwent bilateral ureteral stent removal via cystoscopy."
- Expected result: CPT code 52310-50 (Cystourethroscopy, with removal of foreign body, calculus, or ureteral stent from urethra or bladder; simple, bilateral)

## Data Source

The application uses the `Urinery.xlsx` file in the `data` directory as its knowledge base for CPT codes related to urinary system procedures.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 