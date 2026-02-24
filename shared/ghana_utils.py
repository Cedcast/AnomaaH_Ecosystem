"""
Ghana-specific utilities for AnomaaH Delivery Platform

This module provides utilities for validating and formatting data
specific to Ghana's market requirements.
"""

import re
from typing import Optional, Dict, List
from datetime import datetime, time
import pytz

# Ghana timezone
GHANA_TZ = pytz.timezone('Africa/Accra')

# Phone number validation
GHANA_PHONE_REGEX = r'^(\+233|0)[2-5][0-9]{8}$'
GHANA_PHONE_NETWORKS = {
    '020': 'Vodafone',
    '050': 'Vodafone',
    '023': 'MTN',
    '024': 'MTN',
    '025': 'MTN',
    '053': 'MTN',
    '054': 'MTN',
    '055': 'MTN',
    '026': 'AirtelTigo',
    '027': 'AirtelTigo',
    '056': 'AirtelTigo',
    '057': 'AirtelTigo',
    '028': 'Expresso (Defunct)',
}

# Major cities and regions
GHANA_REGIONS = [
    'Greater Accra',
    'Ashanti',
    'Western',
    'Eastern',
    'Central',
    'Northern',
    'Upper East',
    'Upper West',
    'Volta',
    'Brong-Ahafo',
    'Bono',
    'Bono East',
    'Ahafo',
    'Savannah',
    'North East',
    'Oti',
]

MAJOR_CITIES = {
    'Greater Accra': ['Accra', 'Tema', 'Kasoa', 'Madina', 'Teshie', 'Nungua', 'Dome'],
    'Ashanti': ['Kumasi', 'Obuasi', 'Ejisu', 'Konongo', 'Mampong'],
    'Western': ['Takoradi', 'Sekondi', 'Tarkwa', 'Axim'],
    'Eastern': ['Koforidua', 'Akosombo', 'Nsawam', 'Akim Oda'],
    'Central': ['Cape Coast', 'Winneba', 'Kasoa', 'Elmina'],
}

# Service hours (Ghana time)
SERVICE_HOURS = {
    'start': time(6, 0),   # 6:00 AM
    'end': time(22, 0),    # 10:00 PM
}

# Traffic peak hours in Accra
TRAFFIC_PEAK_HOURS = [
    (time(7, 0), time(9, 30)),    # Morning rush
    (time(16, 0), time(19, 0)),   # Evening rush
]


def validate_ghana_phone(phone: str) -> Dict[str, any]:
    """
    Validate and extract information from Ghana phone number.
    
    Args:
        phone: Phone number to validate
        
    Returns:
        Dictionary with validation result and network info
        
    Example:
        >>> validate_ghana_phone("+233244123456")
        {
            'valid': True,
            'formatted': '+233244123456',
            'network': 'MTN',
            'prefix': '024'
        }
        
        >>> validate_ghana_phone("0201234567")
        {
            'valid': True,
            'formatted': '+233201234567',
            'network': 'Vodafone',
            'prefix': '020'
        }
    """
    result = {
        'valid': False,
        'formatted': None,
        'network': None,
        'prefix': None,
        'error': None
    }
    
    if not phone:
        result['error'] = 'Phone number is required'
        return result
    
    # Remove spaces and dashes
    phone = phone.replace(' ', '').replace('-', '')
    
    # Validate format
    if not re.match(GHANA_PHONE_REGEX, phone):
        result['error'] = 'Invalid Ghana phone number format. Expected: +233XXXXXXXXX or 0XXXXXXXXX'
        return result
    
    # Convert to international format
    if phone.startswith('0'):
        phone = '+233' + phone[1:]
    
    # Extract network prefix (digits 4-6 after +233)
    prefix = phone[4:7]
    
    result['valid'] = True
    result['formatted'] = phone
    result['prefix'] = prefix
    result['network'] = GHANA_PHONE_NETWORKS.get(prefix, 'Unknown')
    
    return result


