import json
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from app.config import get_config

class SlackService:
    """Service for sending notifications to Slack."""
    
    def __init__(self, config=None):
        """Initialize Slack service with configuration."""
        self.config = config or get_config()
        self.client = None
        if self.config.SLACK_BOT_TOKEN:
            # Create client with SSL handling for development
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            self.client = WebClient(
                token=self.config.SLACK_BOT_TOKEN,
                ssl=ssl_context
            )
        
        self.logger = logging.getLogger(__name__)
    
    def is_configured(self) -> bool:
        """Check if Slack is properly configured."""
        return bool(self.config.SLACK_BOT_TOKEN)
    
    def send_analysis_summary(self, summary_path: str):
        """Send analysis summary to Slack channel."""
        self.logger.info("Sending summary to Slack...")

        if not self.is_configured():
            self.logger.warning("No Slack token configured, skipping notification")
            return

        try:
            with open(summary_path, "r", encoding="utf-8") as f:
                summary = json.load(f)

            text = self._format_trading_summary(summary)
            response = self.client.chat_postMessage(
                channel=self.config.SLACK_CHANNEL, 
                text=text
            )

            self.logger.info("Slack notification sent successfully")
            return response
            
        except SlackApiError as e:
            self.logger.error(f"Slack API error: {e.response['error']}")
            raise
        except Exception:
            self.logger.exception("Error sending Slack notification")
            raise
    
    def send_custom_message(self, message: str, channel: str = None):
        """Send a custom message to Slack."""
        if not self.is_configured():
            self.logger.warning("No Slack token configured, skipping notification")
            return
        
        channel = channel or self.config.SLACK_CHANNEL
        
        try:
            response = self.client.chat_postMessage(channel=channel, text=message)
            self.logger.info(f"Custom message sent to {channel}")
            return response
        except SlackApiError as e:
            self.logger.error(f"Slack API error: {e.response['error']}")
            raise
    
    def send_analysis_complete_notification(self, symbols: list, summary_data: dict, user_name: str = None):
        """Send a structured notification when analysis is complete."""
        if not self.is_configured():
            self.logger.warning("No Slack token configured, skipping notification")
            return
        
        try:
            symbol_list = ", ".join(symbols)
            
            # Create blocks for rich formatting
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "📊 Financial Analysis Complete"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Symbols Analyzed:* {symbol_list}"
                    }
                }
            ]
            
            # Add user mention if provided
            if user_name:
                blocks.append({
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"Requested by: @{user_name}"
                        }
                    ]
                })
            
            # Add analysis results for each symbol
            for symbol, analysis in summary_data.get("last_analysis", {}).items():
                grade = analysis.get("grade", "N/A")
                score = analysis.get("score", "N/A")
                
                # Choose emoji based on grade
                grade_emoji = {
                    "A": "🟢", "B": "🔵", "C": "🟡", "D": "🟠", "F": "🔴"
                }.get(grade, "⚪")
                
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"{grade_emoji} *{symbol}*\n*Grade:* {grade} | *Score:* {score:.2f}" if isinstance(score, (int, float)) else f"{grade_emoji} *{symbol}*\n*Grade:* {grade} | *Score:* {score}"
                    }
                })
            
            # Add opportunities if any
            opportunities = summary_data.get("trading_opportunities", [])
            if opportunities:
                blocks.append({
                    "type": "divider"
                })
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"🎯 *Trading Opportunities Found:* {len(opportunities)}"
                    }
                })
                
                for opp in opportunities[:3]:  # Show top 3 opportunities
                    action_emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(opp.get("action", "").upper(), "⚪")
                    blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn", 
                            "text": f"{action_emoji} *{opp['symbol']}* - {opp['action']} (Confidence: {opp['confidence']:.0%})"
                        }
                    })
            
            # Add footer
            blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "💡 *Tip:* Use `/analyze SYMBOL1 SYMBOL2` to analyze more stocks"
                    }
                ]
            })
            
            response = self.client.chat_postMessage(
                channel=self.config.SLACK_CHANNEL,
                blocks=blocks,
                text=f"Analysis complete for {symbol_list}"  # Fallback text
            )
            
            self.logger.info(f"Analysis completion notification sent to Slack")
            return response
            
        except SlackApiError as e:
            self.logger.error(f"Slack API error: {e.response['error']}")
            raise
        except Exception as e:
            self.logger.exception("Error sending analysis completion notification")
            raise
    
    def _format_trading_summary(self, summary: dict) -> str:
        """Format trading summary for Slack display."""
        return format_trading_summary(summary)


# Legacy function for backward compatibility
def send_summary_to_slack(summary_path: str):
    """Legacy function - use SlackService.send_analysis_summary instead."""
    service = SlackService()
    return service.send_analysis_summary(summary_path)

