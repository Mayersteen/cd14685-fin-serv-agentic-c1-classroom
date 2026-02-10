# Foundation SAR - Core Data Schemas and Utilities
# TODO: Implement core Pydantic schemas and data processing utilities

"""
This module contains the foundational components for SAR processing:

1. Pydantic Data Schemas:
   - CustomerData: Customer profile information
   - AccountData: Account details and balances  
   - TransactionData: Individual transaction records
   - CaseData: Unified case combining all data sources
   - RiskAnalystOutput: Risk analysis results
   - ComplianceOfficerOutput: Compliance narrative results

2. Utility Classes:
   - ExplainabilityLogger: Audit trail logging
   - DataLoader: Combines fragmented data into case objects

YOUR TASKS:
- Study the data files in data/ folder
- Design Pydantic schemas that match the CSV structure
- Implement validation rules for financial data
- Create a DataLoader that builds unified case objects
- Add proper error handling and logging
"""

import json
import pandas as pd
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Literal, Annotated
from pydantic import BaseModel, Field, SecretStr, field_validator, AfterValidator, BeforeValidator, model_validator, ValidationError
import math
import uuid
import os
from enum import Enum


# ========================================================================================
# Pydantic Validation Functions and Smart Types for cleaner code and less repetition
# ========================================================================================
def validate_date_format(v: str) -> str:
    """Validator: Checks if string is YYYY-MM-DD"""
    try:
        datetime.strptime(v, '%Y-%m-%d')
    except ValueError:
        raise ValueError(f"Date must be in YYYY-MM-DD format: {v}")
    return v

def validate_float_precision(v: float) -> float:
    """Validator: Checks if float has max 2 decimal places"""
    shifted = v * 100
    # Use 1e-9 for floating point tolerance
    if not math.isclose(shifted, round(shifted), abs_tol=1e-9):
        raise ValueError(f"Float has too many decimal places (max 2): [{v}]")
    return v

def validate_non_empty(v: str) -> str:
    """Validator: Checks string is not empty or whitespace"""
    if not v.strip():
        raise ValueError("Field cannot be empty or whitespace only")
    return v

# Custom-ReUsable Types, that bind the function to the type
IsoDateStr = Annotated[str, AfterValidator(validate_date_format)]
NonEmptyStr = Annotated[str, AfterValidator(validate_non_empty)]

MAX_MONETARY_VALUE = 100_000_000_000.0
ValidatedFloat = Annotated[
    float,
    Field(ge=-MAX_MONETARY_VALUE, le=MAX_MONETARY_VALUE),
    AfterValidator(validate_float_precision)
]

# ========================================================================================

# ===== TODO: IMPLEMENT PYDANTIC SCHEMAS =====
class CustomerData(BaseModel):
    """Customer information schema with validation
    
    REQUIRED FIELDS (examine data/customers.csv):
    - customer_id: str = Unique identifier like "CUST_0001"
    - name: str = Full customer name like "John Smith"
    - date_of_birth: str = Date in YYYY-MM-DD format like "1985-03-15"
    - ssn_last_4: str = Last 4 digits like "1234"
    - address: str = Full address like "123 Main St, City, ST 12345"
    - customer_since: str = Date in YYYY-MM-DD format like "2010-01-15"
    - risk_rating: Literal['Low', 'Medium', 'High'] = Risk assessment
    
    OPTIONAL FIELDS:
    - phone: Optional[str] = Phone number like "555-123-4567"
    - occupation: Optional[str] = Job title like "Software Engineer"
    - annual_income: Optional[int] = Yearly income like 75000
    
    HINT: Use Field(..., description="...") for required fields
    HINT: Use Field(None, description="...") for optional fields
    HINT: Use Literal type for risk_rating to restrict values
    """
    # TODO: Complete the Pydantic models with validation logic [DONE]
    # Required Fields
    customer_id: NonEmptyStr = Field(..., description="Customer ID")
    name: NonEmptyStr = Field(..., description="Full customer name")
    date_of_birth: IsoDateStr = Field(..., description="Date of birth")
    # name, date_of_birth, and address would also be PII, but the question focused only on the
    # SSN (How will you handle the SSN field for privacy?), therefore I implemented special
    # handling only for the SSN in the first version
    ssn_last_4: SecretStr = Field(..., exclude=True, description="Last 4 SSN digits")
    address: NonEmptyStr = Field(..., description="Address")
    customer_since: IsoDateStr = Field(..., description="Customer Since Date")
    risk_rating: Literal['Low', 'Medium', 'High', 'Critical'] = Field(..., description="Risk assessment")

    # Optional Fields
    phone: Optional[str] = Field(None, description="Phone number")
    occupation: Optional[str] = Field(None, description="Job title")
    annual_income: Optional[int] = Field(None, description="Yearly income")

    # Ensure that ssn_last_4 consists of exactly 4 digits and no other characters.
    @field_validator('ssn_last_4')
    @classmethod
    def ssn4_format_validator(cls, v: SecretStr) -> SecretStr:
        ssn_value = v.get_secret_value()
        if not len(ssn_value) == 4:
            raise ValueError(f"ssn_last_4 must consist of four digits: {v}")
        if not ssn_value.isdigit():
            raise ValueError(f"ssn_last_4 can only include digits: {v}")
        if ssn_value == "0000":
            raise ValueError("SSN last 4 cannot be 0000")
        return v