def format_ghana_phone(phone: str, format_type: str = 'international') -> Optional[str]:
    """
    Format Ghana phone number.
    
    Args:
        phone: Phone number to format
        format_type: 'international' (+233...) or 'local' (0...)
        
    Returns:
        Formatted phone number or None if invalid
        
    Example:
        >>> format_ghana_phone("0244123456", "international")
        '+233244123456'
        
        >>> format_ghana_phone("+233244123456", "local")
        '0244123456'
    """
    validation = validate_ghana_phone(phone)
    
    if not validation['valid']:
        return None
    
    formatted = validation['formatted']
    
    if format_type == 'local':
        return '0' + formatted[4:]
    
    return formatted


def is_service_hours(dt: Optional[datetime] = None) -> bool:
    """
    Check if given time is within service hours (6 AM - 10 PM Ghana time).
    
    Args:
        dt: Datetime to check (defaults to current time in Ghana)
        
    Returns:
        True if within service hours
        
    Example:
        >>> is_service_hours(datetime(2026, 2, 24, 8, 0))  # 8 AM
        True
        
        >>> is_service_hours(datetime(2026, 2, 24, 23, 0))  # 11 PM
        False
    """
    if dt is None:
        dt = datetime.now(GHANA_TZ)
    elif dt.tzinfo is None:
        # Assume UTC, convert to Ghana time
        dt = pytz.utc.localize(dt).astimezone(GHANA_TZ)
    
    current_time = dt.time()
    return SERVICE_HOURS['start'] <= current_time <= SERVICE_HOURS['end']


def is_peak_traffic_time(dt: Optional[datetime] = None) -> bool:
    """
    Check if given time is during Accra peak traffic hours.
    
    Args:
        dt: Datetime to check (defaults to current time in Ghana)
        
    Returns:
        True if during peak traffic
        
    Example:
        >>> is_peak_traffic_time(datetime(2026, 2, 24, 8, 0))  # 8 AM
        True
        
        >>> is_peak_traffic_time(datetime(2026, 2, 24, 14, 0))  # 2 PM
        False
    """
    if dt is None:
        dt = datetime.now(GHANA_TZ)
    elif dt.tzinfo is None:
        dt = pytz.utc.localize(dt).astimezone(GHANA_TZ)
    
    current_time = dt.time()
    
    for start, end in TRAFFIC_PEAK_HOURS:
        if start <= current_time <= end:
            return True
    
    return False


def calculate_surge_multiplier(dt: Optional[datetime] = None) -> float:
    """
    Calculate surge pricing multiplier based on time and traffic.
    
    Args:
        dt: Datetime to check (defaults to current time)
        
    Returns:
        Surge multiplier (1.0 = normal, 1.5 = 50% surge, etc.)
        
    Example:
        >>> calculate_surge_multiplier(datetime(2026, 2, 24, 8, 0))  # Peak
        1.3
        
        >>> calculate_surge_multiplier(datetime(2026, 2, 24, 14, 0))  # Normal
        1.0
    """
    if not is_service_hours(dt):
        # Night delivery premium
        return 1.5
    
    if is_peak_traffic_time(dt):
        # Peak traffic surcharge
        return 1.3
    
    # Normal pricing
    return 1.0


def validate_ghana_address(address: Dict[str, str]) -> Dict[str, any]:
    """
    Validate Ghana address components.
    
    Args:
        address: Dictionary with 'city', 'region', 'area', 'address_line'
        
    Returns:
        Validation result dictionary
        
    Example:
        >>> validate_ghana_address({
        ...     'city': 'Accra',
        ...     'region': 'Greater Accra',
        ...     'area': 'Osu',
        ...     'address_line': 'Oxford Street'
        ... })
        {'valid': True, 'errors': []}
    """
    result = {
        'valid': True,
        'errors': []
    }
    
    # Check required fields
    required_fields = ['city', 'region', 'address_line']
    for field in required_fields:
        if not address.get(field):
            result['valid'] = False
            result['errors'].append(f'{field} is required')
    
    # Validate region
    region = address.get('region')
    if region and region not in GHANA_REGIONS:
        result['valid'] = False
        result['errors'].append(f'Invalid region. Must be one of: {", ".join(GHANA_REGIONS[:5])}...')
    
    # Validate city is in region
    city = address.get('city')
    if region and city:
        cities_in_region = MAJOR_CITIES.get(region, [])
        # We don't enforce this strictly as there are many cities
        # but we can warn if it's not in our list
        if cities_in_region and city not in cities_in_region:
            # Just a warning, not an error
            result['warning'] = f'City "{city}" not in our database for {region}'
    
    return result


