# Quick Start Guide: Using Real Company Data

## Testing the Scraper

Run the test script to see the scraper in action:

```bash
cd c:\Users\osman\Github\DataGovernancePlatform
python test_scraper.py
```

This will:
1. Scrape Apple Inc. data (30 annual reports from 1994-2023)
2. Search for Microsoft
3. Save results to `apple_scraped_data.json`

## Before Running the API

You need to run database migrations to create the new tables:

```bash
cd backend1
flask db migrate -m "Add companies and annual reports tables"
flask db upgrade
```

## Using the API

### 1. Start the Server

```bash
cd backend1
python run.py
```

### 2. Login to Get JWT Token

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "your_password"}'
```

Save the `access_token` from the response.

### 3. Scrape a Company

```bash
curl -X POST http://localhost:5000/api/companies/scrape \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"slug": "apple-inc"}'
```

### 4. List Companies

```bash
curl http://localhost:5000/api/companies \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 5. Get Company Details with Reports

```bash
curl http://localhost:5000/api/companies/1 \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 6. Create Compliance Report Linked to Company

```bash
curl -X POST http://localhost:5000/api/reports \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "title": "Apple Q1 2024 Compliance Review",
    "report_type": "compliance",
    "company_id": 1,
    "source_annual_report_id": 1,
    "status": "draft",
    "priority": "medium"
  }'
```

## Popular Company Slugs

Here are some company slugs you can try:

- `apple-inc` - Apple Inc. (AAPL)
- `microsoft-corp` - Microsoft Corporation (MSFT)
- `amazon-com-inc` - Amazon.com Inc. (AMZN)
- `google-inc` - Google/Alphabet (GOOG)
- `tesla-inc` - Tesla Inc. (TSLA)
- `meta-platforms-inc` - Meta/Facebook (META)

## Searching for Companies

If you don't know the slug:

```bash
curl "http://localhost:5000/api/companies/search?q=Tesla" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

This returns the slug you need to scrape.

## Integration with Compliance Reports

Once companies are scraped, you can:

1. **Link existing reports** to companies:
   ```bash
   curl -X PUT http://localhost:5000/api/reports/1 \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -d '{"company_id": 1}'
   ```

2. **Filter reports by company**:
   ```bash
   curl "http://localhost:5000/api/reports?company_id=1" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE"
   ```

## Data Structure

Each scraped company includes:
- Company profile (name, ticker, industry, sector)
- Official website
- 20-30 years of annual reports
- Direct PDF download links

Example report object:
```json
{
  "year": 2023,
  "title": "2023 Annual Report",
  "pdf_url": "https://www.annualreports.com/HostedData/.../NASDAQ_AAPL_2023.pdf",
  "report_type": "Annual Report"
}
```

## Next Steps

See [walkthrough.md](file:///C:/Users/osman/.gemini/antigravity/brain/f75e5a4a-08e0-4e7d-8997-f48098df268e/walkthrough.md) for full implementation details and [implementation_plan.md](file:///C:/Users/osman/.gemini/antigravity/brain/f75e5a4a-08e0-4e7d-8997-f48098df268e/implementation_plan.md) for the complete plan.