class AccountData(BaseModel):
    """Account information schema with validation
    
    REQUIRED FIELDS (examine data/accounts.csv):
    - account_id: str = Unique identifier like "CUST_0001_ACC_1"
    - customer_id: str = Must match CustomerData.customer_id
    - account_type: str = Type like "Checking", "Savings", "Money_Market"
    - opening_date: str = Date in YYYY-MM-DD format
    - current_balance: float = Current balance (can be negative)
    - average_monthly_balance: float = Average balance
    - status: str = Status like "Active", "Closed", "Suspended"
    
    HINT: All fields are required for account data
    HINT: Use float for monetary amounts
    HINT: current_balance can be negative for overdrafts
    """
    # TODO: Implement the AccountData schema
    account_id: NonEmptyStr = Field(..., description="Account ID")
    customer_id: NonEmptyStr = Field(..., description="Customer ID")
    account_type: Literal['Checking', 'Savings', 'Money_Market', 'Business_Checking'] = Field(..., description="Account type")
    opening_date: IsoDateStr = Field(..., description="Date in YYYY-MM-DD format")
    current_balance: ValidatedFloat = Field(..., description="Current balance", allow_inf_nan=False)
    average_monthly_balance: ValidatedFloat = Field(..., description="Average balance", allow_inf_nan=False)
    status: Literal['Active', 'Closed', 'Suspended'] = Field(..., description="Account status")

class TransactionData(BaseModel):
    """Transaction information schema with validation
    
    REQUIRED FIELDS (examine data/transactions.csv):
    - transaction_id: str = Unique identifier like "TXN_B24455F3"
    - account_id: str = Must match AccountData.account_id
    - transaction_date: str = Date in YYYY-MM-DD format
    - transaction_type: str = Type like "Cash_Deposit", "Wire_Transfer"
    - amount: float = Transaction amount (negative for withdrawals)
    - description: str = Description like "Cash deposit at branch"
    - method: str = Method like "Wire", "ACH", "ATM", "Teller"
    
    OPTIONAL FIELDS:
    - counterparty: Optional[str] = Other party in transaction
    - location: Optional[str] = Transaction location or branch
    
    HINT: amount can be negative for debits/withdrawals
    HINT: Use descriptive field descriptions for clarity
    """
    # TODO: Implement the TransactionData schema
    transaction_id: NonEmptyStr = Field(..., description="Transaction ID")
    account_id: NonEmptyStr = Field(..., description="Account ID")
    transaction_date: IsoDateStr = Field(..., description="Transaction date")
    transaction_type: NonEmptyStr = Field(..., description="Transaction type")
    amount: ValidatedFloat = Field(..., description="Transaction amount")
    description: NonEmptyStr = Field(..., description="Transaction description")
    method: NonEmptyStr = Field(..., description="Transaction method")
    counterparty: Optional[str] = Field(None, description="Counter party in transaction")
    location: Optional[str] = Field(None, description="Transaction location or branch")

    @model_validator(mode='before')
    @classmethod
    def convert_nan_to_none(clscls, data: Any) -> Any:
        # Pre-validator to automatically convert pandas/numpy NaNs to None before
        # Pydantic validation occurs.

        if isinstance(data, dict):
            for k,v in data.items():
                # Check if falue is float and is nan
                if isinstance(v, float) and math.isnan(v):
                    data[k] = None

        return data

    @field_validator('transaction_date')
    @classmethod
    def validate_past_date(cls, v: str) -> str:
        try:
            # Parse the YYYY-MM-DD string
            txn_date = datetime.strptime(v, '%Y-%m-%d').date()
            current_date = datetime.now(timezone.utc).date()

            if txn_date > current_date:
                raise ValueError(f"Transaction date cannot be in the future: {v}")
        except ValueError as e:
            # Re-raise parsing errors if they occur (though IsoDateStr handles format)
            if "format" in str(e): raise e
            raise ValueError(f"Date validation error: {e}")

        return v

