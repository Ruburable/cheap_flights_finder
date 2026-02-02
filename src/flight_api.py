"""
Amadeus API client for flight searches
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from amadeus import Client, ResponseError

logger = logging.getLogger(__name__)


class FlightAPI:
    """Amadeus API client wrapper"""
    
    def __init__(self, api_key: str, api_secret: str):
        self.client = Client(
            client_id=api_key,
            client_secret=api_secret
        )
        logger.info("Amadeus API client initialized")
    
    def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: datetime,
        return_date: datetime,
        adults: int = 1,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for round-trip flights
        
        Args:
            origin: Origin airport code (e.g., 'WAW')
            destination: Destination airport code (e.g., 'GRU')
            departure_date: Departure date
            return_date: Return date
            adults: Number of adult passengers
            max_results: Maximum number of results to return
        
        Returns:
            List of flight offers
        """
        try:
            logger.info(
                f"Searching flights: {origin} → {destination}, "
                f"{departure_date.date()} - {return_date.date()}"
            )
            
            response = self.client.shopping.flight_offers_search.get(
                originLocationCode=origin,
                destinationLocationCode=destination,
                departureDate=departure_date.strftime('%Y-%m-%d'),
                returnDate=return_date.strftime('%Y-%m-%d'),
                adults=adults,
                currencyCode='PLN',
                max=max_results
            )
            
            flights = response.data if hasattr(response, 'data') else []
            logger.info(f"Found {len(flights)} flight offers")
            
            return self._parse_flight_offers(flights)
            
        except ResponseError as error:
            logger.error(f"Amadeus API error: {error}")
            return []
        except Exception as e:
            logger.error(f"Flight search error: {e}")
            return []
    
    def _parse_flight_offers(self, offers: List[Any]) -> List[Dict[str, Any]]:
        """Parse Amadeus flight offers into simplified format"""
        parsed_offers = []
        
        for offer in offers:
            try:
                # Extract price
                price = float(offer.get('price', {}).get('total', 0))
                currency = offer.get('price', {}).get('currency', 'PLN')
                
                # Extract itineraries (outbound and return)
                itineraries = offer.get('itineraries', [])
                
                if len(itineraries) < 2:
                    continue  # Not a round trip
                
                outbound = self._parse_itinerary(itineraries[0])
                inbound = self._parse_itinerary(itineraries[1])
                
                parsed_offer = {
                    'id': offer.get('id'),
                    'price': price,
                    'currency': currency,
                    'outbound': outbound,
                    'inbound': inbound,
                    'total_stops': outbound['stops'] + inbound['stops'],
                    'booking_link': self._generate_booking_link(offer)
                }
                
                parsed_offers.append(parsed_offer)
                
            except Exception as e:
                logger.warning(f"Error parsing offer: {e}")
                continue
        
        return parsed_offers
    
    def _parse_itinerary(self, itinerary: Dict[str, Any]) -> Dict[str, Any]:
        """Parse a single itinerary (outbound or inbound)"""
        segments = itinerary.get('segments', [])
        
        if not segments:
            return {}
        
        first_segment = segments[0]
        last_segment = segments[-1]
        
        # Extract departure info
        departure = first_segment.get('departure', {})
        departure_airport = departure.get('iataCode')
        departure_time = departure.get('at')
        
        # Extract arrival info
        arrival = last_segment.get('arrival', {})
        arrival_airport = arrival.get('iataCode')
        arrival_time = arrival.get('at')
        
        # Calculate duration
        duration = itinerary.get('duration', 'PT0H')
        
        # Extract connection info
        stops = len(segments) - 1
        connections = []
        
        for i in range(len(segments) - 1):
            connection_airport = segments[i].get('arrival', {}).get('iataCode')
            if connection_airport:
                connections.append(connection_airport)
        
        # Extract airline info
        airlines = list(set([
            seg.get('carrierCode', '') 
            for seg in segments
        ]))
        
        return {
            'departure_airport': departure_airport,
            'departure_time': departure_time,
            'arrival_airport': arrival_airport,
            'arrival_time': arrival_time,
            'duration': duration,
            'stops': stops,
            'connections': connections,
            'airlines': airlines,
            'segments': len(segments)
        }
    
    def _generate_booking_link(self, offer: Dict[str, Any]) -> str:
        """Generate Google Flights booking link"""
        # This is a simplified version - in production, you'd want to use
        # the actual booking link from Amadeus or construct a proper deep link
        itineraries = offer.get('itineraries', [])
        
        if len(itineraries) >= 2:
            outbound = itineraries[0].get('segments', [{}])[0]
            inbound = itineraries[1].get('segments', [{}])[0]
            
            origin = outbound.get('departure', {}).get('iataCode', '')
            destination = outbound.get('arrival', {}).get('iataCode', '')
            dep_date = outbound.get('departure', {}).get('at', '')[:10]
            ret_date = inbound.get('departure', {}).get('at', '')[:10]
            
            return (
                f"https://www.google.com/flights?hl=en#flt="
                f"{origin}.{destination}.{dep_date}*"
                f"{destination}.{origin}.{ret_date}"
            )
        
        return "https://www.google.com/flights"
    
    def search_flexible_dates(
        self,
        origin: str,
        destination: str,
        departure_start: datetime,
        departure_end: datetime,
        trip_length_min: int,
        trip_length_max: int,
        max_results_per_date: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search flights across multiple date combinations
        
        Args:
            origin: Origin airport code
            destination: Destination airport code
            departure_start: Earliest departure date
            departure_end: Latest departure date
            trip_length_min: Minimum trip length in days
            trip_length_max: Maximum trip length in days
            max_results_per_date: Max results per date combination
        
        Returns:
            List of all flight offers found
        """
        all_offers = []
        current_date = departure_start
        
        while current_date <= departure_end:
            # Try different trip lengths
            for trip_length in range(trip_length_min, trip_length_max + 1):
                return_date = current_date + timedelta(days=trip_length)
                
                offers = self.search_flights(
                    origin=origin,
                    destination=destination,
                    departure_date=current_date,
                    return_date=return_date,
                    max_results=max_results_per_date
                )
                
                all_offers.extend(offers)
            
            # Move to next day
            current_date += timedelta(days=1)
        
        logger.info(f"Flexible search found {len(all_offers)} total offers")
        return all_offers
