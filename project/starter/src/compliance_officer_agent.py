# Compliance Officer Agent - ReACT Implementation  
# TODO: Implement Compliance Officer Agent using ReACT prompting

"""
Compliance Officer Agent Module

This agent generates regulatory-compliant SAR narratives using ReACT prompting.
It takes risk analysis results and creates structured documentation for 
FinCEN submission.

YOUR TASKS:
- Study ReACT (Reasoning + Action) prompting methodology
- Design system prompt with Reasoning/Action framework
- Implement narrative generation with word limits
- Validate regulatory compliance requirements
- Create proper audit logging and error handling
"""

import json
import openai
from datetime import datetime, timezone
from typing import Dict, Any, List
from dotenv import load_dotenv
from unittest.mock import MagicMock
import re

# # Implementation without module repetition.
# try:
#     # Relative import (e.g. from .foundation_sar)
#     from . import foundation_sar as sar
# except ImportError:
#     try:
#         # Package import (e.g. from src.foundation_sar)
#         from src import foundation_sar as sar
#     except ImportError:
#         # Direct import (e.g. import foundation_sar)
#         import foundation_sar as sar
#
# RiskAnalystOutput = sar.RiskAnalystOutput
# ExplainabilityLogger = sar.ExplainabilityLogger
# CaseData = sar.CaseData
# ComplianceOfficerOutput = sar.ComplianceOfficerOutput
# CustomerData = sar.CustomerData
# TransactionData = sar.TransactionData

# Use the direct import since 'src' is now in your sys.path
try:
    from foundation_sar import RiskAnalystOutput, ExplainabilityLogger, CaseData, ComplianceOfficerOutput, TransactionData, CustomerData
except ImportError:
    from src.foundation_sar import RiskAnalystOutput, ExplainabilityLogger, CaseData, ComplianceOfficerOutput, TransactionData, CustomerData

# Load environment variables
load_dotenv()

