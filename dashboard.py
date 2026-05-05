import pandas as pd
from pathlib import Path

# ==========================================================
# Accounting Intern Automation System
# Equity Residential-style Multi-Property Accounting Workflow
# ==========================================================

BASE_DIR = Path("accounting_intern_automation")
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"

DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ----------------------------------------------------------
# 1. Create sample data if files do not exist
# ----------------------------------------------------------

def create_sample_data():
    properties_file = DATA_DIR / "properties.csv"
    gl_file = DATA_DIR / "gl_accounts.csv"
    utilities_file = DATA_DIR / "utilities.csv"
    invoices_file = DATA_DIR / "invoices.csv"
    vendors_file = DATA_DIR / "vendors.csv"

    if not properties_file.exists():
        pd.DataFrame({
            "property_id": ["P001", "P002", "P003", "P004"],
            "property_name": ["Augusta Gardens", "River View", "Lake Point", "Oak Heights"],
            "expected_cashflow": [50000, 62000, 45500, 71000],
            "actual_cashflow": [48000, 62000, 47000, 69000]
        }).to_csv(properties_file, index=False)

    if not gl_file.exists():
        pd.DataFrame({
            "property_id": ["P001", "P001", "P002", "P003", "P004"],
            "account_type": ["Payables", "Receivables", "Settlement", "Suspense", "Chargeback"],
            "expected_balance": [20000, 15000, 10000, 5000, 2500],
            "actual_balance": [21000, 15000, 9700, 6200, 2500]
        }).to_csv(gl_file, index=False)

    if not utilities_file.exists():
        pd.DataFrame({
            "property_id": ["P001", "P002", "P003", "P004", "P004"],
            "utility_type": ["Electricity", "Water", "Gas", "Electricity", "Electricity"],
            "expected_bill": [1200, 1500, 950, 1800, 1800],
            "actual_bill": [1250, 1500, 870, 2100, 2100],
            "billing_status": ["Billed", "Billed", "Billed", "Billed", "Billed"]
        }).to_csv(utilities_file, index=False)

    if not invoices_file.exists():
        pd.DataFrame({
            "invoice_id": ["INV001", "INV002", "INV003", "INV004"],
            "property_id": ["P001", "P002", "P003", "P004"],
            "vendor": ["ABC Services", "XYZ Utilities", "Prime Maintenance", "Georgia Repairs"],
            "gl_account": ["Payables", "Utilities", "Repairs", "Maintenance"],
            "invoice_amount": [500, 700, 1200, 950],
            "payment_status": ["Processed", "Delayed", "Processed", "Voided"]
        }).to_csv(invoices_file, index=False)

    if not vendors_file.exists():
        pd.DataFrame({
            "vendor": ["ABC Services", "XYZ Utilities", "Prime Maintenance", "Georgia Repairs"],
            "tax_id_available": [True, False, True, True],
            "w9_on_file": [True, False, True, True]
        }).to_csv(vendors_file, index=False)


# ----------------------------------------------------------
# 2. Cash flow reconciliation
# ----------------------------------------------------------

def reconcile_cashflows(properties_df):
    properties_df["cashflow_variance"] = (
        properties_df["actual_cashflow"] - properties_df["expected_cashflow"]
    )

    properties_df["variance_percent"] = (
        properties_df["cashflow_variance"] / properties_df["expected_cashflow"] * 100
    ).round(2)

    properties_df["reconciliation_status"] = properties_df["cashflow_variance"].apply(
        lambda x: "Matched" if x == 0 else "Review Required"
    )

    return properties_df


# ----------------------------------------------------------
# 3. GL account reconciliation
# ----------------------------------------------------------

def reconcile_gl_accounts(gl_df):
    gl_df["gl_variance"] = gl_df["actual_balance"] - gl_df["expected_balance"]

    gl_df["status"] = gl_df["gl_variance"].apply(
        lambda x: "Reconciled" if x == 0 else "Exception"
    )

    return gl_df


# ----------------------------------------------------------
# 4. Financial variance analysis
# ----------------------------------------------------------

def analyze_variances(properties_df):
    summary = properties_df.groupby("property_id").agg(
        expected_cashflow=("expected_cashflow", "sum"),
        actual_cashflow=("actual_cashflow", "sum"),
        total_variance=("cashflow_variance", "sum")
    ).reset_index()

    summary["variance_percent"] = (
        summary["total_variance"] / summary["expected_cashflow"] * 100
    ).round(2)

    summary["risk_level"] = summary["variance_percent"].apply(
        lambda x: "High" if abs(x) >= 5 else "Moderate" if abs(x) >= 2 else "Low"
    )

    return summary