def format_trading_summary(summary: dict) -> str:
    ts = summary.get("timestamp", "N/A")
    symbols_count = summary.get("symbols_monitored", 0)
    last_analysis = summary.get("last_analysis", {})
    active_alerts = summary.get("active_alerts", 0)
    detailed_analysis = summary.get("detailed_analysis", {})

    lines = [
        f"📊 *DETAILED TRADING ANALYSIS*",
        f"⏰ *Analysis Time:* {ts[:19].replace('T', ' ')}",
        f"📈 *Symbols Analyzed:* {symbols_count} | 🚨 *Active Alerts:* {active_alerts}",
        "─────────────────────────────────",
        ""
    ]

    # Quick overview of all symbols first
    for symbol, analysis in last_analysis.items():
        grade = analysis.get("grade", "N/A")
        score = analysis.get("score", "N/A")
        
        # Grade emoji
        grade_emoji = {"A": "🟢", "B": "🔵", "C": "🟡", "D": "🟠", "F": "🔴"}.get(grade, "⚪")
        
        score_display = f"{score:.2f}" if isinstance(score, (int, float)) else str(score)
        lines.append(f"{grade_emoji} *{symbol}* - Grade: *{grade}* | Score: *{score_display}*")

    lines.extend(["", "═══════ DETAILED ANALYSIS ═══════", ""])

    # Detailed analysis for each symbol
    for symbol, details in detailed_analysis.items():
        lines.append(f"🔍 *{symbol} - COMPREHENSIVE ANALYSIS*")
        lines.append("─" * 30)
        
        trading_signal = details.get("trading_signal", {})
        action = trading_signal.get("action", "N/A")
        confidence = trading_signal.get("confidence", "N/A")
        position_size = trading_signal.get("position_size", "N/A")
        time_horizon = trading_signal.get("time_horizon", "N/A")

        # Trading Signal Section
        action_emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(action.upper(), "⚪")
        confidence_display = f"{confidence:.0%}" if isinstance(confidence, (int, float)) else str(confidence)
        
        lines.extend([
            f"🎯 *TRADING SIGNAL*",
            f"   {action_emoji} *Action:* {action} | *Confidence:* {confidence_display}",
            f"   ⏱️ *Time Horizon:* {time_horizon}",
            f"   💹 *Position Size:* {position_size}",
        ])

        # Price Targets
        entry_price = trading_signal.get("entry_price")
        stop_loss = trading_signal.get("stop_loss")
        take_profit = trading_signal.get("take_profit")
        
        if any([entry_price, stop_loss, take_profit]):
            lines.append(f"💰 *PRICE TARGETS*")
            if entry_price is not None:
                lines.append(f"   💵 Entry: ${entry_price}")
            if stop_loss is not None:
                lines.append(f"   🛑 Stop Loss: ${stop_loss}")
            if take_profit is not None:
                lines.append(f"   🎯 Take Profit: ${take_profit}")

        # Analysis Reasons
        fr = trading_signal.get("fundamental_reasons", [])
        if fr:
            lines.append(f"📈 *FUNDAMENTAL REASONS*")
            for r in fr[:3]:  # Limit to top 3 for readability
                lines.append(f"   • {r}")

        tr = trading_signal.get("technical_reasons", [])
        if tr:
            lines.append(f"📊 *TECHNICAL REASONS*")
            for r in tr[:3]:  # Limit to top 3
                lines.append(f"   • {r}")

        nc = trading_signal.get("news_catalysts", [])
        if nc:
            lines.append(f"📰 *NEWS CATALYSTS*")
            for c in nc[:3]:  # Limit to top 3
                lines.append(f"   • {c}")

        # Market Context
        mt = trading_signal.get("market_timing")
        if mt:
            lines.extend([
                f"⏰ *MARKET TIMING*",
                f"   {mt}"
            ])

        # Risk Assessment
        rf = details.get("risk_factors", [])
        if rf:
            lines.append(f"⚠️ *RISK FACTORS*")
            for r in rf[:3]:  # Limit to top 3
                lines.append(f"   • {r}")

        # Key Growth Drivers
        kd = details.get("key_drivers", [])
        if kd:
            lines.append(f"🚀 *KEY DRIVERS*")
            for d in kd[:3]:  # Limit to top 3
                lines.append(f"   • {d}")

        # Overall Assessment
        overall = details.get("overall_analysis")
        if overall:
            lines.extend([
                f"📝 *OVERALL ASSESSMENT*",
                f"   {overall[:200]}{'...' if len(overall) > 200 else ''}"  # Truncate for readability
            ])

        # Contrarian Views
        cv = details.get("contrarian_views")
        if cv:
            lines.extend([
                f"🤔 *CONTRARIAN VIEWS*",
                f"   {cv[:150]}{'...' if len(cv) > 150 else ''}"  # Truncate for readability
            ])

        lines.extend(["", "─" * 30, ""])  # Separator between symbols

    lines.extend([
        "🎯 *Analysis powered by AI | Use responsibly*",
        "💡 *Tip:* Use `/analyze SYMBOL1 SYMBOL2` for more analysis"
    ])

    return "\n".join(lines)
