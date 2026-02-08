# Workflow Testing and Validation
This output stems from `Step 7` of the `03_workflow_integration.ipynb` notebook.

```
✅ Paths set. Looking for tests in: C:\Users\mayer\PycharmProjects\cd14685-fin-serv-agentic-c1-classroom\project\starter\tests
📁 Added tests directory to Python path: C:\Users\mayer\PycharmProjects\cd14685-fin-serv-agentic-c1-classroom\project\starter\tests
🔍 Validating Workflow Components
✅ Foundation components available
✅ Risk Analyst Agent available
✅ Compliance Officer Agent available
✅ Test modules available

📊 Component Status: ✅ ALL READY

🚀 All components ready - you can run integration tests!
🧪 Comprehensive Integration Testing
📋 TODO: Uncomment and run after implementing complete workflow
🔍 Running Foundation Component Tests...
============================= test session starts =============================
platform win32 -- Python 3.14.2, pytest-9.0.2, pluggy-1.6.0 -- C:\Users\mayer\PycharmProjects\cd14685-fin-serv-agentic-c1-classroom\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\mayer\PycharmProjects\cd14685-fin-serv-agentic-c1-classroom\project\starter
plugins: anyio-4.12.1
collecting ... collected 10 items


..\tests\test_foundation.py::TestCustomerData::test_valid_customer_data PASSED [ 10%]

..\tests\test_foundation.py::TestCustomerData::test_customer_risk_rating_validation PASSED [ 20%]

..\tests\test_foundation.py::TestAccountData::test_valid_account_data PASSED [ 30%]

..\tests\test_foundation.py::TestAccountData::test_account_balance_validation PASSED [ 40%]

..\tests\test_foundation.py::TestTransactionData::test_valid_transaction_data PASSED [ 50%]

..\tests\test_foundation.py::TestTransactionData::test_transaction_amount_validation PASSED [ 60%]

..\tests\test_foundation.py::TestCaseData::test_valid_case_creation PASSED [ 70%]

..\tests\test_foundation.py::TestDataLoader::test_csv_data_loading PASSED [ 80%]

..\tests\test_foundation.py::TestExplainabilityLogger::test_log_creation PASSED [ 90%]

..\tests\test_foundation.py::TestExplainabilityLogger::test_log_file_writing PASSED [100%]


============================== warnings summary ===============================
..\..\..\.venv\Lib\site-packages\_pytest\config\__init__.py:1303
  C:\Users\mayer\PycharmProjects\cd14685-fin-serv-agentic-c1-classroom\.venv\Lib\site-packages\_pytest\config\__init__.py:1303: PytestAssertRewriteWarning: Module already imported so cannot be rewritten; anyio
    self._mark_plugins_for_rewrite(hook, disable_autoload)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================== 10 passed, 1 warning in 0.04s ========================
🔍 Running Risk Analyst Agent Tests...
============================= test session starts =============================
platform win32 -- Python 3.14.2, pytest-9.0.2, pluggy-1.6.0 -- C:\Users\mayer\PycharmProjects\cd14685-fin-serv-agentic-c1-classroom\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\mayer\PycharmProjects\cd14685-fin-serv-agentic-c1-classroom\project\starter
plugins: anyio-4.12.1
collecting ... collected 10 items


..\tests\test_risk_analyst.py::TestRiskAnalystAgent::test_agent_initialization PASSED [ 10%]

..\tests\test_risk_analyst.py::TestRiskAnalystAgent::test_analyze_case_success PASSED [ 20%]

..\tests\test_risk_analyst.py::TestRiskAnalystAgent::test_analyze_case_json_error PASSED [ 30%]

..\tests\test_risk_analyst.py::TestRiskAnalystAgent::test_extract_json_from_code_block PASSED [ 40%]

..\tests\test_risk_analyst.py::TestRiskAnalystAgent::test_extract_json_from_plain_text PASSED [ 50%]

..\tests\test_risk_analyst.py::TestRiskAnalystAgent::test_extract_json_empty_response PASSED [ 60%]

..\tests\test_risk_analyst.py::TestRiskAnalystAgent::test_format_accounts PASSED [ 70%]

..\tests\test_risk_analyst.py::TestRiskAnalystAgent::test_format_transactions PASSED [ 80%]

..\tests\test_risk_analyst.py::TestRiskAnalystAgent::test_system_prompt_structure PASSED [ 90%]

..\tests\test_risk_analyst.py::TestRiskAnalystAgent::test_api_call_parameters PASSED [100%]


============================== warnings summary ===============================
..\..\..\.venv\Lib\site-packages\_pytest\config\__init__.py:1303
  C:\Users\mayer\PycharmProjects\cd14685-fin-serv-agentic-c1-classroom\.venv\Lib\site-packages\_pytest\config\__init__.py:1303: PytestAssertRewriteWarning: Module already imported so cannot be rewritten; anyio
    self._mark_plugins_for_rewrite(hook, disable_autoload)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================== 10 passed, 1 warning in 0.04s ========================
📝 Running Compliance Officer Agent Tests...
============================= test session starts =============================

platform win32 -- Python 3.14.2, pytest-9.0.2, pluggy-1.6.0 -- C:\Users\mayer\PycharmProjects\cd14685-fin-serv-agentic-c1-classroom\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\mayer\PycharmProjects\cd14685-fin-serv-agentic-c1-classroom\project\starter
plugins: anyio-4.12.1
collecting ... collected 10 items


..\tests\test_compliance_officer.py::TestComplianceOfficerAgent::test_agent_initialization PASSED [ 10%]

..\tests\test_compliance_officer.py::TestComplianceOfficerAgent::test_generate_compliance_narrative_success PASSED [ 20%]

..\tests\test_compliance_officer.py::TestComplianceOfficerAgent::test_narrative_word_count_validation PASSED [ 30%]

..\tests\test_compliance_officer.py::TestComplianceOfficerAgent::test_json_parsing_error PASSED [ 40%]

..\tests\test_compliance_officer.py::TestComplianceOfficerAgent::test_extract_json_from_code_block PASSED [ 50%]

..\tests\test_compliance_officer.py::TestComplianceOfficerAgent::test_extract_json_from_plain_text PASSED [ 60%]

..\tests\test_compliance_officer.py::TestComplianceOfficerAgent::test_extract_json_empty_response PASSED [ 70%]

..\tests\test_compliance_officer.py::TestComplianceOfficerAgent::test_format_transactions_for_compliance PASSED [ 80%]

..\tests\test_compliance_officer.py::TestComplianceOfficerAgent::test_system_prompt_structure PASSED [ 90%]

..\tests\test_compliance_officer.py::TestComplianceOfficerAgent::test_api_call_parameters PASSED [100%]


============================== warnings summary ===============================
..\..\..\.venv\Lib\site-packages\_pytest\config\__init__.py:1303
  C:\Users\mayer\PycharmProjects\cd14685-fin-serv-agentic-c1-classroom\.venv\Lib\site-packages\_pytest\config\__init__.py:1303: PytestAssertRewriteWarning: Module already imported so cannot be rewritten; anyio
    self._mark_plugins_for_rewrite(hook, disable_autoload)

..\..\..\..\..\..\..\Python314\Lib\unittest\mock.py:1170
  C:\Python314\Lib\unittest\mock.py:1170: PytestCollectionWarning: cannot collect 'test_client' because it is not a function.
    def __call__(self, /, *args, **kwargs):

..\..\..\..\..\..\..\Python314\Lib\unittest\mock.py:1170
  C:\Python314\Lib\unittest\mock.py:1170: PytestCollectionWarning: cannot collect 'test_logger' because it is not a function.
    def __call__(self, /, *args, **kwargs):

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================= 10 passed, 3 warnings in 0.07s ========================

============================================================
📊 INTEGRATION TEST RESULTS:
   Foundation Components: ✅ PASS
   Risk Analyst Agent: ✅ PASS
   Compliance Officer Agent: ✅ PASS
   Overall Status: ✅ ALL TESTS PASSED

🎉 Your system is ready for production workflow testing!
📝 Proceed to run the complete system demonstration.
```

