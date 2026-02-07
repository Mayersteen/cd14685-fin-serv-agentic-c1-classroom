# Risk Analyst Agent - Chain-of-Thought Implementation
# TODO: Implement Risk Analyst Agent using Chain-of-Thought prompting

"""
Risk Analyst Agent Module

This agent performs suspicious activity classification using Chain-of-Thought reasoning.
It analyzes customer profiles, account behavior, and transaction patterns to identify
potential financial crimes.

YOUR TASKS:
- Study Chain-of-Thought prompting methodology
- Design system prompt with structured reasoning framework
- Implement case analysis with proper error handling
- Parse and validate structured JSON responses
- Create comprehensive audit logging
"""

import json
import openai
from datetime import datetime, timezone
from typing import Dict, Any, List
from dotenv import load_dotenv

# TODO: Import your foundation components
#from foundation_sar import (
#    RiskAnalystOutput,
#    ExplainabilityLogger,
#    CaseData
#)

# # Handle imports for both Notebook execution and Pytest runner
# try:
#     # 1. Try relative import (Standard for Python packages/Pytest)
#     from .foundation_sar import RiskAnalystOutput, ExplainabilityLogger, CaseData
# except ImportError:
#     try:
#         # 2. Try explicit package import (Sometimes needed by Pytest from root)
#         from src.foundation_sar import RiskAnalystOutput, ExplainabilityLogger, CaseData
#     except ImportError:
#         # 3. Fallback for Jupyter Notebooks (When running directly inside src/)
#         from foundation_sar import RiskAnalystOutput, ExplainabilityLogger, CaseData

# Use the direct import since 'src' is now in your sys.path
try:
    from foundation_sar import RiskAnalystOutput, ExplainabilityLogger, CaseData, ComplianceOfficerOutput
except ImportError:
    from src.foundation_sar import RiskAnalystOutput, ExplainabilityLogger, CaseData, ComplianceOfficerOutput

# Load environment variables
load_dotenv()