def format_ghana_currency(amount: float, show_symbol: bool = True) -> str:
    """
    Format amount in Ghana Cedis.
    
    Args:
        amount: Amount to format
        show_symbol: Whether to show GH₵ symbol
        
    Returns:
        Formatted currency string
        
    Example:
        >>> format_ghana_currency(15.50)
        'GH₵ 15.50'
        
        >>> format_ghana_currency(15.50, show_symbol=False)
        '15.50'
    """
    formatted = f'{amount:.2f}'
    
    if show_symbol:
        return f'GH₵ {formatted}'
    
    return formatted


def calculate_delivery_fee(distance_km: float, dt: Optional[datetime] = None) -> Dict[str, any]:
    """
    Calculate delivery fee with Ghana-specific pricing and surge.
    
    Args:
        distance_km: Distance in kilometers
        dt: Datetime for surge calculation
        
    Returns:
        Dictionary with fee breakdown
        
    Example:
        >>> calculate_delivery_fee(5.0)
        {
            'base_fee': 5.0,
            'distance_fee': 7.5,
            'surge_multiplier': 1.0,
            'subtotal': 12.5,
            'total': 12.5,
            'total_formatted': 'GH₵ 12.50'
        }
    """
    BASE_FEE = 5.0
    PER_KM_RATE = 1.5
    
    surge = calculate_surge_multiplier(dt)
    
    distance_fee = distance_km * PER_KM_RATE
    subtotal = BASE_FEE + distance_fee
    total = subtotal * surge
    
    return {
        'base_fee': BASE_FEE,
        'distance_fee': distance_fee,
        'surge_multiplier': surge,
        'surge_reason': _get_surge_reason(dt),
        'subtotal': subtotal,
        'total': round(total, 2),
        'total_formatted': format_ghana_currency(total),
        'currency': 'GHS',
    }


def _get_surge_reason(dt: Optional[datetime] = None) -> Optional[str]:
    """Get reason for surge pricing."""
    if not is_service_hours(dt):
        return 'Night delivery premium'
    elif is_peak_traffic_time(dt):
        return 'Peak traffic hours'
    return None


def get_mobile_money_providers() -> List[Dict[str, str]]:
    """
    Get list of supported mobile money providers in Ghana.
    
    Returns:
        List of provider dictionaries
    """
    return [
        {
            'code': 'mtn',
            'name': 'MTN Mobile Money',
            'short_name': 'MTN MoMo',
            'ussd_code': '*170#',
            'prefixes': ['023', '024', '025', '053', '054', '055']
        },
        {
            'code': 'vodafone',
            'name': 'Vodafone Cash',
            'short_name': 'Vodafone Cash',
            'ussd_code': '*110#',
            'prefixes': ['020', '050']
        },
        {
            'code': 'airteltigo',
            'name': 'AirtelTigo Money',
            'short_name': 'AirtelTigo Money',
            'ussd_code': '*110#',
            'prefixes': ['026', '027', '056', '057']
        },
    ]


def detect_mobile_money_provider(phone: str) -> Optional[Dict[str, str]]:
    """
    Detect mobile money provider from phone number.
    
    Args:
        phone: Ghana phone number
        
    Returns:
        Provider info or None
        
    Example:
        >>> detect_mobile_money_provider("0244123456")
        {'code': 'mtn', 'name': 'MTN Mobile Money', ...}
    """
    validation = validate_ghana_phone(phone)
    
    if not validation['valid']:
        return None
    
    prefix = validation['prefix']
    providers = get_mobile_money_providers()
    
    for provider in providers:
        if prefix in provider['prefixes']:
            return provider
    
    return None


# Language support (basic)
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'tw': 'Twi (Akan)',
    'ga': 'Ga',
}

