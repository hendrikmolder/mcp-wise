# Invoice Creation Examples

This document provides examples of how to use the new invoice creation tools in the Wise MCP server.

## Example 1: Simple Invoice

```python
# First, get available balance currencies
get_balance_currencies(profile_type="personal")

# Create a simple invoice with one line item
create_invoice(
    profile_type="personal",
    balance_id=12345,  # Use the balance ID from get_balance_currencies
    due_days=30,
    line_items=[
        {
            "name": "Consulting Services",
            "amount": 1000.00,
            "currency": "EUR",
            "quantity": 1
        }
    ],
    payer_name="John Doe",
    payer_email="john@example.com",
    invoice_number="INV-001",
    message="Thank you for your business!"
)
```

## Example 2: Invoice with Multiple Line Items and Tax

```python
create_invoice(
    profile_type="business",
    balance_id=67890,
    due_days=15,
    line_items=[
        {
            "name": "Web Development",
            "amount": 2500.00,
            "currency": "USD",
            "quantity": 1,
            "tax_name": "VAT",
            "tax_percentage": 20.0,
            "tax_behaviour": "EXCLUDED"
        },
        {
            "name": "Domain Registration",
            "amount": 15.00,
            "currency": "USD",
            "quantity": 2,
            "tax_name": "VAT",
            "tax_percentage": 20.0,
            "tax_behaviour": "EXCLUDED"
        }
    ],
    payer_name="Acme Corporation",
    payer_email="accounting@acme.com",
    invoice_number="INV-2025-001",
    message="Payment terms: Net 15 days",
    issue_date="2025-07-01"
)
```

## Example 3: Invoice with Contact ID

```python
# If you have a contact ID from your Wise account
create_invoice(
    profile_type="personal",
    balance_id=12345,
    due_days=7,
    line_items=[
        {
            "name": "Freelance Writing",
            "amount": 500.00,
            "currency": "GBP",
            "quantity": 5  # 5 articles
        }
    ],
    payer_contact_id="contact_123456",  # Existing contact in Wise
    invoice_number="FREELANCE-001"
)
```

## Getting Balance Information

Before creating an invoice, you need to know which balance to use. Use the `get_balance_currencies` tool:

```python
# This will return something like:
# Available balances for invoice creation:
# • Currency: EUR, Balance ID: 12345
# • Currency: USD, Balance ID: 67890
# • Currency: GBP, Balance ID: 11111

get_balance_currencies(profile_type="personal")
```

## Tax Behaviors

When adding tax to line items, you can specify the tax behavior:

- `"INCLUDED"`: Tax is included in the unit price
- `"EXCLUDED"`: Tax is added on top of the unit price

## Response Format

Successful invoice creation will return:
```
Invoice created successfully! ID: req_abc123, Status: DRAFT, Link: https://wise.com/pay/req_abc123
```

The invoice will be created in DRAFT status and can be published through the Wise web interface.
