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


@api_bp.route('/slack/analyze', methods=['POST'])
def slack_analyze():
    """
    Slack slash command endpoint for /analyze command.
    
    Handles Slack slash commands like: /analyze NVDA AAPL MSFT
    
    Expected form data from Slack:
    - token: Slack verification token
    - command: The slash command (/analyze)
    - text: Space-separated symbols (e.g., "NVDA AAPL MSFT")
    - user_name: Username who triggered the command
    - channel_name: Channel where command was used
    """
    try:
        # Get form data from Slack
        token = request.form.get('token', '')
        command = request.form.get('command', '')
        text = request.form.get('text', '').strip()
        user_name = request.form.get('user_name', 'unknown')
        channel_name = request.form.get('channel_name', 'unknown')
        
        logger.info(f"Slack command received: {command} from {user_name} in #{channel_name}")
        
        # Validate command
        if command != '/analyze':
            return jsonify({
                "response_type": "ephemeral",
                "text": f"❌ Unknown command: {command}. Use `/analyze SYMBOL1 SYMBOL2...`"
            })
        
        # Parse symbols from text
        if not text:
            return jsonify({
                "response_type": "ephemeral",
                "text": "❌ Please provide symbols to analyze.\n*Usage:* `/analyze AAPL MSFT GOOGL`"
            })
        
        # Extract symbols (split by spaces and clean up)
        symbols = [symbol.upper().strip() for symbol in text.split() if symbol.strip()]
        
        if not symbols:
            return jsonify({
                "response_type": "ephemeral", 
                "text": "❌ No valid symbols provided.\n*Usage:* `/analyze AAPL MSFT GOOGL`"
            })
        
        # Limit number of symbols for performance
        if len(symbols) > 5:
            return jsonify({
                "response_type": "ephemeral",
                "text": f"❌ Too many symbols ({len(symbols)}). Maximum 5 symbols allowed.\n*Usage:* `/analyze AAPL MSFT GOOGL`"
            })
        
        # Validate symbol format (basic check)
        invalid_symbols = [s for s in symbols if len(s) > 10 or not s.isalnum()]
        if invalid_symbols:
            return jsonify({
                "response_type": "ephemeral",
                "text": f"❌ Invalid symbols: {', '.join(invalid_symbols)}\n*Usage:* `/analyze AAPL MSFT GOOGL`"
            })
        
        logger.info(f"Starting Slack analysis for symbols: {symbols} (requested by {user_name})")
        
        # Start background analysis with user context
        executor.submit(run_background_analysis_slack, symbols, user_name, detailed=True, mode="once")
        
        # Return immediate response to Slack
        symbol_list = ", ".join(symbols)
        return jsonify({
            "response_type": "in_channel",  # Show to everyone in channel
            "text": f"🔍 *Analysis Started*",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"📊 *Financial Analysis Started*\n*Symbols:* {symbol_list}\n*Requested by:* @{user_name}\n*Estimated completion:* 2-5 minutes"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": "⏳ Analysis running in background... Results will be posted when complete."
                        }
                    ]
                }
            ]
        })
        
    except Exception as e:
        logger.exception("Error in Slack analyze endpoint")
        return jsonify({
            "response_type": "ephemeral",
            "text": f"❌ *Error processing command*\n```{str(e)}```\nPlease try again or contact support."
        })


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


def run_background_analysis_slack(symbols: list, user_name: str, detailed: bool = True, mode: str = "once"):
    """
    Background task to run financial analysis and send enhanced Slack notification.
    
    Args:
        symbols: List of financial symbols to analyze
        user_name: Slack username who requested the analysis
        detailed: Whether to include detailed analysis
        mode: Analysis mode ('once' or 'continuous')
    """
    try:
        logger.info(f"Background Slack analysis started for {symbols} (requested by {user_name})")
        
        # Initialize analyzer
        analyzer = FinancialAnalyzer()
        
        # Run analysis
        result_path = analyzer.analyze_symbols(
            symbols=symbols,
            detailed=detailed,
            mode=mode,
            output_file="trading_summary.json"
        )
        
        # Send both detailed trading summary and enhanced notification to Slack
        slack_service = SlackService()
        if slack_service.is_configured():
            # 1. Send detailed trading summary (same as /analyze endpoint)
            slack_service.send_analysis_summary(result_path)
            logger.info(f"Detailed trading summary sent to Slack for {symbols}")
            
            # 2. Send enhanced summary notification with user attribution
            import json
            with open(result_path, 'r') as f:
                summary_data = json.load(f)
            
            slack_service.send_analysis_complete_notification(symbols, summary_data, user_name)
            logger.info(f"Enhanced Slack analysis notification sent for {symbols}")
        else:
            logger.warning("Slack not configured, skipping notification")
        
        logger.info(f"Background Slack analysis completed for {symbols}")
        
    except Exception as e:
        logger.exception(f"Error in background Slack analysis for {symbols}")


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