class CaseData(BaseModel):
    """Unified case object combining all data sources
    
    REQUIRED FIELDS:
    - case_id: str = Unique case identifier (generate with uuid)
    - customer: CustomerData = Customer information object
    - accounts: List[AccountData] = List of customer's accounts
    - transactions: List[TransactionData] = List of suspicious transactions
    - case_created_at: str = ISO timestamp when case was created
    - data_sources: Dict[str, str] = Source tracking with keys like:
      * "customer_source": "csv_extract_20241219"
      * "account_source": "csv_extract_20241219" 
      * "transaction_source": "csv_extract_20241219"
    
    VALIDATION RULES:
    - transactions list cannot be empty (use @field_validator)
    - All accounts should belong to the same customer
    - All transactions should belong to accounts in the case
    
    HINT: Use @field_validator('transactions') with @classmethod decorator
    HINT: Check if not v: raise ValueError("message") for empty validation
    """
    # TODO: Implement the CaseData schema with validation
    case_id: NonEmptyStr = Field(..., description="Case ID")
    customer: CustomerData = Field(..., description="Customer information")
    accounts: List[AccountData] = Field(..., description="Accounts information")
    transactions: List[TransactionData] = Field(..., min_length=1, description="Suspicious transactions")
    case_created_at: NonEmptyStr = Field(..., description="ISO timestamp when case was created")
    data_sources: Dict[str, str] = Field(..., description="Sources and source file")

#    @model_validator(mode='after')
#    def validate_referential_integrity(self) -> 'CaseData':
#        # Ensures that:
#        # 1. Acc accounts belong to the specified customer
#        # 2. All txn belong to one of the specified
#
#        # 1. Verification of Account <-> Customer link
#        for acc in self.accounts:
#            if acc.customer_id != self.customer.customer_id:
#                raise ValueError(
#                    f"Integrity Error: Account {acc.account_id} belongs to {acc.customer_id}, "
#                    f"but Case is for {self.customer.customer_id}"
#                )
#
#        # 2. Verification of TXN <-> Account link
#        valid_account_ids = {acc.account_id for acc in self.accounts}
#        for txn in self.transactions:
#            if txn.account_id not in valid_account_ids:
#                raise ValueError(
#                    f"Integrity Error: Transaction {txn.transaction_id} refers to "
#                    f"account {txn.account_id} which is not present in this case."
#                )
#        return self

class RiskAnalystOutput(BaseModel):
    """Risk Analyst agent structured output
    
    REQUIRED FIELDS (for Chain-of-Thought agent output):
    - classification: Literal['Structuring', 'Sanctions', 'Fraud', 'Money_Laundering', 'Other']
    - confidence_score: float = Confidence between 0.0 and 1.0 (use ge=0.0, le=1.0)
    - reasoning: str = Step-by-step analysis reasoning (max 500 chars)
    - key_indicators: List[str] = List of suspicious indicators found
    - risk_level: Literal['Low', 'Medium', 'High', 'Critical'] = Risk assessment
    
    HINT: Use Literal types to restrict classification and risk_level values
    HINT: Use Field(..., ge=0.0, le=1.0) for confidence_score validation
    HINT: Use Field(..., max_length=500) for reasoning length limit
    """
    # TODO: Implement the RiskAnalystOutput schema
    classification: Literal[
        'Structuring',
        'Sanctions',
        'Fraud',
        'Money_Laundering',
        'Other'
    ] = Field(..., description="Primary category of the suspicious activity")

    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 and 1.0"
    )

    reasoning: NonEmptyStr = Field(
        ...,
        max_length=500,
        description="Step-by-step analysis reasoning (max 500 chars)"
    )

    key_indicators: List[str] = Field(
        ...,
        min_length=1,
        description="List of suspicious indicators"
    )

    risk_level: Literal['Low', 'Medium', 'High', 'Critical'] = Field(..., description="Risk assessment")

