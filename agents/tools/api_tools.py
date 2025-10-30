"""
LangChain tools for interacting with the Cobank API.

This module provides LangChain-compatible tools for querying branches,
deposit schemes, and loan schemes from the Cobank API.
"""

import json
from typing import Dict, Any, Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from agents.tools.api_client import CobankAPIClient


class BranchSearchInput(BaseModel):
    """Input schema for branch search tool."""
    bcode: Optional[str] = Field(None, description="Branch code")
    name: Optional[str] = Field(None, description="Branch name")
    city: Optional[str] = Field(None, description="City name")
    pin: Optional[str] = Field(None, description="PIN code")
    status: Optional[str] = Field(None, description="Branch status (Active/Inactive)")


class BranchSearchTool(BaseTool):
    """Tool for searching branches in the Cobank system."""
    
    name: str = "search_branches"
    description: str = """
    Search for bank branches based on various criteria.
    Use this when users ask about:
    - Branch locations
    - Branch addresses
    - Finding branches in a specific city
    - Branch codes or names
    - Active or inactive branches
    
    Provide filters like branch code, name, city, PIN code, or status to narrow results.
    """
    args_schema: type[BaseModel] = BranchSearchInput
    
    def _run(
        self,
        bcode: Optional[str] = None,
        name: Optional[str] = None,
        city: Optional[str] = None,
        pin: Optional[str] = None,
        status: Optional[str] = None
    ) -> str:
        """Execute the branch search."""
        try:
            client = CobankAPIClient()
            
            # Build filters dict, only including non-None values
            filters = {}
            if bcode:
                filters["bcode"] = bcode
            if name:
                filters["name"] = name
            if city:
                filters["city"] = city
            if pin:
                filters["pin"] = pin
            if status:
                filters["status"] = status
            
            results = client.search_branches(filters if filters else None)
            
            if not results:
                return "No branches found matching the criteria."
            
            # Limit results to prevent context overflow
            if len(results) > 20:
                limited_results = results[:20]
                return json.dumps({
                    "results": limited_results,
                    "total_count": len(results),
                    "showing": "first 20 results",
                    "note": f"Showing 20 out of {len(results)} total branches. Add more specific filters to narrow results."
                }, indent=2)
            
            return json.dumps(results, indent=2)
        except Exception as e:
            return f"Error searching branches: {str(e)}"


class DepositSchemeSearchInput(BaseModel):
    """Input schema for deposit scheme search tool."""
    actype: Optional[str] = Field(None, description="Account type (SB, RD, FD, MIS)")
    name: Optional[str] = Field(None, description="Scheme name")
    tenure: Optional[float] = Field(None, description="Tenure period")
    tunit: Optional[str] = Field(None, description="Tenure unit (Year/Month)")
    status: Optional[str] = Field(None, description="Scheme status (Running/Closed)")


class DepositSchemeSearchTool(BaseTool):
    """Tool for searching deposit schemes in the Cobank system."""
    
    name: str = "search_deposit_schemes"
    description: str = """
    Search for deposit schemes (Savings, Recurring Deposits, Fixed Deposits, MIS).
    Use this when users ask about:
    - Deposit account types
    - Interest rates on deposits
    - Fixed deposit schemes
    - Recurring deposit options
    - Savings account details
    - MIS (Monthly Income Scheme) plans
    - Deposit tenure and interest rates
    
    Provide filters like account type (SB/RD/FD/MIS), scheme name, tenure, or status.
    """
    args_schema: type[BaseModel] = DepositSchemeSearchInput
    
    def _run(
        self,
        actype: Optional[str] = None,
        name: Optional[str] = None,
        tenure: Optional[float] = None,
        tunit: Optional[str] = None,
        status: Optional[str] = None
    ) -> str:
        """Execute the deposit scheme search."""
        try:
            client = CobankAPIClient()
            
            # Build filters dict, only including non-None values
            filters = {}
            if actype:
                filters["actype"] = actype
            if name:
                filters["name"] = name
            if tenure is not None:
                filters["tenure"] = tenure
            if tunit:
                filters["tunit"] = tunit
            if status:
                filters["status"] = status
            
            results = client.search_deposit_schemes(filters if filters else None)
            
            if not results:
                return "No deposit schemes found matching the criteria."
            
            # Limit results to prevent context overflow
            if len(results) > 15:
                limited_results = results[:15]
                return json.dumps({
                    "results": limited_results,
                    "total_count": len(results),
                    "showing": "first 15 results",
                    "note": f"Showing 15 out of {len(results)} total schemes. Add more specific filters (like actype: FD/RD/SB/MIS) to narrow results."
                }, indent=2)
            
            return json.dumps(results, indent=2)
        except Exception as e:
            return f"Error searching deposit schemes: {str(e)}"


