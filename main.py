#!/usr/bin/env python3
"""
Flight Deal Bot - Main Entry Point
Automated flight price monitoring for Warsaw to Brazil
"""

import sys
import logging
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.scheduler import run_once, run_continuous, FlightBot
from src.config import get_config

# Configure logging
def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    log_level = logging.DEBUG if verbose else logging.INFO
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'flight-bot.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Flight Deal Bot - Automated price monitoring for Warsaw to Brazil',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run continuously (production mode)
  python main.py --once             # Run once and exit
  python main.py --test             # Test mode (no emails sent)
  python main.py --test-email       # Send test email
  python main.py --verbose          # Enable debug logging
  python main.py --config custom.yaml  # Use custom config file
        """
    )
    
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run price check once and exit'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Test mode - dry run without sending emails'
    )
    
    parser.add_argument(
        '--test-email',
        action='store_true',
        help='Send a test email to verify configuration'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose (debug) logging'
    )
    
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    try:
        # Welcome message
        logger.info("=" * 60)
        logger.info("✈️  Flight Deal Bot - Warsaw to Brazil")
        logger.info("=" * 60)
        
        # Load configuration
        try:
            config = get_config(args.config)
            logger.info(f"Configuration loaded from: {args.config}")
            logger.info(f"Origin: {config.origin}")
            logger.info(f"Destinations: {', '.join(config.destinations)}")
            logger.info(f"Check frequency: Every {config.check_frequency_hours} hours")
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {args.config}")
            logger.error("Please copy config.example.yaml to config.yaml and edit it")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Configuration error: {e}")
            sys.exit(1)
        
        # Test email
        if args.test_email:
            logger.info("Sending test email...")
            bot = FlightBot(args.config)
            success = bot.email.test_email()
            
            if success:
                logger.info("✅ Test email sent successfully!")
                logger.info("Check your inbox to confirm receipt")
            else:
                logger.error("❌ Test email failed - check your configuration")
                sys.exit(1)
            
            sys.exit(0)
        
        # Test mode
        if args.test:
            logger.info("🧪 Running in TEST mode (no emails will be sent)")
            # Temporarily disable email
            import src.email_sender
            original_send = src.email_sender.EmailSender._send_email
            src.email_sender.EmailSender._send_email = lambda self, *args, **kwargs: logger.info("📧 (Test mode: email suppressed)")
        
        # Run mode
        if args.once:
            logger.info("Running single price check...")
            run_once(args.config)
            logger.info("✅ Price check complete!")
        else:
            logger.info("Starting continuous monitoring...")
            logger.info("Press Ctrl+C to stop")
            run_continuous(args.config)
    
    except KeyboardInterrupt:
        logger.info("\n👋 Shutting down gracefully...")
        sys.exit(0)
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
