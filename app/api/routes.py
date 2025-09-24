"""
API Routes for Financial Analyst App.

This module defines all REST API endpoints for the application.
"""

from flask import Blueprint, jsonify, request, current_app
from concurrent.futures import ThreadPoolExecutor
import logging

from app.core.analyzer import FinancialAnalyzer
from app.services.slack_service import SlackService
from app.api.schemas import AnalysisRequest, AnalysisResponse

# Create blueprint
api_bp = Blueprint('api', __name__)

# Thread pool for background tasks
executor = ThreadPoolExecutor(max_workers=2)

logger = logging.getLogger(__name__)


@api_bp.route('/analyze', methods=['POST'])
def analyze():
    """
    Analyze financial symbols and send results to Slack.
    
    Expected JSON payload:
    {
        "symbols": ["AAPL", "MSFT"],
        "detailed": true,
        "mode": "once"
    }
    """
    try:
        # Validate request
        data = request.get_json(force=True)
        if not data:
            return jsonify({"success": False, "error": "No JSON payload provided"}), 400
        
        # Validate required fields
        symbols = data.get("symbols")
        if not symbols:
            return jsonify({"success": False, "error": "Missing 'symbols' field"}), 400
        
        if not isinstance(symbols, list) or not symbols:
            return jsonify({"success": False, "error": "'symbols' must be a non-empty list"}), 400
        
        # Optional parameters
        detailed = data.get("detailed", True)
        mode = data.get("mode", "once")
        
        # Validate symbols
        for symbol in symbols:
            if not isinstance(symbol, str) or not symbol.strip():
                return jsonify({"success": False, "error": f"Invalid symbol: {symbol}"}), 400
        
        logger.info(f"Starting analysis for symbols: {symbols}")
        
        # Run analysis in background
        executor.submit(run_background_analysis, symbols, detailed, mode)
        
        return jsonify({
            "success": True,
            "message": f"Analysis started for {len(symbols)} symbols",
            "symbols": symbols,
            "estimated_completion": "2-5 minutes"
        })
        
    except Exception as e:
        logger.exception("Error in analyze endpoint")
        return jsonify({
            "success": False, 
            "error": f"Internal server error: {str(e)}"
        }), 500


@api_bp.route('/status', methods=['GET'])
def status():
    """Get the current status of the application."""
    try:
        analyzer = FinancialAnalyzer()
        config_status = analyzer.get_configuration_status()
        
        return jsonify({
            "success": True,
            "status": "operational",
            "configuration": config_status,
            "version": "2.0.0"
        })
        
    except Exception as e:
        logger.exception("Error in status endpoint")
        return jsonify({
            "success": False,
            "error": f"Status check failed: {str(e)}"
        }), 500


@api_bp.route('/health', methods=['GET'])
def health():
    """Simple health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "fin-analyst-app"
    })


def run_background_analysis(symbols: list, detailed: bool = True, mode: str = "once"):
    """
    Background task to run financial analysis and send Slack notification.
    
    Args:
        symbols: List of financial symbols to analyze
        detailed: Whether to include detailed analysis
        mode: Analysis mode ('once' or 'continuous')
    """
    try:
        logger.info(f"Background analysis started for {symbols}")
        
        # Initialize analyzer
        analyzer = FinancialAnalyzer()
        
        # Run analysis
        result_path = analyzer.analyze_symbols(
            symbols=symbols,
            detailed=detailed,
            mode=mode,
            output_file="trading_summary.json"
        )
        
        # Send to Slack if configured
        slack_service = SlackService()
        if slack_service.is_configured():
            slack_service.send_analysis_summary(result_path)
            logger.info("Analysis results sent to Slack")
        else:
            logger.warning("Slack not configured, skipping notification")
        
        logger.info(f"Background analysis completed for {symbols}")
        
    except Exception as e:
        logger.exception(f"Error in background analysis for {symbols}")


@api_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404


@api_bp.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors."""
    return jsonify({
        "success": False,
        "error": "Method not allowed"
    }), 405


@api_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.exception("Internal server error")
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500
