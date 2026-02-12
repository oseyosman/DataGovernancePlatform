-- Seed data for NYSE 2024 Listed Company Compliance Guidance Memo
-- Based on: https://www.nyse.com/publicdocs/nyse/regulation/nyse/NYSE_2024_Listed_Company_Compliance_Guidance_Memo.pdf

-- 1. Recovery of Erroneously Awarded Compensation (Clawback Policy)
INSERT INTO compliance_requirements (standard_name, control_id, control_description, status, notes)
VALUES (
    'NYSE 2024 Memo',
    'CLAWBACK-001',
    'Adopt and implement a written policy for the recovery of erroneously awarded incentive-based compensation (Clawback Policy) as per NYSE Listing Standard 303A.14.',
    'compliant',
    'Policy adopted on Dec 1, 2023. Compliance confirmed via Listing Manager by Dec 31, 2023.'
);

-- 2. Dealing with Material News
INSERT INTO compliance_requirements (standard_name, control_id, control_description, status, notes)
VALUES (
    'NYSE 2024 Memo',
    'DISCLOSURE-001',
    'Ensure immediate release of material news to the public. For news released shortly before or during trading hours (7:00 AM - 4:00 PM ET), provide at least 10 minutes advance notice to NYSE Market Watch.',
    'compliant',
    'Standard Operating Procedure (SOP) for material news disclosure updated.'
);

-- 3. Annual Meeting Requirement
INSERT INTO compliance_requirements (standard_name, control_id, control_description, status, notes)
VALUES (
    'NYSE 2024 Memo',
    'GOVERNANCE-001',
    'Hold an annual shareholders'' meeting during each fiscal year as per Section 302.00 of the Listed Company Manual.',
    'in_progress',
    'Scheduled for Q2 2024.'
);

-- 4. Annual Written Affirmation & CEO Certification
INSERT INTO compliance_requirements (standard_name, control_id, control_description, status, notes)
VALUES (
    'NYSE 2024 Memo',
    'REPORTING-001',
    'Submit Annual Written Affirmation and Annual CEO Certification to NYSE via Listing Manager within 30 days of the annual shareholders'' meeting.',
    'not_applicable',
    'Pending annual meeting completion.'
);

-- 5. Interim Written Affirmation
INSERT INTO compliance_requirements (standard_name, control_id, control_description, status, notes)
VALUES (
    'NYSE 2024 Memo',
    'REPORTING-002',
    'Submit Interim Written Affirmation within 5 business days of any director or executive officer change, or change in independence status of a director.',
    'compliant',
    'No recent board changes.'
);

-- 6. T+1 Settlement Cycle
INSERT INTO compliance_requirements (standard_name, control_id, control_description, status, notes)
VALUES (
    'NYSE 2024 Memo',
    'TRADING-001',
    'Transition to T+1 settlement cycle effective May 28, 2024. Ensure all trading and settlement systems are updated to support one business day settlement.',
    'in_progress',
    'System testing scheduled for April 2024.'
);

-- 7. Related Party Transactions
INSERT INTO compliance_requirements (standard_name, control_id, control_description, status, notes)
VALUES (
    'NYSE 2024 Memo',
    'AUDIT-001',
    'Audit Committee must review and approve all related party transactions as defined in Item 404 of Regulation S-K.',
    'compliant',
    'Quarterly review process established.'
);

-- 8. Audit Committee Independence
INSERT INTO compliance_requirements (standard_name, control_id, control_description, status, notes)
VALUES (
    'NYSE 2024 Memo',
    'GOVERNANCE-002',
    'Maintain an independent Audit Committee that satisfies the requirements of Rule 10A-3 under the Exchange Act and Section 303A.06 of the Listed Company Manual.',
    'compliant',
    'Annual independence questionnaires completed by all members.'
);
