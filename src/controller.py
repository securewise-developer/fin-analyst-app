from flask import Flask, jsonify, request
import os
from slack_sdk import WebClient
from concurrent.futures import ThreadPoolExecutor
from src.main import run_trading_monitor
from src.slack_notifier import send_summary_to_slack
import logging

app = Flask(__name__)
slack_token: str = os.getenv("SLACK_BOT_TOKEN","")
client = WebClient(token=slack_token)
executor = ThreadPoolExecutor(max_workers=2)

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json(force=True)
        symbols = data.get("symbols")
        if not symbols:
            return jsonify({"success": False, "error": "Missing 'symbols'"}), 400

        # Run trading_monitor_main in background 
        executor.submit(run_analysis, symbols)

        return jsonify({"success": True})
    except Exception as e:
        logging.exception("Error in analyze endpoint")
        return jsonify({"success": False, "error": str(e)}), 500


def run_analysis(symbols):
    """Background task to run analysis and send Slack notification."""
    try:
        run_trading_monitor(symbols=symbols, detailed=True, mode="once") #continuous 
        send_summary_to_slack("trading_summary.json")
    except Exception: 
        logging.exception("Error during trading monitor analysis")

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

if __name__ == "__main__":
    app.run(port=8080, debug=True)