class ComplianceOfficerOutput(BaseModel):
    """Compliance Officer agent structured output
    
    REQUIRED FIELDS (for ReACT agent output):
    - narrative: str = Regulatory narrative text (max 1000 chars for ≤200 words)
    - narrative_reasoning: str = Reasoning for narrative construction (max 500 chars)
    - regulatory_citations: List[str] = List of relevant regulations like:
      * "31 CFR 1020.320 (BSA)"
      * "12 CFR 21.11 (SAR Filing)"
      * "FinCEN SAR Instructions"
    - completeness_check: bool = Whether narrative meets all requirements
    
    HINT: Use Field(..., max_length=1000) for narrative length limit
    HINT: Use Field(..., max_length=500) for reasoning length limit
    HINT: Use bool type for completeness_check
    """
    # TODO: Implement the ComplianceOfficerOutput schema
    narrative: NonEmptyStr = Field(..., max_length=1000, description="Regulatory narrative (max 1000 chars)")
    narrative_reasoning: NonEmptyStr = Field(..., max_length=500, description="Reasoning for narrative construction (max 500 chars)")
    regulatory_citations: List[str] = Field(..., min_length=1, description="List of relevant regulations")
    completeness_check: bool = Field(..., description="True if narrative meets all requirements")

# ===== TODO: IMPLEMENT AUDIT LOGGING =====

class ExplainabilityLogger:
    """Simple audit logging for compliance trails

    ATTRIBUTES:
    - log_file: str = Path to JSONL log file (default: "sar_audit.jsonl")
    - entries: List = In-memory storage of log entries

    METHODS:
    - log_agent_action(): Logs agent actions with structured data
    
    LOG ENTRY STRUCTURE (use this exact format):
    {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'case_id': case_id,
        'agent_type': agent_type,  # "DataLoader", "RiskAnalyst", "ComplianceOfficer"
        'action': action,          # "create_case", "analyze_case", "generate_narrative"
        'input_summary': str(input_data),
        'output_summary': str(output_data),
        'reasoning': reasoning,
        'execution_time_ms': execution_time_ms,
        'success': success,        # True/False
        'error_message': error_message  # None if success=True
    }
    
    HINT: Write each entry as JSON + newline to create JSONL format
    HINT: Use 'a' mode to append to log file
    HINT: Store entries in self.entries list AND write to file
    """
    
    def __init__(self, log_file: str = "sar_audit.jsonl"):
        # TODO: Initialize with log_file path and empty entries list
        self.log_file = log_file
        self.entries = []
    
    def log_agent_action(self, agent_type: str, action: str, case_id: str, 
                        input_data: Dict, output_data: Dict, reasoning: str, 
                        execution_time_ms: float, success: bool = True, 
                        error_message: Optional[str] = None) -> str:
        """Log an agent action with essential context
        
        IMPLEMENTATION STEPS:
        1. Create entry dictionary with all fields (see structure above)
        2. Add entry to self.entries list
        3. Write entry to log file as JSON line
        
        HINT: Use json.dumps(entry) + '\n' for JSONL format
        HINT: Use datetime.now(timezone.utc).isoformat() for timestamp
        HINT: Convert input_data and output_data to strings with str()
        """

        log_id = str(uuid.uuid4())

        entry = {
            'log_id': log_id,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'case_id': case_id,
            'agent_type': agent_type,
            'action': action,
            'input_summary': str(input_data),
            'output_summary': str(output_data),
            'reasoning': reasoning,
            'execution_time_ms': execution_time_ms,
            'success': success,
            'error_message': error_message
        }

        self.entries.append(entry)

        # We use 'append' mode for writing to avoid the deletion of previous logs.
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry) + '\n')
        except IOError as e:
            # We will print the log to console if file access fails.
            print(f"⚠️ Logger Error: Could not write to {self.log_file}: {e}")

        return log_id