class ComplianceOfficerAgent:
    """
    Compliance Officer agent using ReACT prompting framework.
    
    TODO: Implement agent that:
    - Uses Reasoning + Action structured prompting
    - Generates regulatory-compliant SAR narratives
    - Enforces word limits and terminology
    - Includes regulatory citations
    - Validates narrative completeness
    """
    
    def __init__(self, openai_client, explainability_logger, model="gpt-4"):
        """Initialize the Compliance Officer Agent
        
        Args:
            openai_client: OpenAI client instance
            explainability_logger: Logger for audit trails
            model: OpenAI model to use
        """
        # TODO: Initialize agent components
        self.client = openai_client
        self.logger = explainability_logger
        self.model = model
        #pass
        
        # TODO: Design ReACT system prompt
        # ReACT System Prompt
        self.system_prompt = """
            You are a Senior AML Compliance Officer (ReACT Agent) for a major financial institution.
            Your task is to review a case file and the findings of a Risk Analyst, then draft a concise 
            Suspicious Activity Report (SAR) narrative in accordance with BSA/AML regulations.

            # INPUT CONTEXT
            You will receive a JSON object containing:
            1. Customer & Account Details
            2. Transaction History
            3. Risk Analyst Findings (Classification, Reasoning, Risk Level)

            # ReACT FRAMEWORK INSTRUCTIONS
            You must execute this task in two phases:

            ## PHASE 1: REASONING
            Analyze the data before writing. Ask yourself:
            1. What is the specific suspicious behavior? (e.g., Structuring, Layering)
            2. Which regulations apply? (e.g., 31 CFR 1020.320 for suspicious transactions, 12 CFR 21.11)
            3. What are the "Who, What, Where, When, Why"? 
            4. Are there mitigating factors? (If none, note that: "No apparent economic purpose")

            ## PHASE 2: ACTION
            Draft the narrative text strictly following these rules:
            - START with the date range and total suspicious amount.
            - BODY should detail the specific patterns (e.g., "Customer made 4 cash deposits...").
            - CONCLUSION should state the suspicion (e.g., "Activity appears structured to evade reporting requirements").
            - TONE: Strictly factual and objective. Exclude personal opinions and flowery language. State the facts and the specific basis for suspicion (e.g., "pattern is consistent with..."). 
            - DO NOT make recommendations or conclusions (e.g., NEVER say "warrant further investigation", "recommend review" or "should investigate").
            - LENGTH: Maximum 120 words.

            # OUTPUT FORMAT
            You must respond with a VALID JSON object matching this structure exactly:
            {
                "narrative_reasoning": "Brief explanation of your regulatory analysis",
                "regulatory_citations": ["List", "of", "Regulations"],
                "narrative": "The final SAR narrative text...",
                "completeness_check": true
            }
            
            narrative has a max word cound of 120 and a max character count of 1000
            narrative_reasoning has a max character count of 500
        """

    def generate_compliance_narrative(self, case_data, risk_analysis) -> 'ComplianceOfficerOutput':
        """
        Generate regulatory-compliant SAR narrative using ReACT framework.
        
        TODO: Implement narrative generation that:
        - Creates ReACT-structured user prompt
        - Includes risk analysis findings
        - Makes OpenAI API call with constraints
        - Validates narrative word count
        - Parses and validates JSON response
        - Logs operations for audit
        """
        start_time = datetime.now(timezone.utc)

        try:

            tx_summary = self._format_transactions_for_compliance(case_data.transactions)

            case_context = f"""
            CUSTOMER: {case_data.customer.name} (ID: {case_data.customer.customer_id})
            TRANSACTIONS:
            {tx_summary}
            
            """

            risk_context = self._format_risk_analysis_for_prompt(risk_analysis)

            full_prompt = f"{case_context}\n\n{risk_context}"

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.2,
                max_tokens=800
            )

            if not response or not hasattr(response, 'choices') or not response.choices:
                raise ValueError("OpenAI API returned an empty response")

            raw_content = response.choices[0].message.content
            json_str = self._extract_json_from_response(raw_content)
            result_dict = json.loads(json_str)

            narrative_text = result_dict.get("narrative", "")
            citations_list = result_dict.get("regulatory_citations", [])
            customer_name_val = case_data.customer.name
            risk_indicators_val = getattr(risk_analysis, 'key_indicators', [])

            validation = self._validate_narrative_compliance(
                narrative = narrative_text,
                citations = citations_list,
                customer_name = customer_name_val,
                risk_indicators=risk_indicators_val
            )

            # Raise ValueError for validation errors (Hard Fails) so unit tests pass
            if validation["errors"]:
                error_msg = f"Strict Regulatory Validation Failed. Errors: {validation['errors']}"
                raise ValueError(error_msg)

            # Log warnings (Soft Fails) but allow process to continue
            if validation["warnings"]:
                print(f"   ⚠️ Compliance Warnings: {validation['warnings']}")

            compliance_narrative = ComplianceOfficerOutput(**result_dict)
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000

            if self.logger:
                self.logger.log_agent_action(
                    agent_type="ComplianceOfficer",
                    action="generate_narrative",
                    case_id=case_data.case_id,
                    input_data={"risk_level": risk_analysis.risk_level},
                    output_data=result_dict,
                    reasoning=compliance_narrative.narrative_reasoning,
                    execution_time_ms=execution_time,
                    success=True
                )

            print("   ✅ Compliance Narrative Generated Successfully.")
            return compliance_narrative

        except ValueError as e:
            # Re-raise ValueError to satisfy unit tests (Word Count, JSON Parsing)
            print(f"   ❌ Validation/Parsing Error: {str(e)}")

            if self.logger:
                self.logger.log_agent_action(
                    agent_type="ComplianceOfficer",
                    action="generate_narrative_error",
                    case_id=case_data.case_id,
                    input_data={"customer_id": case_data.customer.customer_id},
                    output_data=None,
                    reasoning=f"JSON parsing failed: {str(e)}",  # Must include 'JSON parsing failed' for test
                    execution_time_ms=(datetime.now(timezone.utc) - start_time).total_seconds() * 1000,
                    success=False
                )

            raise e

        except Exception as e:

            error_msg = str(e)
            print(f"   ⚠️ Compliance Generation Failed: {error_msg}")
            print("   🔄 Switching to Fallback Narrative (Manual Review Stub)...")

            if self.logger:
                self.logger.log_agent_action(
                    agent_type="ComplianceOfficer",
                    action="generate_narrative_fallback",
                    case_id=case_data.case_id,
                    input_data={"customer_id": case_data.customer.customer_id},
                    output_data=None,
                    reasoning=f"Fallback triggered due to: {error_msg}",
                    execution_time_ms=(datetime.now(timezone.utc) - start_time).total_seconds() * 1000,
                    success=False
                )

            return self._generate_fallback_narrative(case_data, error_msg)


    def _generate_fallback_narrative(self, case_data, error_reason: str) -> 'ComplianceOfficerOutput':
        """
        Creates a safe, placeholder ComplianceOfficerOutput when the Agent fails.
        This ensures the pipeline continues to the next step (Human Review).
        """
        return ComplianceOfficerOutput(
            narrative_reasoning=f"AUTOMATED GENERATION FAILED. Error: {error_reason}. Proceeding to manual review.",
            regulatory_citations=["MANUAL_REVIEW_REQUIRED"],
            narrative=f"System Error: Unable to generate SAR narrative for Customer {case_data.customer.name}. Manual Compliance Officer review is required.",
            completeness_check=False
        )

    def _format_transactions_for_compliance(self, transactions: List[TransactionData]) -> str:
        """Helper to format transactions list for the prompt"""
        return "\n".join([
            f"{i}. {t.transaction_date}: ${t.amount:,.2f} {t.transaction_type} via {t.method} at {t.location}"
            for i, t in enumerate(transactions, 1)
        ])

    def _extract_json_from_response(self, response_content: str) -> str:
        """Extract JSON content from LLM response"""
        # REQUIRED PREFIX for 'test_json_parsing_error'
        error_prefix = "Failed to parse Compliance Officer JSON output"

        if not response_content:
            raise ValueError(f"{error_prefix}: No JSON content found")

        try:
            if "```" in response_content:
                lines = response_content.split('\n')
                clean_lines = [line for line in lines if not line.strip().startswith('```')]
                clean_content = '\n'.join(clean_lines)
            else:
                clean_content = response_content

            start_idx = clean_content.find('{')
            end_idx = clean_content.rfind('}') + 1

            if start_idx == -1 or end_idx == 0:
                raise ValueError(f"{error_prefix}: No JSON content found")

            return clean_content[start_idx:end_idx]

        except json.JSONDecodeError as e:
            raise ValueError(f"{error_prefix}: {e}")

    def _format_risk_analysis_for_prompt(self, risk_analysis) -> str:
        """Format risk analysis results for compliance prompt
        
        TODO: Create structured format that includes:
        - Classification and confidence
        - Key suspicious indicators
        - Risk level assessment
        - Analyst reasoning
        """
        return f"""
        
        RISK ANALYST RESULTS:
            - Classification and confidence: {risk_analysis.classification}
            - Key suspicious indicator: {', '.join(risk_analysis.key_indicators)}
            - Risk level assessment: {risk_analysis.risk_level}
            - Analyst reasoning: "{risk_analysis.reasoning}"
            
        """

    def _validate_narrative_compliance(self, narrative: str, citations: List[str], customer_name: str, risk_indicators: List[str] = None) -> Dict[str, Any]:
        """Validate narrative meets regulatory requirements
        
        TODO: Implement validation that checks:
        - Word count (≤120 words)
        - Required elements present
        - Appropriate terminology
        - Regulatory completeness
        """
        errors = []
        warnings = []

        # PROHIBITED PHRASES that lead to a hard fail
        # SARs must be objective. They cannot contain recommendations or subjective beliefs.
        prohibited_phrases = [
            "warrant further investigation",
            "recommend review",
            "should be investigated",
            "please investigate",
            "we believe",
            "i believe",
            "we feel",
            "i feel",
            "opinion is",
            "suggest checking",
            " i ",
            " we "
        ]

        lower_narrative = narrative.lower()
        for phrase in prohibited_phrases:
            if phrase in lower_narrative:
                errors.append(
                    f"Prohibited regulatory language found: '{phrase}' (Narratives must be factual, not advisory)"
                )

        # =========================================================================================================
        # REQUIRED ELEMENTS of FinCEN SAR (The '5 Ws') that are relevant in this context.
        # =========================================================================================================

        # WHO
        if customer_name not in narrative:
            warnings.append(f"Narrative missing subject identity: '{customer_name}'")

        # HOW MUCH
        # Must find at least one occurrence of $ followed by digits
        money_pattern = r'(\$\s?[\d,.]+|[\d,.]+\s?(?:USD|dollars?))'

        if not re.search(money_pattern, narrative, re.IGNORECASE):
            warnings.append("Narrative missing specific monetary amounts (e.g., '$9,000', '9000 USD')")

        # WHEN
        date_pattern = (
            r'\b('  # Start word boundary and group
            r'(?:19|20)\d{2}|'  # Years: 19xx or 20xx
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*|'  # Months (short or long)
            r'\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?'  # Dates: 1/1, 01-01-91, 1991-01-01
            r')\b'  # End word boundary
        )
        if not re.search(date_pattern, narrative, re.IGNORECASE):
            warnings.append("Narrative missing timeframe/dates (e.g., 'Jan 1991', '01/01/91')")

        # WHY: Connection to Risk Indicators
        indicators_found = False
        if risk_indicators:
            for indicator in risk_indicators:
                if indicator.lower() in lower_narrative:
                    indicators_found = True
                    break

            if not indicators_found:
                warnings.append(f"Narrative might not fully address specific risk indicators: {risk_indicators}")

        # =========================================================================================================
        # Checking Structure and Format
        # =========================================================================================================

        # Pass the STRING 'narrative' to the validator
        word_count = len(narrative.split())
        if word_count > 120:
            errors.append(f"Narrative exceeds 120 word limit. Current: {word_count}")

        # We must have at least one citation.
        if not citations or len(citations) == 0:
            errors.append("Regulatory citations list is empty")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