## Cell 2
As I have no more credits, I had to implement Mock services and responses, to ensure that I don't get stuck by OpenAI
API errors (no more credits), etc.

The variable/constant `SELECT_TOP_N_CUSTOMERS` defines how many top_n customers are processed.

```
🎯 End-to-End Workflow Testing (Hybrid Mode)
ℹ️  Configuration: Real CSV Data + Mock AI Agents
🚀 Starting end-to-end workflow test...
📂 Loading Real Data from: C:\Users\mayer\PycharmProjects\cd14685-fin-serv-agentic-c1-classroom\project\starter\data
   📊 Loaded 150 customers, 178 accounts, 4268 transactions.
🔍 Screening customers from real data...
✅ Selected 6 customers for processing

▶️  Processing Customer 1: Tanya Johnston
   ✅ Case Created: 872c9845-52b6-493e-b9a5-039969a67045
📄 Creating SAR Document
   ✅ SAR Generated: SAR_b90e5687-88d8-4ccb-8c1b-f3a5df365cfd

▶️  Processing Customer 2: Lucas Allen
   ✅ Case Created: 211335dd-422c-45ef-b6d7-bb006539ea74
📄 Creating SAR Document
   ✅ SAR Generated: SAR_4ef82c41-5477-44f5-be68-0ae89a5ee39e

▶️  Processing Customer 3: Cindy Clayton
   ✅ Case Created: 7f93385f-3cf7-4eb0-8ab6-912506dadacb
📄 Creating SAR Document
   ✅ SAR Generated: SAR_476f6866-1ea1-422f-a149-0217b846bee5

▶️  Processing Customer 4: Melissa Miller
   ✅ Case Created: 5b832ab5-b90d-489d-afad-e10f94d15aeb
📄 Creating SAR Document
   ✅ SAR Generated: SAR_b5e854d2-994d-4025-a00c-d59c88aaf091

▶️  Processing Customer 5: Elijah Patton
   ✅ Case Created: d5d23446-f9a1-4768-a68a-5aaaebf06bd0
📄 Creating SAR Document
   ✅ SAR Generated: SAR_98180f71-2ca1-4f63-8cfd-244493cc1678

▶️  Processing Customer 6: Clayton Steele
   ✅ Case Created: 2db94ca2-5e14-4e16-aa87-5d6c91b41cfe
📄 Creating SAR Document
   ✅ SAR Generated: SAR_c46b8c3e-bc77-4a2a-a594-7b05f0ce60ce

📊 HYBRID TEST RESULTS:
   Cases Processed: 6
   SARs Generated: 6
   Errors: 0
```