class DataLoader:
    """Simple loader that creates case objects from CSV data
    
    ATTRIBUTES:
    - logger: ExplainabilityLogger = For audit logging
    
    HELPFUL METHODS:
    - create_case_from_data(): Creates CaseData from input dictionaries
    
    IMPLEMENTATION PATTERN:
    1. Start timing with start_time = datetime.now()
    2. Generate case_id with str(uuid.uuid4())
    3. Create CustomerData object from customer_data dict
    4. Filter accounts where acc['customer_id'] == customer.customer_id
    5. Get account_ids set from filtered accounts
    6. Filter transactions where txn['account_id'] in account_ids
    7. Create CaseData object with all components
    8. Calculate execution_time_ms
    9. Log success/failure with self.logger.log_agent_action()
    10. Return CaseData object (or raise exception on failure)
    """
    
    def __init__(self, explainability_logger: ExplainabilityLogger):
        # TODO: Store logger for audit trail
        self.logger = explainability_logger
    
    def create_case_from_data(self, 
                            customer_data: Dict,
                            account_data: List[Dict],
                            transaction_data: List[Dict]) -> CaseData:
        """Create a unified case object from fragmented AML data

        SUGGESTED STEPS:
        1. Record start time for performance tracking
        2. Generate unique case_id using uuid.uuid4()
        3. Create CustomerData object from customer_data dictionary
        4. Filter account_data list for accounts belonging to this customer
        5. Create AccountData objects from filtered accounts
        6. Get set of account_ids from customer's accounts
        7. Filter transaction_data for transactions in customer's accounts
        8. Create TransactionData objects from filtered transactions  
        9. Create CaseData object combining all components
        10. Add case metadata (case_id, timestamp, data_sources)
        11. Calculate execution time in milliseconds
        12. Log operation with success/failure status
        13. Return CaseData object
        
        ERROR HANDLING:
        - Wrap in try/except block
        - Log failures with error message
        - Re-raise exceptions for caller
        
        DATA_SOURCES FORMAT:
        {
            'customer_source': f"csv_extract_{datetime.now().strftime('%Y%m%d')}",
            'account_source': f"csv_extract_{datetime.now().strftime('%Y%m%d')}",
            'transaction_source': f"csv_extract_{datetime.now().strftime('%Y%m%d')}"
        }
        
        HINT: Use list comprehensions for filtering
        HINT: Use set comprehension for account_ids: {acc.account_id for acc in accounts}
        HINT: Use datetime.now(timezone.utc).isoformat() for timestamps
        HINT: Calculate execution_time_ms = (datetime.now() - start_time).total_seconds() * 1000
        """

        start_time = datetime.now(timezone.utc)
        case_id = str(uuid.uuid4())

        try:

            # Improved customer data import
            try:
                customer = CustomerData(**customer_data)
            except ValidationError as e:
                raise ValueError(f"Customer Data Error (ID: {customer_data.get('customer_id')}): {e}")

            # Improved account data import
            customer_accounts = []
            raw_customer_accounts = [acc for acc in account_data if acc['customer_id'] == customer.customer_id]

            for acc_dict in raw_customer_accounts:
                try:
                    customer_accounts.append(AccountData(**acc_dict))
                except ValidationError as e:
                    acc_id = acc_dict.get('account_id', 'Unknown')
                    raise ValueError(f"Account Data Error (Account ID: {acc_id}): {e}")

            valid_account_ids = {acc.account_id for acc in customer_accounts}

            # Improved transactions import
            customer_transactions = []
            raw_customer_transactions = [txn for txn in transaction_data if txn['account_id'] in valid_account_ids]

            for txn_dict in raw_customer_transactions:
                try:
                    customer_transactions.append(TransactionData(**txn_dict))
                except ValidationError as e:
                    # FIX 1: Identify exactly which transaction failed
                    txn_id = txn_dict.get('transaction_id', 'Unknown')
                    raise ValueError(f"Transaction Data Error (Txn ID: {txn_id}): {e}")


            current_date_str = datetime.now().strftime('%Y%m%d')
            data_sources = {
                'customer_source': f"csv_extract_{current_date_str}",
                'account_source': f"csv_extract_{current_date_str}",
                'transaction_source': f"csv_extract_{current_date_str}"
            }

            case = CaseData(
                case_id = case_id,
                customer = customer,
                accounts = customer_accounts,
                transactions = customer_transactions,
                case_created_at = datetime.now(timezone.utc).isoformat(),
                data_sources = data_sources
            )

            end_time = datetime.now(timezone.utc)
            execution_time_ms = (end_time - start_time).total_seconds() * 1000

            reasoning_msg = (
                f"Successfully built case for Customer {customer.customer_id}. "
                f"Aggregated {len(customer_accounts)} accounts and "
                f"{len(customer_transactions)} transactions."
            )

            self.logger.log_agent_action(
                agent_type = "DataLoader",
                action = "create_case",
                case_id = case_id,
                input_data = {"customer_id": customer.customer_id},
                output_data = {"case_id" : case.case_id, "status": "created"},
                reasoning = reasoning_msg,
                execution_time_ms = execution_time_ms,
                success = True
            )

            return case

        except Exception as e:
            end_time = datetime.now(timezone.utc)
            execution_time_ms = (end_time - start_time).total_seconds() * 1000

            self.logger.log_agent_action(
                agent_type = "DataLoader",
                action = "create_case",
                case_id = case_id,
                input_data = customer_data,
                output_data = {},
                reasoning = f"Failed to create case due to data integrity issue.",
                execution_time_ms = execution_time_ms,
                success = False,
                error_message = str(e)
            )

            raise e