# ===== REACT PROMPTING HELPERS =====

def create_react_framework():
    """Helper function showing ReACT structure
    
    TODO: Study this example and adapt for compliance narratives:
    
    **REASONING Phase:**
    1. Review the risk analyst's findings
    2. Assess regulatory narrative requirements
    3. Identify key compliance elements
    4. Consider narrative structure
    
    **ACTION Phase:**
    1. Draft concise narrative (≤120 words)
    2. Include specific details and amounts
    3. Reference suspicious activity pattern
    4. Ensure regulatory language
    """
    return {
        "reasoning_phase": [
            "Review risk analysis findings",
            "Assess regulatory requirements", 
            "Identify compliance elements",
            "Plan narrative structure"
        ],
        "action_phase": [
            "Draft concise narrative",
            "Include specific details",
            "Reference activity patterns",
            "Use regulatory language"
        ]
    }

def get_regulatory_requirements():
    """Key regulatory requirements for SAR narratives
    
    TODO: Use these requirements in your prompts:
    """
    return {
        "word_limit": 120,
        "required_elements": [
            "Customer identification",
            "Suspicious activity description", 
            "Transaction amounts and dates",
            "Why activity is suspicious"
        ],
        "terminology": [
            "Suspicious activity",
            "Regulatory threshold",
            "Financial institution",
            "Money laundering",
            "Bank Secrecy Act"
        ],
        "citations": [
            "31 CFR 1020.320 (BSA)",
            "12 CFR 21.11 (SAR Filing)",
            "FinCEN SAR Instructions"
        ]
    }

