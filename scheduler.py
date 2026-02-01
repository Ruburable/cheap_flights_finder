"""
Scheduler for automated flight price checks
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.config import get_config
from src.flight_api import FlightAPI
from src.database import Database
from src.analyzer import PriceAnalyzer
from src.email_sender import EmailSender

logger = logging.getLogger(__name__)


class FlightBot:
    """Main flight deal bot orchestrator"""

    def __init__(self, config_path: str = "config.yaml"):
        self.config = get_config(config_path)

        # Initialize components
        self.api = FlightAPI(
            api_key=self.config.amadeus_api_key,
            api_secret=self.config.amadeus_api_secret
        )
        self.db = Database(db_path=self.config.database_path)
        self.analyzer = PriceAnalyzer(self.db, self.config)
        self.email = EmailSender(self.config)

        logger.info("Flight bot initialized successfully")

    def check_prices(self):
        """Main price checking routine"""
        logger.info("=" * 60)
        logger.info("Starting price check...")
        logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)

        try:
            all_offers = []

            # Check each destination
            for destination in self.config.destinations:
                logger.info(f"Checking {self.config.origin} → {destination}")

                offers = self._search_destination(destination)
                all_offers.extend(offers)

            if not all_offers:
                logger.warning("No flight offers found")
                return

            logger.info(f"Found {len(all_offers)} total offers")

            # Analyze offers
            analyzed_offers = []
            for offer in all_offers:
                # Add origin/destination to offer
                offer['origin'] = self.config.origin

                # Analyze
                analysis_result = self.analyzer.analyze_offer(offer)
                analyzed_offers.append({
                    **offer,
                    'analysis': analysis_result
                })

                # Store in database
                self._store_price_check(offer, analysis_result)

            # Get best offers
            best_offers = self.analyzer.get_best_offers(analyzed_offers, limit=5)

            # Log results
            for i, offer in enumerate(best_offers):
                quality = offer['analysis']['deal_quality']
                logger.info(
                    f"{i + 1}. {offer['origin']}→{offer['destination']}: "
                    f"{offer['price']} {offer['currency']} ({quality})"
                )

            # Check if should send alerts
            alertable_offers = self.analyzer.get_alertable_offers(best_offers)

            if alertable_offers:
                logger.info(f"🎉 Found {len(alertable_offers)} alertable deals!")

                # Record deals in database
                for offer in alertable_offers:
                    self._store_deal(offer)

                # Send email alert
                self.email.send_deal_alert(alertable_offers)
            else:
                logger.info("No deals meeting alert criteria")

            # Cleanup old data
            self.db.cleanup_old_data(
                detailed_days=self.config.get('advanced.keep_detailed_history_days', 30),
                aggregate_days=self.config.get('advanced.keep_aggregated_history_days', 365)
            )

            logger.info("Price check complete!")

        except Exception as e:
            logger.error(f"Error during price check: {e}", exc_info=True)

            if self.config.get('advanced.send_error_notifications', True):
                self._send_error_notification(e)

    def _search_destination(self, destination: str) -> List[Dict[str, Any]]:
        """Search flights for a specific destination"""
        offers = []

        # Get date parameters
        search_window_days = self.config.get('dates.search_window_days', 180)
        trip_length_min = self.config.trip_length_min
        trip_length_max = self.config.trip_length_max
        flexible = self.config.trip_length_flexible

        # Define search dates
        today = datetime.now()
        target_periods = self.config.get('dates.target_periods', [])

        if target_periods:
            # Search specific target periods
            for period in target_periods:
                start_date = datetime.strptime(period['start_date'], '%Y-%m-%d')
                end_date = datetime.strptime(period['end_date'], '%Y-%m-%d')

                # Sample a few dates in the period (to avoid too many API calls)
                search_dates = self._sample_dates(start_date, end_date, samples=3)

                for dep_date in search_dates:
                    trip_lengths = [trip_length_min, trip_length_max] if flexible else [trip_length_min]

                    for length in trip_lengths:
                        ret_date = dep_date + timedelta(days=length)

                        flight_offers = self.api.search_flights(
                            origin=self.config.origin,
                            destination=destination,
                            departure_date=dep_date,
                            return_date=ret_date,
                            max_results=5
                        )

                        # Add metadata
                        for offer in flight_offers:
                            offer['destination'] = destination
                            offer['departure_date'] = dep_date.strftime('%Y-%m-%d')
                            offer['return_date'] = ret_date.strftime('%Y-%m-%d')
                            offer['trip_length'] = length

                        offers.extend(flight_offers)
        else:
            # Search general window
            search_start = today + timedelta(days=14)  # Start 2 weeks from now
            search_end = today + timedelta(days=search_window_days)

            # Sample dates to avoid excessive API calls
            search_dates = self._sample_dates(search_start, search_end, samples=5)

            for dep_date in search_dates:
                trip_lengths = range(trip_length_min, trip_length_max + 1, 3) if flexible else [trip_length_min]

                for length in trip_lengths:
                    ret_date = dep_date + timedelta(days=length)

                    flight_offers = self.api.search_flights(
                        origin=self.config.origin,
                        destination=destination,
                        departure_date=dep_date,
                        return_date=ret_date,
                        max_results=5
                    )

                    # Add metadata
                    for offer in flight_offers:
                        offer['destination'] = destination
                        offer['departure_date'] = dep_date.strftime('%Y-%m-%d')
                        offer['return_date'] = ret_date.strftime('%Y-%m-%d')
                        offer['trip_length'] = length

                    offers.extend(flight_offers)

        logger.info(f"Found {len(offers)} offers for {destination}")
        return offers

    def _sample_dates(self, start: datetime, end: datetime, samples: int) -> List[datetime]:
        """Sample evenly spaced dates from a range"""
        total_days = (end - start).days

        if total_days <= 0:
            return [start]

        if samples >= total_days:
            # Return all days
            return [start + timedelta(days=i) for i in range(total_days + 1)]

        # Sample evenly
        step = total_days / (samples - 1) if samples > 1 else 0
        return [start + timedelta(days=int(i * step)) for i in range(samples)]

    def _store_price_check(self, offer: Dict[str, Any], analysis: Dict[str, Any]):
        """Store price check in database"""
        try:
            self.db.add_price_check({
                'origin': offer.get('origin'),
                'destination': offer.get('destination'),
                'departure_date': offer.get('departure_date'),
                'return_date': offer.get('return_date'),
                'trip_length': offer.get('trip_length'),
                'price': offer.get('price'),
                'currency': offer.get('currency'),
                'stops': offer.get('total_stops', 0),
                'airlines': offer.get('outbound', {}).get('airlines', []),
                'connections': offer.get('outbound', {}).get('connections', []),
                'raw_offer': offer
            })
        except Exception as e:
            logger.error(f"Error storing price check: {e}")

    def _store_deal(self, offer: Dict[str, Any]):
        """Store deal in database"""
        try:
            analysis = offer['analysis']

            self.db.add_deal({
                'origin': offer.get('origin'),
                'destination': offer.get('destination'),
                'departure_date': offer.get('departure_date'),
                'return_date': offer.get('return_date'),
                'price': offer.get('price'),
                'currency': offer.get('currency'),
                'discount_percent': analysis.get('discount_percent'),
                'deal_quality': analysis.get('deal_quality'),
                'outbound': offer.get('outbound'),
                'inbound': offer.get('inbound'),
                'booking_link': offer.get('booking_link'),
                'notified': True
            })
        except Exception as e:
            logger.error(f"Error storing deal: {e}")

    def _send_error_notification(self, error: Exception):
        """Send error notification email"""
        try:
            subject = "⚠️ Flight Bot Error"
            text = f"An error occurred during price check:\n\n{str(error)}"
            html = f"<html><body><h2>Error</h2><p>{str(error)}</p></body></html>"

            self.email._send_email(subject, html, text)
        except:
            logger.error("Failed to send error notification")


def run_once(config_path: str = "config.yaml"):
    """Run price check once and exit"""
    bot = FlightBot(config_path)
    bot.check_prices()


def run_continuous(config_path: str = "config.yaml"):
    """Run price checks continuously on schedule"""
    bot = FlightBot(config_path)

    # Get check frequency from config
    check_hours = bot.config.check_frequency_hours

    logger.info(f"Starting continuous mode: checking every {check_hours} hours")

    # Create scheduler
    scheduler = BlockingScheduler()

    # Add job
    scheduler.add_job(
        bot.check_prices,
        trigger=IntervalTrigger(hours=check_hours),
        id='price_check',
        name='Flight price check',
        replace_existing=True
    )

    # Run first check immediately
    bot.check_prices()

    # Start scheduler
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")