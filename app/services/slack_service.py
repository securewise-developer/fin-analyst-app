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
            self.client = WebClient(token=self.config.SLACK_BOT_TOKEN)
        
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
        f"📅 *Trading Summary* ({ts})",
        f"👀 Symbols monitored: *{symbols_count}*",
        f"🚨 Active alerts: *{active_alerts}*",
        ""
    ]

    for symbol, analysis in last_analysis.items():
        grade = analysis.get("grade", "N/A")
        score = analysis.get("score", "N/A")
        last_update = analysis.get("last_update", "N/A")
        lines.append(f"📊 *{symbol}* - Grade: *{grade}*, Score: {score}, Last update: {last_update}")

    lines.append("")

    for symbol, details in detailed_analysis.items():
        lines.append(f"🔍 *Detailed Analysis for {symbol}*")
        trading_signal = details.get("trading_signal", {})
        action = trading_signal.get("action", "N/A")
        confidence = trading_signal.get("confidence", "N/A")
        position_size = trading_signal.get("position_size", "N/A")
        time_horizon = trading_signal.get("time_horizon", "N/A")
        entry_price = trading_signal.get("entry_price")
        exit_price = trading_signal.get("exit_price")
        stop_loss = trading_signal.get("stop_loss")
        take_profit = trading_signal.get("take_profit")

        # Emoji for action
        action_emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(action.upper(), "⚪")
        lines.append(f"🎯 Trading Signal: {action_emoji} *{action}* (Confidence: {confidence})")
        lines.append(f"⏱️ Time Horizon: {time_horizon}")
        lines.append(f"💹 Position Size: {position_size}")

        # Prices
        if entry_price is not None:
            lines.append(f"💵 Entry Price: {entry_price}")
        if exit_price is not None:
            lines.append(f"🏁 Exit Price: {exit_price}")
        if stop_loss is not None:
            lines.append(f"🛑 Stop Loss: {stop_loss}")
        if take_profit is not None:
            lines.append(f"🎯 Take Profit: {take_profit}")

        # Fundamental reasons
        fr = trading_signal.get("fundamental_reasons", [])
        if fr:
            lines.append("📈 Fundamental Reasons:")
            for r in fr:
                lines.append(f"    • {r}")

        # Technical reasons
        tr = trading_signal.get("technical_reasons", [])
        if tr:
            lines.append("📊 Technical Reasons:")
            for r in tr:
                lines.append(f"    • {r}")

        # News catalysts
        nc = trading_signal.get("news_catalysts", [])
        if nc:
            lines.append("📰 News Catalysts:")
            for c in nc:
                lines.append(f"    • {c}")

        # Market timing
        mt = trading_signal.get("market_timing")
        if mt:
            lines.append(f"⏰ Market Timing: {mt}")

        # Risk factors
        rf = details.get("risk_factors", [])
        if rf:
            lines.append("⚠️ Risk Factors:")
            for r in rf:
                lines.append(f"    • {r}")

        # Key drivers
        kd = details.get("key_drivers", [])
        if kd:
            lines.append("🚀 Key Drivers:")
            for d in kd:
                lines.append(f"    • {d}")

        # Contrarian views
        cv = details.get("contrarian_views")
        if cv:
            lines.append(f"🤔 Contrarian Views: {cv}")

        # Overall analysis
        overall = details.get("overall_analysis")
        if overall:
            lines.append(f"📝 Overall: {overall}")

        lines.append("")  # blank line between symbols

    return "\n".join(lines)