# ===== HELPER FUNCTIONS (PROVIDED) =====

def _clean_and_prepare_records(df: pd.DataFrame) -> pd.DataFrame:
    context = "DataCleaning"
    df_cleaned = df.astype(object).where(pd.notnull(df), None)

    for col in df_cleaned.columns:
        has_nan = df_cleaned[col].apply(lambda x: isinstance(x, float) and math.isnan(x)).any()
        if has_nan:
            error_msg = f"[{context}] Critical Error: Column '{col}' still contains float NaNs."
            raise ValueError(error_msg)

    return df_cleaned

def load_csv_data(data_dir: str = "data/") -> tuple:
    """Helper function to load all CSV files

    Returns:
        tuple: (customers_df, accounts_df, transactions_df)
    """
    try:

        dtype_map = {
            'ssn_last_4': str,
            'customer_id': str,
            'account_id': str,
            'transaction_id': str
        }

        # Load CSVs with explicit types
        customers_df = pd.read_csv(f"{data_dir}/customers.csv", dtype=dtype_map)
        accounts_df = pd.read_csv(f"{data_dir}/accounts.csv", dtype=dtype_map)
        transactions_df = pd.read_csv(f"{data_dir}/transactions.csv", dtype=dtype_map)

        customers_df = _clean_and_prepare_records(customers_df)
        accounts_df = _clean_and_prepare_records(accounts_df)
        transactions_df = _clean_and_prepare_records(transactions_df)

        def strip_strings(x):
            return x.strip() if isinstance(x, str) else x

        customers_df = customers_df.map(strip_strings)
        accounts_df = accounts_df.map(strip_strings)
        transactions_df = transactions_df.map(strip_strings)

        return customers_df, accounts_df, transactions_df

    except FileNotFoundError as e:
        raise FileNotFoundError(f"CSV file not found: {e}")
    except Exception as e:
        raise Exception(f"Error loading CSV data: {e}")

if __name__ == "__main__":
    print("🏗️  Foundation SAR Module")
    print("Core data schemas and utilities for SAR processing")
    print("\n📋 TODO Items:")
    print("• Implement Pydantic schemas based on CSV data")
    print("• Create ExplainabilityLogger for audit trails")
    print("• Build DataLoader for case object creation")
    print("• Add comprehensive error handling")
    print("• Write unit tests for all components")