class LoanSchemeSearchInput(BaseModel):
    """Input schema for loan scheme search tool."""
    name: Optional[str] = Field(None, description="Loan scheme name")
    category: Optional[str] = Field(None, description="Loan category (Secured/Unsecured)")
    tenure: Optional[int] = Field(None, description="Loan tenure in months")
    interesttype: Optional[str] = Field(None, description="Interest type (Flat/Reducing)")
    status: Optional[str] = Field(None, description="Scheme status (Running/Closed)")


class LoanSchemeSearchTool(BaseTool):
    """Tool for searching loan schemes in the Cobank system."""
    
    name: str = "search_loan_schemes"
    description: str = """
    Search for loan schemes available in the bank.
    Use this when users ask about:
    - Loan types and options
    - Loan interest rates
    - Secured vs unsecured loans
    - Loan tenure and amounts
    - Personal loan schemes
    - Home loan schemes
    - Vehicle loan schemes
    - Education loan schemes
    
    Provide filters like scheme name, category (Secured/Unsecured), tenure, or status.
    """
    args_schema: type[BaseModel] = LoanSchemeSearchInput
    
    def _run(
        self,
        name: Optional[str] = None,
        category: Optional[str] = None,
        tenure: Optional[int] = None,
        interesttype: Optional[str] = None,
        status: Optional[str] = None
    ) -> str:
        """Execute the loan scheme search."""
        try:
            client = CobankAPIClient()
            
            # Build filters dict, only including non-None values
            filters = {}
            if name:
                filters["name"] = name
            if category:
                filters["category"] = category
            if tenure is not None:
                filters["tenure"] = tenure
            if interesttype:
                filters["interesttype"] = interesttype
            if status:
                filters["status"] = status
            
            results = client.search_loan_schemes(filters if filters else None)
            
            if not results:
                return "No loan schemes found matching the criteria."
            
            # Limit results to prevent context overflow
            if len(results) > 15:
                limited_results = results[:15]
                return json.dumps({
                    "results": limited_results,
                    "total_count": len(results),
                    "showing": "first 15 results",
                    "note": f"Showing 15 out of {len(results)} total schemes. Add more specific filters (like category: Secured/Unsecured) to narrow results."
                }, indent=2)
            
            return json.dumps(results, indent=2)
        except Exception as e:
            return f"Error searching loan schemes: {str(e)}"


class MemberSearchInput(BaseModel):
    """Input schema for member search tool."""
    memberno: Optional[int] = Field(None, description="Member number")
    name: Optional[str] = Field(None, description="Member name")
    mobile: Optional[str] = Field(None, description="Mobile number")
    pan: Optional[str] = Field(None, description="PAN card number")
    aadhar: Optional[str] = Field(None, description="Aadhar number")
    status: Optional[str] = Field(None, description="Member status (New/Member/Canceled)")
    start_date: Optional[str] = Field(None, description="Start date for date range filter (YYYY-MM-DD format)")
    end_date: Optional[str] = Field(None, description="End date for date range filter (YYYY-MM-DD format)")


