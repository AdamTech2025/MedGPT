# Medical CPT Code Analyzer

A Django-based web application that uses dual AI agents to analyze medical scenarios and provide accurate CPT codes for urinary system procedures.

## Features

- **Dual AI Agent Architecture**: Uses two AI agents for analysis and validation
- **First Agent (Analyzer)**: Analyzes medical scenarios using GPT-3.5 Turbo
- **Second Agent (Validator)**: Validates results using GPT-4o for higher accuracy
- **Modern UI**: Clean, responsive interface with clear input and output sections
- **Confidence Levels**: Provides confidence ratings for the suggested CPT codes

## Technical Stack

- **Backend**: Django 5.1.7
- **Data Processing**: Pandas 2.2.3
- **Excel Handling**: OpenPyXL 3.1.5
- **Environment Variables**: Python-dotenv 1.0.1
- **AI Integration**: OpenAI API 1.66.3
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
   .venv\Scripts\activate
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
   - First agent analyzes the scenario and suggests a CPT code
   - Second agent validates the first agent's suggestion
4. View the results, including:
   - CPT Code
   - Description
   - Detailed explanation
   - Confidence level

## Data Source

The application uses the `Urinery.xlsx` file in the `data` directory as its knowledge base for CPT codes related to urinary system procedures.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 