# ----------------------------------------------------------
# 5. Utility billing validation
# ----------------------------------------------------------

def validate_utility_billing(utilities_df):
    utilities_df["billing_variance"] = (
        utilities_df["actual_bill"] - utilities_df["expected_bill"]
    )

    utilities_df["duplicate_record"] = utilities_df.duplicated(
        subset=["property_id", "utility_type", "actual_bill"],
        keep=False
    )

    utilities_df["billing_issue"] = utilities_df.apply(
        lambda row: "Duplicate Entry"
        if row["duplicate_record"]
        else "Billing Variance"
        if row["billing_variance"] != 0
        else "Valid",
        axis=1
    )

    return utilities_df


# ----------------------------------------------------------
# 6. Invoice processing review
# ----------------------------------------------------------

def review_invoices(invoices_df):
    invoices_df["requires_follow_up"] = invoices_df["payment_status"].apply(
        lambda x: True if x in ["Delayed", "Voided"] else False
    )

    invoices_df["invoice_action"] = invoices_df["payment_status"].apply(
        lambda x: "Resolve delayed payment"
        if x == "Delayed"
        else "Confirm voided check or reissue"
        if x == "Voided"
        else "No action required"
    )

    return invoices_df


# ----------------------------------------------------------
# 7. Tax preparation support
# ----------------------------------------------------------

def prepare_tax_summary(vendors_df):
    vendors_df["tax_document_status"] = vendors_df.apply(
        lambda row: "Complete"
        if row["tax_id_available"] and row["w9_on_file"]
        else "Incomplete",
        axis=1
    )

    return vendors_df


# ----------------------------------------------------------
# 8. Generate management summary
# ----------------------------------------------------------

def generate_summary(cashflow_df, gl_df, utility_df, invoice_df, tax_df):
    summary = {
        "properties_reviewed": cashflow_df["property_id"].nunique(),
        "cashflow_exceptions": len(cashflow_df[cashflow_df["reconciliation_status"] == "Review Required"]),
        "gl_exceptions": len(gl_df[gl_df["status"] == "Exception"]),
        "utility_billing_issues": len(utility_df[utility_df["billing_issue"] != "Valid"]),
        "invoice_follow_ups": len(invoice_df[invoice_df["requires_follow_up"] == True]),
        "vendors_with_incomplete_tax_docs": len(tax_df[tax_df["tax_document_status"] == "Incomplete"])
    }

    return pd.DataFrame([summary])


# ----------------------------------------------------------
# 9. Run automation
# ----------------------------------------------------------

def main():
    create_sample_data()

    properties = pd.read_csv(DATA_DIR / "properties.csv")
    gl_accounts = pd.read_csv(DATA_DIR / "gl_accounts.csv")
    utilities = pd.read_csv(DATA_DIR / "utilities.csv")
    invoices = pd.read_csv(DATA_DIR / "invoices.csv")
    vendors = pd.read_csv(DATA_DIR / "vendors.csv")

    cashflow_report = reconcile_cashflows(properties)
    gl_report = reconcile_gl_accounts(gl_accounts)
    variance_report = analyze_variances(cashflow_report)
    utility_report = validate_utility_billing(utilities)
    invoice_report = review_invoices(invoices)
    tax_summary = prepare_tax_summary(vendors)

    management_summary = generate_summary(
        cashflow_report,
        gl_report,
        utility_report,
        invoice_report,
        tax_summary
    )

    cashflow_report.to_csv(OUTPUT_DIR / "cashflow_reconciliation_report.csv", index=False)
    gl_report.to_csv(OUTPUT_DIR / "gl_reconciliation_report.csv", index=False)
    variance_report.to_csv(OUTPUT_DIR / "financial_variance_analysis.csv", index=False)
    utility_report.to_csv(OUTPUT_DIR / "utility_billing_validation_report.csv", index=False)
    invoice_report.to_csv(OUTPUT_DIR / "invoice_processing_report.csv", index=False)
    tax_summary.to_csv(OUTPUT_DIR / "tax_preparation_summary.csv", index=False)
    management_summary.to_csv(OUTPUT_DIR / "management_summary.csv", index=False)

    print("Accounting automation completed successfully.")
    print("\nManagement Summary:")
    print(management_summary.to_string(index=False))


if __name__ == "__main__":
    main()
