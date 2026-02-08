# Workflow Efficiency & Cost Analysis Report

This report is based on the data from manual runs of "📊 Step 5: Workflow Metrics and Analysis" from  
the `03_workflow_integration.ipynb` file.

This report analyzes the performance of the Two-Stage AI Workflow for Suspicious Activity Report (SAR) 
generation. The system integrates a "Human-in-the-Loop" decision gate between the initial Risk Analysis 
(Stage 1) and the resource-intensive Compliance Narrative Generation (Stage 2).

The data demonstrates that the two-stage architecture successfully reduces operational costs by filtering 
out non-viable cases before expensive processing occurs, while maintaining a clear audit trail of human 
decision-making.

## Process throughput

The workflow processed a total of 5 cases, resulting in 2 filed SARs.



| Metric                   | Count | Rate |
|:-------------------------|:-----:| :--: |
| Total Cases Screened     |   5   | 100% |
| ✅ Approved (SARs Filed)  |   2   |40%|
| ❌ Rejected (No Filing)   |   3   |60%|

Observation: A rejection rate of 60% at the human gate indicates that the system is effectively 
serving as a filter, preventing the majority of cases from consuming downstream resources unnecessarily.

## Cost optimization analysis

The primary goal of the two-stage architecture is to minimize API costs associated with the Compliance Officer agent, which generates long-form narratives.

- Strategy: Only run the Compliance Agent for cases approved by the human reviewer.
- Result: The workflow avoided 3 expensive compliance calls (60% of total volume).

| Cost Model       | Description                                 | Estimated Cost |
|:-----------------|:--------------------------------------------|:--------------:|
| **Theoretical Cost** | Single-Stage (Run everything for everyone)  |     $3.00      |
| **Actual Cost**      | Two-Stage (Run Compliance only on approval) |     $1.65      |
| **Net Savings**      | **Total capital preserved**                 |     $1.35      |

Total Cost Reduction: **45.0%**

Conclusion: The cost optimization hypothesis is VALIDATED. 

The implementation successfully demonstrated a 45% reduction in operational expense compared 
to a monolithic (single-stage) automation approach.

## Human-AI Decision Alignment

The data is based on my run, where I made "random decisions".

This section evaluates the agreement between the AI's risk assessment and the human reviewer's 
final decision.

- Total Decisions Logged: 5
- Decisions Breakdown:
  - REJECT: 3
  - PROCEED: 2

### Confidence Correlation:

We analyzed the average AI confidence scores for cases that were approved versus those 
that were rejected.

| Decision outcome    | Avg. AI Confidence |
|:--------------------|:-------------------|
| **Approved Cases**  | 0.92               |
| **Rejeceted Cases** | 0.92               |

### Critical Insight

The data shows that humans are rejecting cases where the AI had high confidence (0.92).

### Interpretation

This suggests a potential disagreement pattern. The AI may be overfitting to specific indicators (false positives), or the human reviewer is applying nuance that the current prompt engineering does not capture. This warrants further tuning of the Risk Analyst's instructions to align better with human judgment.