# ===== TESTING UTILITIES =====

def test_narrative_generation():
    """Test the agent with sample risk analysis
    
    TODO: Use this function to test your implementation:
    - Create sample risk analysis results
    - Initialize compliance agent
    - Generate narrative
    - Validate compliance requirements
    """
    print("🧪 Testing Compliance Officer Agent")
    """Test the agent with sample risk analysis (Self-contained Mock Test)"""
    print("\n🧪 Testing Compliance Officer Agent...")

    # 1. Create Sample Data (Case & Risk Analysis)
    # ---------------------------------------------------------
    print("   1. Creating sample inputs...")

    # Minimal Customer & Account
    cust = CustomerData(
        customer_id="TEST_CUST", name="John Doe", date_of_birth="1980-01-01",
        ssn_last_4="1234", address="123 Main St", customer_since="2020", risk_rating="Medium"
    )

    # Minimal Transactions
    txs = [
        TransactionData(
            transaction_id="T1",
            account_id="A1",
            transaction_date="2024-01-01",
            transaction_type="Deposit",
            amount=9900.0,
            method="Cash",
            description="Dep",
            location="Br1"
        ),
        TransactionData(
            transaction_id="T2",
            account_id="A1",
            transaction_date="2024-01-02",
            transaction_type="Deposit",
            amount=9900.0, method="Cash",
            description="Dep",
            location="Br1"
        )
    ]

    case = CaseData(
        case_id="TEST_CASE",
        customer=cust,
        accounts=[],
        transactions=txs,
        case_created_at="2024-01-03",
        data_sources={}
    )

    # Minimal Risk Analysis
    risk_out = RiskAnalystOutput(
        classification="Structuring",
        confidence_score=0.95,
        risk_level="High",
        reasoning="Pattern of deposits just below reporting threshold.",
        key_indicators=["threshold avoidance", "cash deposits"]
    )

    print("   2. Initializing Agent with Mock Client...")
    # Create a mock that behaves like the OpenAI client
    mock_client = MagicMock()
    mock_response = MagicMock()

    # Define what the LLM "returns"
    mock_content = """
        ```json
        {
            "narrative_reasoning": "The customer is structuring deposits to avoid CTRs.",
            "regulatory_citations": ["31 CFR 1020.320"],
            "narrative": "Between Jan 1 and Jan 2, 2024, customer John Doe conducted two cash deposits of $9,900 each, totaling $19,800. These transactions occurred on consecutive days. The amounts appear designed to evade the $10,000 Currency Transaction Report (CTR) filing requirement. This pattern suggests structuring behavior with no apparent lawful purpose.",
            "completeness_check": true
        }
        ```
        """

    # structure the mock to match client.chat.completions.create().choices[0].message.content
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = mock_content
    mock_client.chat.completions.create.return_value = mock_response

    # Initialize agent
    logger = ExplainabilityLogger()  # Helper logger
    agent = ComplianceOfficerAgent(mock_client, logger)

    # 3. Generate Narrative
    # ---------------------------------------------------------
    print("   3. Generating Narrative...")
    try:
        result = agent.generate_compliance_narrative(case, risk_out)
        print("      ✅ Narrative generated successfully.")
    except Exception as e:
        print(f"      ❌ Failed to generate narrative: {e}")
        return

    # 4. Validate Compliance Requirements
    # ---------------------------------------------------------
    print("   4. Validating Output...")

    # Check 1: Narrative Length
    word_count = len(result.narrative.split())
    if word_count <= 120:
        print(f"      ✅ Word count OK: {word_count} words (Limit: 120)")
    else:
        print(f"      ❌ Word count exceeded: {word_count} words")

    # Check 2: Citations present
    if len(result.regulatory_citations) > 0:
        print(f"      ✅ Citations present: {result.regulatory_citations}")
    else:
        print("      ❌ No regulatory citations found")

    # Check 3: Completeness flag
    if result.completeness_check:
        print("      ✅ Completeness check passed")
    else:
        print("      ❌ Completeness check failed")

    print("\n✅ Test Complete.")

if __name__ == "__main__":
    print("✅ Compliance Officer Agent Module")
    print("ReACT prompting for regulatory narrative generation")
    print("\n📋 TODO Items:")
    print("• Design ReACT system prompt")
    print("• Implement generate_compliance_narrative method")
    print("• Add narrative validation (word count, terminology)")
    print("• Create regulatory citation system")
    print("• Test with sample risk analysis results")
    print("\n💡 Key Concepts:")
    print("• ReACT: Reasoning + Action structured prompting")
    print("• Regulatory Compliance: BSA/AML requirements")
    print("• Narrative Constraints: Word limits and terminology")
    print("• Audit Logging: Complete decision documentation")
