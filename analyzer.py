"""
Price analyzer - determines if a price is a good deal
"""

import logging
from typing import Dict, List, Optional, Any
from src.database import Database
from src.config import Config

logger = logging.getLogger(__name__)


class PriceAnalyzer:
    """Analyzes flight prices to identify deals"""

    def __init__(self, database: Database, config: Config):
        self.db = database
        self.config = config

    def analyze_offer(self, offer: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a flight offer to determine if it's a deal

        Args:
            offer: Flight offer data

        Returns:
            Analysis results with deal quality and recommendation
        """
        route = f"{offer['origin']}-{offer['destination']}"
        price = offer['price']

        # Get historical statistics
        stats_30d = self.db.get_price_statistics(route, days=30)
        stats_90d = self.db.get_price_statistics(route, days=90)

        # Determine deal quality
        deal_quality = self._determine_deal_quality(
            price=price,
            stats_30d=stats_30d,
            stats_90d=stats_90d
        )

        # Calculate discount percentage
        discount_percent = None
        if stats_30d['avg']:
            discount_percent = ((stats_30d['avg'] - price) / stats_30d['avg']) * 100

        # Determine if should alert
        should_alert = self._should_alert(
            price=price,
            discount_percent=discount_percent,
            deal_quality=deal_quality
        )

        return {
            'route': route,
            'price': price,
            'currency': offer['currency'],
            'deal_quality': deal_quality,
            'discount_percent': discount_percent,
            'should_alert': should_alert,
            'stats_30d': stats_30d,
            'stats_90d': stats_90d,
            'comparison': self._generate_comparison(price, stats_30d, stats_90d)
        }

    def _determine_deal_quality(
            self,
            price: float,
            stats_30d: Dict[str, float],
            stats_90d: Dict[str, float]
    ) -> str:
        """
        Determine the quality of a deal

        Returns:
            'amazing', 'great', 'good', or 'average'
        """
        # Check absolute price thresholds
        amazing_price = self.config.amazing_deal_price
        great_price = self.config.great_deal_price
        good_price = self.config.get('price_alerts.thresholds.good_deal', 3000)

        # Check percentage thresholds
        amazing_percent = self.config.get('price_alerts.percentage_thresholds.amazing_deal_percent', 25)
        great_percent = self.config.get('price_alerts.percentage_thresholds.great_deal_percent', 20)
        good_percent = self.config.get('price_alerts.percentage_thresholds.good_deal_percent', 15)

        # Calculate discount if we have historical data
        discount_percent = 0
        if stats_30d['avg']:
            discount_percent = ((stats_30d['avg'] - price) / stats_30d['avg']) * 100

        # Determine quality
        require_both = self.config.get('price_alerts.require_both_conditions', False)

        if require_both:
            # Must meet BOTH price AND percentage
            if price <= amazing_price and discount_percent >= amazing_percent:
                return 'amazing'
            elif price <= great_price and discount_percent >= great_percent:
                return 'great'
            elif price <= good_price and discount_percent >= good_percent:
                return 'good'
        else:
            # Meets EITHER condition
            if price <= amazing_price or discount_percent >= amazing_percent:
                return 'amazing'
            elif price <= great_price or discount_percent >= great_percent:
                return 'great'
            elif price <= good_price or discount_percent >= good_percent:
                return 'good'

        return 'average'

    def _should_alert(
            self,
            price: float,
            discount_percent: Optional[float],
            deal_quality: str
    ) -> bool:
        """
        Determine if an alert should be sent based on config

        Returns:
            True if should send alert, False otherwise
        """
        alert_frequency = self.config.get('email.alert_frequency', 'major_deals_only')

        if alert_frequency == 'major_deals_only':
            # Only alert on great or amazing deals
            if deal_quality in ['amazing', 'great']:
                return True

            # Also check if discount meets major deal threshold
            threshold = self.config.major_deal_threshold_percent
            if discount_percent and discount_percent >= threshold:
                return True

            return False

        elif alert_frequency == 'immediate':
            # Alert on any good deal or better
            return deal_quality in ['good', 'great', 'amazing']

        elif alert_frequency == 'daily_digest':
            # Will be handled by digest logic
            return deal_quality in ['good', 'great', 'amazing']

        return False

    def _generate_comparison(
            self,
            price: float,
            stats_30d: Dict[str, float],
            stats_90d: Dict[str, float]
    ) -> Dict[str, Any]:
        """Generate price comparison text"""
        comparison = {
            'current_price': price,
            'vs_30d_avg': None,
            'vs_90d_avg': None,
            'vs_30d_min': None,
            'percentile': None
        }

        if stats_30d['avg']:
            diff = price - stats_30d['avg']
            pct = (diff / stats_30d['avg']) * 100
            comparison['vs_30d_avg'] = {
                'diff': diff,
                'percent': pct,
                'text': f"{'↓' if diff < 0 else '↑'} {abs(pct):.1f}%"
            }

        if stats_90d['avg']:
            diff = price - stats_90d['avg']
            pct = (diff / stats_90d['avg']) * 100
            comparison['vs_90d_avg'] = {
                'diff': diff,
                'percent': pct,
                'text': f"{'↓' if diff < 0 else '↑'} {abs(pct):.1f}%"
            }

        if stats_30d['min']:
            diff = price - stats_30d['min']
            comparison['vs_30d_min'] = {
                'diff': diff,
                'is_new_low': diff < 0
            }

        return comparison

    def get_best_offers(
            self,
            offers: List[Dict[str, Any]],
            limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple offers and return the best ones

        Args:
            offers: List of flight offers
            limit: Maximum number of offers to return

        Returns:
            List of best offers with analysis
        """
        analyzed_offers = []

        for offer in offers:
            analysis = self.analyze_offer(offer)

            analyzed_offers.append({
                **offer,
                'analysis': analysis
            })

        # Sort by deal quality and price
        quality_order = {'amazing': 0, 'great': 1, 'good': 2, 'average': 3}

        analyzed_offers.sort(
            key=lambda x: (
                quality_order.get(x['analysis']['deal_quality'], 99),
                x['price']
            )
        )

        return analyzed_offers[:limit]

    def should_send_alert_email(self, analyzed_offers: List[Dict[str, Any]]) -> bool:
        """
        Determine if any email alert should be sent

        Args:
            analyzed_offers: List of analyzed offers

        Returns:
            True if should send alert email
        """
        for offer in analyzed_offers:
            if offer['analysis']['should_alert']:
                return True

        return False

    def get_alertable_offers(
            self,
            analyzed_offers: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Filter offers to only those that should trigger alerts

        Args:
            analyzed_offers: List of analyzed offers

        Returns:
            List of offers that should be alerted on
        """
        return [
            offer for offer in analyzed_offers
            if offer['analysis']['should_alert']
        ]