class RiskAnalystAgent:
    """
    Risk Analyst agent using Chain-of-Thought reasoning.
    
    TODO: Implement agent that:
    - Uses systematic Chain-of-Thought prompting
    - Classifies suspicious activity patterns
    - Returns structured JSON output
    - Handles errors gracefully
    - Logs all operations for audit
    """
    
    def __init__(self, openai_client, explainability_logger, model="gpt-4"):
        """Initialize the Risk Analyst Agent
        
        Args:
            openai_client: OpenAI client instance
            explainability_logger: Logger for audit trails
            model: OpenAI model to use
        """
        # TODO: Initialize agent components
        self.client = openai_client
        self.logger = explainability_logger
        self.model = model
        
        # TODO: Design Chain-of-Thought system prompt
        self.system_prompt = """
        You are a Senior Financial Crime Risk Analyst with 20 years of experience in BSA/AML compliance. 
        Your job is to analyze financial cases and identify suspicious activity using Chain-of-Thought reasoning.

        You must follow this 5-STEP ANALYSIS FRAMEWORK (Think step-by-step):
        1. DATA REVIEW: Scan customer profile, account types, and transaction history.
        2. PATTERN RECOGNITION: Look for structuring, round-dollar amounts, velocity spikes, or inconsistent behavior.
        3. REGULATORY MAPPING: Map observed behaviors to specific predicate offenses (e.g., structuring -> 31 CFR 1010.100).
        4. RISK QUANTIFICATION: Assess the severity (volume, frequency, impact).
        5. CLASSIFICATION DECISION: Select the distinct classification based on evidence.

        You must output a VALID JSON object matching this schema exactly:
        {
          "classification": "Literal['Structuring', 'Sanctions', 'Fraud', 'Money_Laundering', 'Other']",
          "confidence_score": 0.0,
          "reasoning": "Step-by-step analysis summary (max 500 chars)",
          "key_indicators": ["list", "of", "specific", "flags"],
              "risk_level": "Literal['Low', 'Medium', 'High']"
            }

            CRITICAL RULES:
            - If you see transactions just below $10,000, verify if it is Structuring.
            - If you see rapid movement of funds, check for Layering.
            - Be concise in your reasoning but strictly follow the evidence.
            - Use a professional terminology and approach
        """

    def analyze_case(self, case_data) -> 'RiskAnalystOutput':  # Use quotes for forward reference
        """
        Perform risk analysis on a case using Chain-of-Thought reasoning.
        
        TODO: Implement analysis that:
        - Creates structured user prompt with case details
        - Makes OpenAI API call with system prompt
        - Parses and validates JSON response
        - Handles errors and logs operations
        - Returns validated RiskAnalystOutput
        """
        start_time = datetime.now(timezone.utc)

        try:
            prompt_data = self._format_case_for_prompt(case_data)

            response = self.client.chat.completions.create(
                model = self.model,
                messages = [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Analyze this case data:\n\n{prompt_data}"}
                ],
                temperature = 0.3,
                max_tokens = 1000
            )

            # 🔍 DEBUG: Check if response is valid
            if not response or not hasattr(response, 'choices') or not response.choices:
                print(f"❌ API ERROR: Response is empty or malformed.")
                print(f"   Raw Response: {response}")
                raise ValueError("OpenAI API returned an empty response (choices=None)")

            try:
                raw_content = response.choices[0].message.content
                json_str = self._extract_json_from_response(raw_content)
                result_json = json.loads(json_str)
                analysis_result = RiskAnalystOutput(**result_json)

            except Exception as e:
                raise ValueError(f"Failed to parse Risk Analyst JSON output: {e}")

            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000

            if self.logger:
                self.logger.log_agent_action(
                    agent_type = "RiskAnalyst",
                    action = "analyze_case",
                    case_id = case_data.case_id,
                    input_data = {"customer_id": case_data.customer.customer_id},
                    output_data = result_json,
                    reasoning = analysis_result.reasoning,
                    execution_time_ms = execution_time,
                    success = True
                )

            return analysis_result

        except Exception as e:

            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            error_message = f"JSON parsing failed: {str(e)}"
            if self.logger:
                self.logger.log_agent_action(
                    agent_type = "RiskAnalyst",
                    action = "analyze_case",
                    case_id = getattr(case_data, 'case_id', 'UNKNOWN'),
                    input_data = {"error_context": "Analysis failed"},
                    output_data = {},
                    reasoning = error_message,
                    execution_time_ms = execution_time,
                    success = False,
                    error_message = str(e)
                )

            raise e

    def _extract_json_from_response(self, response_content: str) -> str:
        """Extract JSON content from LLM response
        TODO: Implement JSON extraction that handles:
        - JSON in code blocks (```json)
        - JSON in plain text
        - Malformed responses
        - Empty responses
        """

        if not response_content:
            raise ValueError("No JSON content found in response")

        try:
            # 1. Handle Code Blocks (Strip Markdown)
            if "```" in response_content:
                # Split lines and remove any line that is just ``` or ```json
                lines = response_content.split('\n')
                clean_lines = [line for line in lines if not line.strip().startswith('```')]
                clean_content = '\n'.join(clean_lines)
            else:
                clean_content = response_content

            start_idx = clean_content.find('{')
            end_idx = clean_content.rfind('}') + 1

            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON content found")

            return clean_content[start_idx:end_idx]

        except json.JSONDecodeError as e:
            # Add context to the error so we can debug it in the logs
            print(f"❌ JSON Parse Error: {e}")
            print(f"   Raw Content Snippet: {response_content[:200]}...")
            raise ValueError(f"Failed to parse JSON from model response: {e}")

    # ==========================================================================================
    # Split into helper methods as required by tests (test_format_accounts, test_format_transactions)
    def _format_accounts(self, accounts) -> str:
        return "\n".join([
            f"- Account {acc.account_id} ({acc.account_type}): Current Balance ${acc.current_balance:,.2f} (Opened: {acc.opening_date})"
            for acc in accounts
        ])

    def _format_transactions(self, transactions: list) -> str:
        formatted_lines = []
        for i, tx in enumerate(transactions, 1):
            line = (f"{i}. {tx.transaction_date}: {tx.transaction_type} "
                    f"${float(tx.amount):,.2f} - {tx.description} - {tx.location}")
            formatted_lines.append(line)

        return "\n".join(formatted_lines)
    # ==========================================================================================

    def _format_case_for_prompt(self, case_data) -> str:
        """Format case data for the analysis prompt

        TODO: Create readable prompt format that includes:
        - Customer profile summary
        - Account information
        - Transaction details with key metrics
        - Financial summary statistics
        """
        c = case_data.customer

        total_credit = sum(float(t.amount) for t in case_data.transactions
            if t.transaction_type.lower() in ['credit', 'deposit'])

        total_debit = sum(float(t.amount) for t in case_data.transactions
            if t.transaction_type.lower() not in ['credit', 'deposit'])

        net_flow = total_credit - total_debit

        accounts_text = self._format_accounts(case_data.accounts)
        transactions_text = self._format_transactions(case_data.transactions)

        return f"""=== FINANCIAL CRIME CASE FILE ===

            1. CUSTOMER PROFILE
            Name: {c.name}
            ID: {c.customer_id}
            Risk Rating: {c.risk_rating}
            Occupation: {c.occupation}
            Age: {self._calculate_age(c.date_of_birth)} years old
    
            2. ACCOUNT SUMMARY
            {accounts_text}
    
            3. ACTIVITY METRICS
            Total Transactions: {len(case_data.transactions)}
            Total Inflow: ${total_credit:,.2f}
            Total Outflow: ${total_debit:,.2f}
            Net Flow: ${net_flow:,.2f}
    
            4. TRANSACTION LOG (Chronological)
            {transactions_text}
        """

    def _calculate_age(self, dob_str: str) -> int:
        """Helper to calculate age from DOB string (YYYY-MM-DD)"""
        try:
            dob = datetime.strptime(dob_str, "%Y-%m-%d")
            today = datetime.now()
            return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        except:
            return 0  # Fallback if date is invalid

