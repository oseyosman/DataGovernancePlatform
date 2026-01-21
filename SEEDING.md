# Company Data Seeding

## Quick Start

Populate the database with 20 companies from AnnualReports.com:

```bash
python seed_companies.py
```

List all companies in database:

```bash
python seed_companies.py --list
```

Specify a different target count:

```bash
python seed_companies.py --count 25
```

## What It Does

The `seed_companies.py` script:
- Scrapes real company data from AnnualReports.com
- Stores company information (name, website, industry, etc.)
- Adds the 3 most recent annual reports for each company
- Validates data quality (skips generic pages or companies without reports)
- Prevents duplicates (checks if company already exists)

## Current Database

**20 Companies with 97 Annual Reports:**

1. Abbvie Inc
2. Apple Inc. (30 reports - kept all historical)
3. Caterpillar Inc.
4. Cisco Systems Inc.
5. Deere & Co.
6. Dell Technologies Inc.
7. Goldman Sachs Group Inc.
8. Johnson & Johnson
9. Lowe's Companies, Inc.
10. Merck & Co. Inc.
11. Meta Platforms, Inc.
12. PayPal Holdings, Inc
13. Pepsico, Inc.
14. Pfizer Inc.
15. Procter & Gamble Co.
16. Starbucks Corp.
17. Target Corp.
18. Tesla, Inc. (13 reports)
19. Visa, Inc
20. Walmart Inc

## Data Source

All data is scraped from [AnnualReports.com](https://www.annualreports.com) which provides:
- Company profiles
- Annual financial reports (PDF downloads)
- Historical reports going back 20-30 years
- 10,379+ international companies

## View in UI

After seeding, view the companies in your application:
1. Go to http://localhost:5000
2. Login
3. Click the **"Companies"** tab
4. Browse real company data with direct PDF links
