"""
Wise API invoice creation resource for the FastMCP server.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from wise_mcp.app import mcp
from wise_mcp.api.wise_client_helper import init_wise_client
from wise_mcp.api.types import (
    PaymentRequestInvoiceCommand,
    PayerV2,
    LineItem,
    Money,
    LineItemTax
)


@mcp.tool()
def create_invoice(
    profile_type: str,
    balance_id: int,
    due_days: int,
    line_items: List[Dict[str, Any]],
    payer_name: Optional[str] = None,
    payer_email: Optional[str] = None,
    payer_contact_id: Optional[str] = None,
    invoice_number: Optional[str] = None,
    message: Optional[str] = None,
    issue_date: Optional[str] = None
) -> str:
    """
    Create an invoice payment request using the Wise API.

    Args:
        profile_type: The type of profile to use (personal or business)
        balance_id: The ID of the balance to use for the invoice
        due_days: Number of days from today when the invoice is due
        line_items: List of line items, each containing:
            - name: Name/description of the item
            - amount: Unit price amount
            - currency: Currency code (e.g., 'EUR', 'USD')
            - quantity: Quantity of the item
            - tax_name: Optional tax name
            - tax_percentage: Optional tax percentage (0-100)
            - tax_behaviour: Optional tax behaviour ("INCLUDED" or "EXCLUDED")
        payer_name: Optional name of the payer
        payer_email: Optional email of the payer
        payer_contact_id: Optional contact ID of the payer
        invoice_number: Optional invoice number
        message: Optional message to include with the invoice
        issue_date: Optional issue date in YYYY-MM-DD format (defaults to today)

    Returns:
        String message with invoice creation status and link

    Raises:
        Exception: If any API request fails during the process
    """

    ctx = init_wise_client(profile_type)
    
    # Calculate due date
    due_date = (datetime.now() + timedelta(days=due_days)).strftime("%Y-%m-%d")
    
    # Use today as issue date if not provided
    if not issue_date:
        issue_date = datetime.now().strftime("%Y-%m-%d")
    
    # Build payer information
    payer = None
    if payer_name or payer_email or payer_contact_id:
        payer = PayerV2(
            contact_id=payer_contact_id,
            name=payer_name,
            email=payer_email
        )
    
    # Convert line items
    converted_line_items = []
    for item in line_items:
        # Create the money object for unit price
        unit_price = Money(
            amount=float(item["amount"]),
            currency=item["currency"]
        )
        
        # Create tax object if tax information is provided
        tax = None
        if item.get("tax_name") and item.get("tax_percentage") is not None:
            tax = LineItemTax(
                name=item["tax_name"],
                percentage=float(item["tax_percentage"]),
                behaviour=item.get("tax_behaviour", "INCLUDED")
            )
        
        converted_line_items.append(LineItem(
            name=item["name"],
            unit_price=unit_price,
            quantity=int(item["quantity"]),
            tax=tax
        ))
    
    # Create the payment request command
    payment_request = PaymentRequestInvoiceCommand(
        balance_id=balance_id,
        due_at=due_date,
        invoice_number=invoice_number,
        payer=payer,
        line_items=converted_line_items,
        issue_date=issue_date,
        message=message
    )
    
    try:
        # Create the invoice
        result = ctx.wise_api_client.create_payment_request_v2(
            profile_id=ctx.profile.profile_id,
            payment_request=payment_request
        )
        
        return f"Invoice created successfully! ID: {result.id}, Status: {result.status}, Link: {result.link or 'N/A'}"
        
    except Exception as error:
        return f"Failed to create invoice: {str(error)}"


@mcp.tool()
def get_balance_currencies(profile_type: str) -> str:
    """
    Get available currencies and balance IDs for creating invoices.

    Args:
        profile_type: The type of profile to use (personal or business)

    Returns:
        String with formatted list of available balances and their IDs

    Raises:
        Exception: If the API request fails
    """
    
    ctx = init_wise_client(profile_type)
    
    try:
        # Get balance currencies
        currencies = ctx.wise_api_client.get_balance_currencies(ctx.profile.profile_id)
        
        if not currencies.get("balances"):
            return "No balances found for this profile."
        
        result = "Available balances for invoice creation:\n\n"
        for balance in currencies["balances"]:
            result += f"• Currency: {balance['currency']}, Balance ID: {balance['id']}\n"
        
        return result
        
    except Exception as error:
        return f"Failed to get balance currencies: {str(error)}"