SMS_TEMPLATES = {
    'order_confirmed': {
        'en': 'Your order #{order_id} has been confirmed. Delivery in {eta} mins. Track: {tracking_url}',
        'tw': 'Wo order #{order_id} no asɛe. Wɔbɛbrɛ wo nneɛma wɔ simma {eta} mu. Track: {tracking_url}',
        'ga': 'Wo order #{order_id} aba. Delivery le minute {eta} shikɛ. Track: {tracking_url}',
    },
    'rider_assigned': {
        'en': 'Rider {rider_name} ({rider_phone}) has been assigned to your delivery.',
        'tw': 'Rider {rider_name} ({rider_phone}) bɛfa wo nneɛma no akɔbrɛ wo.',
        'ga': 'Rider {rider_name} ({rider_phone}) ni ba wo delivery no.',
    },
    'out_for_delivery': {
        'en': 'Your order is out for delivery. Arriving soon!',
        'tw': 'Wo nneɛma no rekɔ wo nkyɛn. Ɛrebɛduru ntɛm!',
        'ga': 'Wo order le kome. E ba ka nikɛ!',
    },
    'delivered': {
        'en': 'Your order has been delivered. Thank you!',
        'tw': 'Wo nneɛma no aduru. Yɛda wo ase!',
        'ga': 'Wo order aba. Oyiwaladonɔ!',
    },
}


def get_sms_template(event: str, language: str = 'en', **kwargs) -> str:
    """
    Get localized SMS template.
    
    Args:
        event: Event name (e.g., 'order_confirmed')
        language: Language code ('en', 'tw', 'ga')
        **kwargs: Template variables
        
    Returns:
        Formatted SMS message
        
    Example:
        >>> get_sms_template('order_confirmed', 'en', 
        ...                  order_id='12345', eta=30, tracking_url='https://...')
        'Your order #12345 has been confirmed. Delivery in 30 mins. Track: https://...'
    """
    templates = SMS_TEMPLATES.get(event, {})
    template = templates.get(language, templates.get('en', ''))
    
    if not template:
        return ''
    
    try:
        return template.format(**kwargs)
    except KeyError:
        # If missing variables, return English template
        return templates.get('en', '').format(**kwargs)


# Validation summary function
def validate_booking_data(data: Dict) -> Dict[str, any]:
    """
    Comprehensive validation for booking data with Ghana-specific checks.
    
    Args:
        data: Booking data dictionary
        
    Returns:
        Validation result with errors/warnings
    """
    result = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    # Validate phone number
    if 'customer_phone' in data:
        phone_result = validate_ghana_phone(data['customer_phone'])
        if not phone_result['valid']:
            result['valid'] = False
            result['errors'].append(f"Phone: {phone_result['error']}")
    
    # Validate pickup address
    if 'pickup_address' in data:
        addr_result = validate_ghana_address(data['pickup_address'])
        if not addr_result['valid']:
            result['valid'] = False
            result['errors'].extend([f"Pickup address: {e}" for e in addr_result['errors']])
        if 'warning' in addr_result:
            result['warnings'].append(f"Pickup address: {addr_result['warning']}")
    
    # Validate delivery address
    if 'delivery_address' in data:
        addr_result = validate_ghana_address(data['delivery_address'])
        if not addr_result['valid']:
            result['valid'] = False
            result['errors'].extend([f"Delivery address: {e}" for e in addr_result['errors']])
        if 'warning' in addr_result:
            result['warnings'].append(f"Delivery address: {addr_result['warning']}")
    
    # Check service hours
    if not is_service_hours():
        result['warnings'].append('Booking outside service hours (6 AM - 10 PM). Additional charges may apply.')
    
    return result


if __name__ == '__main__':
    # Demo usage
    print("=== Ghana Utilities Demo ===\n")
    
    # Phone validation
    print("1. Phone Validation:")
    phone_tests = ['+233244123456', '0244123456', '0501234567', '1234567890']
    for phone in phone_tests:
        result = validate_ghana_phone(phone)
        print(f"  {phone}: {result}")
    
    print("\n2. Service Hours Check:")
    print(f"  Currently in service hours: {is_service_hours()}")
    print(f"  Currently peak traffic: {is_peak_traffic_time()}")
    
    print("\n3. Delivery Fee Calculation:")
    fee = calculate_delivery_fee(5.0)
    print(f"  5km delivery: {fee}")
    
    print("\n4. Mobile Money Detection:")
    provider = detect_mobile_money_provider('0244123456')
    print(f"  0244123456: {provider}")
    
    print("\n5. SMS Templates:")
    msg = get_sms_template('order_confirmed', 'tw', 
                          order_id='12345', eta=30, 
                          tracking_url='https://track.anomaah.gh/12345')
    print(f"  Twi: {msg}")
