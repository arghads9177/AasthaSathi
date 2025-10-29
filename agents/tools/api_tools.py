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


# Export all tools
def get_api_tools() -> list[BaseTool]:
    """Get all API tools for use in LangChain agents."""
    return [
        BranchSearchTool(),
        DepositSchemeSearchTool(),
        LoanSchemeSearchTool(),
    ]
