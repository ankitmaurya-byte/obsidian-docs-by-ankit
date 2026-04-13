# workflow 
```
START
  │
  ▼
Segregator Agent (Claude Vision)
  │  Classifies every page into 9 doc types
  │
  ├──────────────────────────────┐
  ▼                              ▼                    ▼
ID Agent              Discharge Agent         Bill Agent
(identity_document    (discharge_summary)     (itemized_bill +
 + claim_forms)                                cash_receipt)
  │                              │                    │
  └──────────────────────────────┘────────────────────┘
                                 │
                                 ▼
                           Aggregator
                                 │
                                 ▼
                               END (JSON)
                               
```

# How to use this 
```
Step 1 — Set up your project folder
bashmkdir claim-processor && cd claim-processor
Step 2 — Add your PDF
bashcp /path/to/__final_image_protected.pdf__ .
Step 3 — Run the Claude Code prompt
Paste the giant prompt above into your terminal (inside the claim-processor dir). Claude Code will scaffold everything.
Step 4 — Set your API key
bashcp .env.example .env
# Edit .env and add: ANTHROPIC_API_KEY=sk-ant-...
Step 5 — Test it
bashcurl -X POST http://localhost:8000/api/process \
  -F "claim_id=CLAIM-001" \
  -F "file=@__final_image_protected.pdf__"
```
# Claude code Cli Prompt
```js

claude "Build a production-ready FastAPI + LangGraph claim processing pipeline. Here is the complete spec:

## PROJECT STRUCTURE
Create this layout:
claim-processor/
├── main.py
├── graph/
│   ├── __init__.py
│   ├── workflow.py        # LangGraph graph definition
│   ├── state.py           # TypedDict state schema
│   └── nodes/
│       ├── __init__.py
│       ├── segregator.py  # AI-powered page classifier
│       ├── id_agent.py
│       ├── discharge_agent.py
│       ├── bill_agent.py
│       └── aggregator.py
├── utils/
│   ├── __init__.py
│   └── pdf_utils.py       # PDF page extraction helpers
├── requirements.txt
├── .env.example
└── README.md

## DEPENDENCIES (requirements.txt)
fastapi
uvicorn[standard]
langgraph
langchain-anthropic
langchain-core
pypdf2
pdf2image
anthropic
python-multipart
pillow
python-dotenv

## STATE SCHEMA (graph/state.py)
Define a TypedDict ClaimState with:
- claim_id: str
- pdf_bytes: bytes
- total_pages: int
- page_classification: dict[int, str]  # page_num -> doc_type
- pages_by_type: dict[str, list[int]]  # doc_type -> [page_nums]
- id_extraction: dict
- discharge_extraction: dict
- bill_extraction: dict
- final_output: dict
- errors: list[str]

## SEGREGATOR NODE (graph/nodes/segregator.py)
- Use Claude claude-sonnet-4-20250514 via langchain-anthropic ChatAnthropic
- Convert each PDF page to base64 image using pdf2image + PIL
- Send ALL pages to Claude in a single call with vision, asking it to classify each page into one of these 9 types:
  claim_forms, cheque_or_bank_details, identity_document, itemized_bill,
  discharge_summary, prescription, investigation_report, cash_receipt, other
- Ask Claude to return ONLY valid JSON: {"page_classifications": {"1": "identity_document", "2": "itemized_bill", ...}}
- Parse the JSON response and populate state.page_classification and state.pages_by_type
- Log which pages went to which category

## ID AGENT NODE (graph/nodes/id_agent.py)
- Receives only pages classified as 'identity_document' or 'claim_forms'
- Extract those specific pages from the PDF as images (base64)
- Send to Claude with prompt to extract:
  {
    "patient_name": "",
    "date_of_birth": "",
    "gender": "",
    "id_numbers": {"aadhar": "", "pan": "", "voter_id": ""},
    "policy_number": "",
    "policy_holder_name": "",
    "insurance_company": "",
    "claim_number": "",
    "contact": {"phone": "", "address": "", "email": ""}
  }
- Return structured dict, handle missing fields gracefully with null

## DISCHARGE SUMMARY AGENT (graph/nodes/discharge_agent.py)
- Receives only pages classified as 'discharge_summary'
- Extract:
  {
    "patient_name": "",
    "admission_date": "",
    "discharge_date": "",
    "length_of_stay_days": null,
    "hospital_name": "",
    "ward_type": "",
    "primary_diagnosis": "",
    "secondary_diagnoses": [],
    "procedures_performed": [],
    "attending_physician": "",
    "physician_registration_no": "",
    "discharge_condition": "",
    "follow_up_instructions": ""
  }
- If no discharge summary pages exist, return empty dict with a note

## ITEMIZED BILL AGENT (graph/nodes/bill_agent.py)
- Receives only pages classified as 'itemized_bill' or 'cash_receipt'
- Extract:
  {
    "hospital_name": "",
    "bill_date": "",
    "bill_number": "",
    "line_items": [
      {"description": "", "quantity": null, "unit_price": null, "amount": null, "category": ""}
    ],
    "subtotal": null,
    "taxes": null,
    "discounts": null,
    "total_amount": null,
    "amount_paid": null,
    "amount_due": null,
    "payment_mode": ""
  }
- Calculate and verify total_amount by summing line_items amounts
- If calculated total differs from stated total, include both

## AGGREGATOR NODE (graph/nodes/aggregator.py)
- Combine all three extraction results into final_output:
  {
    "claim_id": "",
    "processing_summary": {
      "total_pages": 0,
      "pages_by_document_type": {},
      "agents_invoked": []
    },
    "identity_information": {},
    "discharge_summary": {},
    "bill_details": {},
    "metadata": {
      "processed_at": "",
      "model_used": "claude-sonnet-4-20250514"
    }
  }

## LANGGRAPH WORKFLOW (graph/workflow.py)
Build this exact conditional routing graph:
- START → segregator_node
- segregator_node → id_agent, discharge_agent, bill_agent (all three run in parallel using Send API or sequential)
- id_agent → aggregator
- discharge_agent → aggregator
- bill_agent → aggregator
- aggregator → END

Use StateGraph from langgraph.graph. If LangGraph version supports it, use parallel fan-out with Send. Otherwise run sequentially: segregator → id → discharge → bill → aggregator.

## FASTAPI APP (main.py)
- POST /api/process
  - Accepts: claim_id (Form field), file (UploadFile PDF)
  - Validates file is PDF
  - Reads file bytes
  - Initializes ClaimState and invokes the compiled LangGraph
  - Returns JSONResponse with final_output
  - Proper error handling with HTTP exceptions

- GET /health → {"status": "ok"}
- GET / → {"message": "Claim Processing API", "docs": "/docs"}

## PDF UTILS (utils/pdf_utils.py)
- extract_page_as_base64_image(pdf_bytes, page_num) -> str
  Uses pdf2image to convert specific page to PIL Image, then base64 encode as JPEG
- extract_pages_as_base64_images(pdf_bytes, page_nums) -> list[str]
  Batch version
- get_pdf_page_count(pdf_bytes) -> int

## ENV CONFIG
- ANTHROPIC_API_KEY required
- Read via python-dotenv
- Add validation on startup

## README.md
Include:
1. Setup instructions (pip install, .env setup)
2. How to run: uvicorn main:app --reload
3. Example curl command to test the /api/process endpoint
4. LangGraph workflow diagram in ASCII
5. Description of each agent

## IMPORTANT IMPLEMENTATION NOTES
- Handle PDFs with no pages for a given doc type gracefully (agent returns empty dict)
- All Claude API calls must include error handling with retries on rate limits
- Log each step clearly with print statements showing progress
- The segregator must work even if pdf2image has issues - fallback to text extraction via PyPDF2
- Use model claude-sonnet-4-20250514 for all LLM calls
- Ensure the app runs with: uvicorn main:app --host 0.0.0.0 --port 8000

After creating all files, install dependencies and verify the app starts without errors by running: uvicorn main:app --host 0.0.0.0 --port 8000 --timeout-keep-alive 120 and confirm it is listening."
```