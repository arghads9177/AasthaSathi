"""
API Agent for handling real-time banking data queries.

This module implements a LangGraph-based agent that uses API tools to answer
queries about branches, deposit schemes, loan schemes, and other real-time data.
"""

from typing import Annotated, Literal, TypedDict, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages

from core.config import Settings
from agents.tools.api_tools import get_api_tools


# Load settings
settings = Settings()


class APIAgentState(TypedDict):
    """State for the API agent."""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    query: str
    error: str | None


class APIAgent:
    """Agent for handling API-based queries using LangGraph."""
    
    def __init__(self, model_name: str = None, temperature: float = 0.1):
        """
        Initialize the API agent.
        
        Args:
            model_name: LLM model to use (defaults to settings)
            temperature: Temperature for LLM responses
        """
        self.model_name = model_name or settings.default_model
        self.temperature = temperature
        
        # Get API tools
        self.tools = get_api_tools()
        
        # Initialize LLM with tools
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            api_key=settings.openai_api_key
        ).bind_tools(self.tools)
        
        # Create the graph
        self.graph = self._create_graph()
        self.app = self.graph.compile()
    
    def _create_graph(self) -> StateGraph:
        """Create the LangGraph workflow."""
        
        # Define the graph
        workflow = StateGraph(APIAgentState)
        
        # Add nodes
        workflow.add_node("agent", self._agent_node)
        workflow.add_node("tools", ToolNode(self.tools))
        
        # Set entry point
        workflow.set_entry_point("agent")
        
        # Add edges
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": END,
            }
        )
        workflow.add_edge("tools", "agent")
        
        return workflow
    
    def _agent_node(self, state: APIAgentState) -> APIAgentState:
        """
        Agent node that calls the LLM.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with agent response
        """
        try:
            messages = state["messages"]
            response = self.llm.invoke(messages)
            return {"messages": [response]}
        except Exception as e:
            error_msg = f"Agent error: {str(e)}"
            return {
                "messages": [AIMessage(content=f"I encountered an error: {error_msg}")],
                "error": error_msg
            }
    
    def _should_continue(self, state: APIAgentState) -> Literal["continue", "end"]:
        """
        Determine if the agent should continue or end.
        
        Args:
            state: Current agent state
            
        Returns:
            "continue" if tools should be called, "end" otherwise
        """
        messages = state["messages"]
        last_message = messages[-1]
        
        # If there are tool calls, continue
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "continue"
        
        # Otherwise, end
        return "end"
    
    def query(self, query: str, api_queries: list[str] = None) -> dict:
        """
        Process a query using the API agent.
        
        Args:
            query: User query
            api_queries: Optional specific API queries to make
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            # Construct the prompt
            if api_queries:
                prompt = f"""Answer the following query using the available API tools.

User Query: {query}

Specific API queries to make:
{chr(10).join(f"- {q}" for q in api_queries)}

Use the appropriate tools to fetch the required data and provide a comprehensive answer.

IMPORTANT: This is an Indian banking system. All monetary amounts should be displayed in INR (Indian Rupees) using the ₹ symbol, not in dollars ($)."""
            else:
                prompt = f"""Answer the following query using the available API tools.

User Query: {query}

Use the appropriate tools to fetch the required data and provide a comprehensive answer.

IMPORTANT: This is an Indian banking system. All monetary amounts should be displayed in INR (Indian Rupees) using the ₹ symbol, not in dollars ($)."""
            
            # Initialize state
            initial_state = {
                "messages": [HumanMessage(content=prompt)],
                "query": query,
                "error": None
            }
            
            # Run the agent
            result = self.app.invoke(initial_state)
            
            # Extract the final response
            final_message = result["messages"][-1]
            
            # Check if there was an error
            if result.get("error"):
                return {
                    "success": False,
                    "response": final_message.content,
                    "error": result["error"],
                    "query": query
                }
            
            return {
                "success": True,
                "response": final_message.content,
                "query": query,
                "api_queries": api_queries or []
            }
            
        except Exception as e:
            return {
                "success": False,
                "response": f"Failed to process query: {str(e)}",
                "error": str(e),
                "query": query
            }
    
    def query_with_context(self, query: str, context: str) -> dict:
        """
        Process a query with additional context.
        
        Args:
            query: User query
            context: Additional context (e.g., from RAG)
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            prompt = f"""Answer the following query using both the provided context and available API tools.

User Query: {query}

Context from knowledge base:
{context}

Use the API tools to fetch any additional real-time data needed, and combine it with the context to provide a comprehensive answer.

IMPORTANT: This is an Indian banking system. All monetary amounts should be displayed in INR (Indian Rupees) using the ₹ symbol, not in dollars ($)."""
            
            # Initialize state
            initial_state = {
                "messages": [HumanMessage(content=prompt)],
                "query": query,
                "error": None
            }
            
            # Run the agent
            result = self.app.invoke(initial_state)
            
            # Extract the final response
            final_message = result["messages"][-1]
            
            return {
                "success": True,
                "response": final_message.content,
                "query": query,
                "used_context": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "response": f"Failed to process query with context: {str(e)}",
                "error": str(e),
                "query": query
            }


# Convenience function
def query_api_agent(query: str, api_queries: list[str] = None) -> dict:
    """
    Query the API agent with a single function call.
    
    Args:
        query: User query
        api_queries: Optional specific API queries
        
    Returns:
        Response dictionary
    """
    agent = APIAgent()
    return agent.query(query, api_queries)


# Example usage
if __name__ == "__main__":
    # Test the API agent
    agent = APIAgent()
    
    test_queries = [
        ("Find all active branches in Kolkata", None),
        ("What are the current FD interest rates?", ["search deposit schemes with type FD"]),
        ("Show me all running loan schemes", ["search loan schemes with status Running"]),
    ]
    
    print("Testing API Agent\n" + "="*80)
    for query, api_queries in test_queries:
        print(f"\nQuery: {query}")
        if api_queries:
            print(f"API Queries: {api_queries}")
        
        result = agent.query(query, api_queries)
        
        print(f"Success: {result['success']}")
        print(f"Response: {result['response'][:200]}...")
        if result.get('error'):
            print(f"Error: {result['error']}")
        print("-" * 80)
