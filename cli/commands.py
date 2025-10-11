"""
Command Line Interface for Financial Analyst App.

This module provides CLI commands for running analysis without the web API.
"""

import argparse
import sys
from pathlib import Path
from typing import List

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.analyzer import FinancialAnalyzer
from app.config import get_config


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Financial Analyst App - CLI Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze single symbol
  python -m cli.commands analyze --symbol AAPL --type equity
  
  # Monitor multiple symbols
  python -m cli.commands monitor --symbols AAPL MSFT GOOGL --mode once
  
  # Continuous monitoring
  python -m cli.commands monitor --symbols AAPL MSFT --mode continuous --interval 15
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Single symbol analysis command
    analyze_parser = subparsers.add_parser(
        'analyze', 
        help='Analyze a single financial symbol'
    )
    analyze_parser.add_argument('--symbol', required=True, help='Symbol to analyze')
    analyze_parser.add_argument(
        '--type', 
        default='equity', 
        choices=['equity', 'etf', 'fund'],
        help='Security type'
    )
    analyze_parser.add_argument(
        '--lookback', 
        type=int, 
        help='Days of price history to analyze'
    )
    analyze_parser.add_argument(
        '--out', 
        default='analysis_report.json',
        help='Output file path'
    )
    
    # Multi-symbol monitoring command
    monitor_parser = subparsers.add_parser(
        'monitor',
        help='Monitor multiple symbols'
    )
    monitor_parser.add_argument(
        '--symbols', 
        nargs='+', 
        required=True,
        help='Symbols to monitor'
    )
    monitor_parser.add_argument(
        '--mode',
        choices=['once', 'continuous'],
        default='once',
        help='Monitoring mode'
    )
    monitor_parser.add_argument(
        '--interval',
        type=int,
        default=15,
        help='Update interval in minutes (for continuous mode)'
    )
    monitor_parser.add_argument(
        '--detailed',
        action='store_true',
        help='Include detailed analysis'
    )
    monitor_parser.add_argument(
        '--out',
        default='trading_summary.json',
        help='Output file path'
    )
    
    # Status command
    status_parser = subparsers.add_parser(
        'status',
        help='Show application status and configuration'
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'analyze':
            run_single_analysis(args)
        elif args.command == 'monitor':
            run_monitoring(args)
        elif args.command == 'status':
            show_status()
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


def run_single_analysis(args):
    """Run analysis for a single symbol."""
    print(f"🔍 Analyzing {args.symbol} ({args.type})...")
    
    analyzer = FinancialAnalyzer()
    result = analyzer.analyze_single_symbol(
        symbol=args.symbol,
        security_type=args.type,
        lookback_days=args.lookback
    )
    
    # Save result
    output_path = Path(args.out)
    output_path.write_text(
        analyzer._json_dumps_pretty(result),
        encoding='utf-8'
    )
    
    print(f"✅ Analysis completed!")
    print(f"   Grade: {result['grade']}")
    print(f"   Overall Score: {result['scores']['overall']:.2f}")
    print(f"   Report saved: {output_path}")


def run_monitoring(args):
    """Run monitoring for multiple symbols."""
    print(f"📊 Starting monitoring for {len(args.symbols)} symbols...")
    print(f"   Symbols: {', '.join(args.symbols)}")
    print(f"   Mode: {args.mode}")
    
    if args.mode == 'continuous':
        print(f"   Interval: {args.interval} minutes")
    
    analyzer = FinancialAnalyzer()
    result_path = analyzer.analyze_symbols(
        symbols=args.symbols,
        detailed=args.detailed,
        mode=args.mode,
        output_file=args.out
    )
    
    if args.mode == 'once':
        print(f"✅ Monitoring completed!")
        print(f"   Results saved: {result_path}")
    else:
        print("🔄 Continuous monitoring started...")
        print("   Press Ctrl+C to stop")


def show_status():
    """Show application status and configuration."""
    print("📋 Financial Analyst App Status")
    print("=" * 40)
    
    config = get_config()
    analyzer = FinancialAnalyzer()
    status = analyzer.get_configuration_status()
    
    print(f"Data Provider: {status['data_provider']}")
    print(f"OpenAI: {'✅ Configured' if status['openai_configured'] else '❌ Missing'}")
    print(f"Slack: {'✅ Configured' if status['slack_configured'] else '❌ Not configured'}")
    print(f"FMP API: {'✅ Configured' if status['fmp_configured'] else '❌ Not configured'}")
    print(f"Price Lookback: {status['price_lookback_days']} days")
    print(f"Update Interval: {status['update_interval']} minutes")
    
    # Validate configuration
    errors = config.validate()
    if errors:
        print("\n⚠️  Configuration Issues:")
        for error in errors:
            print(f"   - {error}")


if __name__ == '__main__':
    sys.exit(main())
