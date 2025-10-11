"""
Request and Response schemas for the API.

This module defines the data structures used in API requests and responses.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    """Request schema for financial analysis."""
    symbols: List[str] = Field(..., description="List of financial symbols to analyze")
    detailed: bool = Field(default=True, description="Whether to include detailed analysis")
    mode: str = Field(default="once", description="Analysis mode: 'once' or 'continuous'")


class SymbolAnalysis(BaseModel):
    """Analysis result for a single symbol."""
    symbol: str
    grade: Optional[str] = None
    score: Optional[float] = None
    last_update: Optional[str] = None


class TradingOpportunity(BaseModel):
    """Trading opportunity data."""
    symbol: str
    grade: str
    confidence: float
    action: str
    timestamp: str


class AnalysisResponse(BaseModel):
    """Response schema for analysis results."""
    success: bool
    timestamp: str
    symbols_monitored: int
    last_analysis: dict[str, SymbolAnalysis]
    trading_opportunities: List[TradingOpportunity]
    active_alerts: int


class ErrorResponse(BaseModel):
    """Error response schema."""
    success: bool = False
    error: str


class StatusResponse(BaseModel):
    """Status response schema."""
    success: bool
    status: str
    configuration: dict
    version: str