class MemberSearchTool(BaseTool):
    """Tool for searching members in the Cobank system."""
    
    name: str = "search_members"
    description: str = """
    Search for bank members/customers based on various criteria.
    Use this when users ask about:
    - Finding member details
    - Member information by name, number, or ID
    - Member status (new, active, canceled)
    - Searching by contact details (mobile)
    - Looking up by PAN or Aadhar
    - Members created within a date range
    
    Provide filters like member number, name, mobile, PAN, Aadhar, status, or date range.
    For date filters, use start_date and end_date in YYYY-MM-DD format.
    """
    args_schema: type[BaseModel] = MemberSearchInput
    
    def _run(
        self,
        memberno: Optional[int] = None,
        name: Optional[str] = None,
        mobile: Optional[str] = None,
        pan: Optional[str] = None,
        aadhar: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> str:
        """Execute the member search."""
        try:
            client = CobankAPIClient()
            
            # Build filters dict, only including non-None values
            filters = {}
            if memberno is not None:
                filters["memberno"] = memberno
            if name:
                filters["name"] = name
            if mobile:
                filters["mobile"] = mobile
            if pan:
                filters["pan"] = pan
            if aadhar:
                filters["aadhar"] = aadhar
            if status:
                filters["status"] = status
            
            # Add date range filters if provided
            if start_date:
                filters["start"] = start_date
            if end_date:
                filters["end"] = end_date
            
            results = client.search_members(filters if filters else None)
            
            if not results:
                return "No members found matching the criteria."
            
            # Limit results to prevent context overflow
            if len(results) > 10:
                limited_results = results[:10]
                return json.dumps({
                    "results": limited_results,
                    "total_count": len(results),
                    "showing": "first 10 results",
                    "note": f"Showing 10 out of {len(results)} total members. Add more specific filters (like memberno or mobile) to narrow results."
                }, indent=2)
            
            return json.dumps(results, indent=2)
        except Exception as e:
            return f"Error searching members: {str(e)}"


class MemberCountInput(BaseModel):
    """Input schema for member count tool."""
    status: Optional[str] = Field(None, description="Member status to count (New/Member/Canceled)")
    mtype: Optional[str] = Field(None, description="Member type (Share/Nominal)")
    start_date: Optional[str] = Field(None, description="Start date for date range filter (YYYY-MM-DD format)")
    end_date: Optional[str] = Field(None, description="End date for date range filter (YYYY-MM-DD format)")


class MemberCountTool(BaseTool):
    """Tool for counting members in the Cobank system."""
    
    name: str = "count_members"
    description: str = """
    Count total members based on filters.
    Use this when users ask about:
    - How many members are there
    - Total member count
    - Number of active/new/canceled members
    - Member statistics
    - Members created within a date range
    
    Provide filters like status, member type, or date range to get specific counts.
    For date filters, use start_date and end_date in YYYY-MM-DD format.
    """
    args_schema: type[BaseModel] = MemberCountInput
    
    def _run(
        self,
        status: Optional[str] = None,
        mtype: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> str:
        """Execute the member count."""
        try:
            client = CobankAPIClient()
            
            # Build filters dict
            filters = {}
            if status:
                filters["status"] = status
            if mtype:
                filters["mtype"] = mtype
            
            # Add date range filters if provided
            if start_date:
                filters["start"] = start_date
            if end_date:
                filters["end"] = end_date
            
            # Use the search endpoint and count results
            results = client.search_members(filters if filters else None)
            count = len(results)
            
            filter_desc = []
            if status:
                filter_desc.append(f"status: {status}")
            if mtype:
                filter_desc.append(f"type: {mtype}")
            if start_date or end_date:
                date_range = []
                if start_date:
                    date_range.append(f"from {start_date}")
                if end_date:
                    date_range.append(f"to {end_date}")
                filter_desc.append(" ".join(date_range))
            
            if filter_desc:
                return f"Total members ({', '.join(filter_desc)}): {count}"
            else:
                return f"Total members: {count}"
        except Exception as e:
            return f"Error counting members: {str(e)}"


class AccountSearchInput(BaseModel):
    """Input schema for account search tool."""
    memberno: Optional[str] = Field(None, description="Member number")
    accountno: Optional[str] = Field(None, description="Account number")
    actype: Optional[str] = Field(None, description="Account type (SB/RD/FD/MIS)")
    status: Optional[str] = Field(None, description="Account status (Applied/New/Running/Matured/Closed)")
    start_date: Optional[str] = Field(None, description="Start date for date range filter (YYYY-MM-DD format)")
    end_date: Optional[str] = Field(None, description="End date for date range filter (YYYY-MM-DD format)")


class AccountSearchTool(BaseTool):
    """Tool for searching accounts in the Cobank system."""
    
    name: str = "search_accounts"
    description: str = """
    Search for customer accounts based on various criteria.
    Use this when users ask about:
    - Account details by account number
    - Accounts belonging to a member
    - Account types (Savings, RD, FD, MIS)
    - Account status (running, matured, closed)
    - Finding specific accounts
    - Accounts created within a date range
    
    Provide filters like account number, member number, account type, status, or date range.
    For date filters, use start_date and end_date in YYYY-MM-DD format.
    """
    args_schema: type[BaseModel] = AccountSearchInput
    
    def _run(
        self,
        memberno: Optional[str] = None,
        accountno: Optional[str] = None,
        actype: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> str:
        """Execute the account search."""
        try:
            client = CobankAPIClient()
            
            # Build filters dict
            filters = {}
            if memberno:
                filters["memberno"] = memberno
            if accountno:
                filters["accountno"] = accountno
            if actype:
                filters["actype"] = actype
            if status:
                filters["status"] = status
            
            # Add date range filters if provided
            if start_date:
                filters["start"] = start_date
            if end_date:
                filters["end"] = end_date
            
            results = client.search_accounts(filters if filters else None)
            
            if not results:
                return "No accounts found matching the criteria."
            
            # Limit results to prevent context overflow
            if len(results) > 15:
                limited_results = results[:15]
                return json.dumps({
                    "results": limited_results,
                    "total_count": len(results),
                    "showing": "first 15 results",
                    "note": f"Showing 15 out of {len(results)} total accounts. Add more specific filters (like accountno or memberno) to narrow results."
                }, indent=2)
            
            return json.dumps(results, indent=2)
        except Exception as e:
            return f"Error searching accounts: {str(e)}"


class AccountCountInput(BaseModel):
    """Input schema for account count tool."""
    actype: Optional[str] = Field(None, description="Account type (SB/RD/FD/MIS)")
    status: Optional[str] = Field(None, description="Account status (Applied/New/Running/Matured/Closed)")
    start_date: Optional[str] = Field(None, description="Start date for date range filter (YYYY-MM-DD format)")
    end_date: Optional[str] = Field(None, description="End date for date range filter (YYYY-MM-DD format)")


class AccountCountTool(BaseTool):
    """Tool for counting accounts in the Cobank system."""
    
    name: str = "count_accounts"
    description: str = """
    Count total accounts based on filters.
    Use this when users ask about:
    - How many accounts are there
    - Total account count
    - Number of accounts by type or status
    - Account statistics
    - Accounts created within a date range
    
    Provide filters like account type, status, or date range to get specific counts.
    For date filters, use start_date and end_date in YYYY-MM-DD format.
    """
    args_schema: type[BaseModel] = AccountCountInput
    
    def _run(
        self,
        actype: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> str:
        """Execute the account count."""
        try:
            client = CobankAPIClient()
            
            # Build filters dict
            filters = {}
            if actype:
                filters["actype"] = actype
            if status:
                filters["status"] = status
            
            # Add date range filters if provided
            if start_date:
                filters["start"] = start_date
            if end_date:
                filters["end"] = end_date
            
            # Use the search endpoint and count results
            results = client.search_accounts(filters if filters else None)
            count = len(results)
            
            filter_desc = []
            if actype:
                filter_desc.append(f"type: {actype}")
            if status:
                filter_desc.append(f"status: {status}")
            if start_date or end_date:
                date_range = []
                if start_date:
                    date_range.append(f"from {start_date}")
                if end_date:
                    date_range.append(f"to {end_date}")
                filter_desc.append(" ".join(date_range))
            
            if filter_desc:
                return f"Total accounts ({', '.join(filter_desc)}): {count}"
            else:
                return f"Total accounts: {count}"
        except Exception as e:
            return f"Error counting accounts: {str(e)}"


class AvailableBalanceInput(BaseModel):
    """Input schema for available balance tool."""
    accountno: str = Field(..., description="Account number to check balance")


class AvailableBalanceTool(BaseTool):
    """Tool for getting available balance of an account."""
    
    name: str = "get_available_balance"
    description: str = """
    Get the current available balance for a specific account.
    Use this when users ask about:
    - Account balance
    - How much money is in an account
    - Current balance
    - Available funds
    - Check balance for account number
    
    Requires the account number as input.
    """
    args_schema: type[BaseModel] = AvailableBalanceInput
    
    def _run(self, accountno: str) -> str:
        """Execute the balance check."""
        try:
            client = CobankAPIClient()
            
            # Get balance information
            result = client.get_available_balance(client.ocode, accountno)
            
            # Extract balance from response
            if isinstance(result, dict):
                balance = float(result.get("cbalance", 0))
                tdate = result.get("tdate", "N/A")
                return f"Available balance for account {accountno}: ₹{balance:,.2f} (as of {tdate[:10]})"
            else:
                return f"Available balance for account {accountno}: ₹{float(result):,.2f}"
        except Exception as e:
            return f"Error getting balance for account {accountno}: {str(e)}"


# Export all tools
def get_api_tools() -> list[BaseTool]:
    """Get all API tools for use in LangChain agents."""
    return [
        BranchSearchTool(),
        DepositSchemeSearchTool(),
        LoanSchemeSearchTool(),
        MemberSearchTool(),
        MemberCountTool(),
        AccountSearchTool(),
        AccountCountTool(),
        AvailableBalanceTool(),
    ]