# ===== PROMPT ENGINEERING HELPERS =====

def create_chain_of_thought_framework():
    """Helper function showing Chain-of-Thought structure
    
    TODO: Study this example and adapt for financial crime analysis:
    
    **Analysis Framework** (Think step-by-step):
    1. **Data Review**: What does the data tell us?
    2. **Pattern Recognition**: What patterns are suspicious?
    3. **Regulatory Mapping**: Which regulations apply?
    4. **Risk Quantification**: How severe is the risk?
    5. **Classification Decision**: What category fits best?
    """
    return {
        "step_1": "Data Review - Examine all available information",
        "step_2": "Pattern Recognition - Identify suspicious indicators", 
        "step_3": "Regulatory Mapping - Connect to known typologies",
        "step_4": "Risk Quantification - Assess severity level",
        "step_5": "Classification Decision - Determine final category"
    }

def get_classification_categories():
    """Standard SAR classification categories
    
    TODO: Use these categories in your prompts:
    """
    return {
        "Structuring": "Transactions designed to avoid reporting thresholds",
        "Sanctions": "Potential sanctions violations or prohibited parties",
        "Fraud": "Fraudulent transactions or identity-related crimes",
        "Money_Laundering": "Complex schemes to obscure illicit fund sources", 
        "Other": "Suspicious patterns not fitting standard categories"
    }

# ===== TESTING UTILITIES =====

def test_agent_with_sample_case():
    """Test the agent with a sample case
    
    TODO: Use this function to test your implementation:
    - Create sample case data
    - Initialize agent
    - Run analysis
    - Validate results
    """
    print("🧪 Testing Risk Analyst Agent")
    print("TODO: Implement test case")

if __name__ == "__main__":
    print("🔍 Risk Analyst Agent Module")
    print("Chain-of-Thought reasoning for suspicious activity classification")
    print("\n📋 TODO Items:")
    print("• Design Chain-of-Thought system prompt")
    print("• Implement analyze_case method")
    print("• Add JSON parsing and validation")
    print("• Create comprehensive error handling")
    print("• Test with sample cases")
    print("\n💡 Key Concepts:")
    print("• Chain-of-Thought: Step-by-step reasoning")
    print("• Structured Output: Validated JSON responses")
    print("• Financial Crime Detection: Pattern recognition")
    print("• Audit Logging: Complete decision trails")
