"""Helper functions and seed data for synthetic dispute case generation."""

from __future__ import annotations
import random
from typing import List, Dict, Any, Tuple
from data.schemas import (
    Auth3DSData,
    DeliveryTrackingData,
    InvoiceDispatchData,
    CustomerCommunicationLog,
    CustomerAccountData,
    RefundLogData,
    PriceBreakdownData,
    SubscriptionMandateData,
    ServiceUsageData,
)

MERCHANTS = [
    ("merch_flipkart_01", "Flipkart India", "E-commerce"),
    ("merch_myntra_02", "Myntra Fashion", "D2C"),
    ("merch_zepto_03", "Zepto Quick Commerce", "QuickCommerce"),
    ("merch_swiggy_04", "Swiggy Instamart", "QuickCommerce"),
    ("merch_postman_05", "Postman Technologies", "SaaS"),
    ("merch_cleartrip_06", "Cleartrip Travel", "Travel"),
    ("merch_unacademy_07", "Unacademy EdTech", "EdTech"),
    ("merch_cultfit_08", "Cult.fit Fitness", "D2C"),
    ("merch_zerodha_09", "Zerodha Broking", "SaaS"),
    ("merch_boat_10", "boAt Lifestyle", "D2C"),
    ("merch_zomato_11", "Zomato Dining", "QuickCommerce"),
    ("merch_makemytrip_12", "MakeMyTrip Flights", "Travel"),
    ("merch_chargebee_13", "Chargebee Subscriptions", "SaaS"),
    ("merch_lenskart_14", "Lenskart Eyewear", "D2C"),
    ("merch_nykaa_15", "Nykaa Cosmetics", "E-commerce"),
]

INDIAN_CITIES = [
    ("Bengaluru", "Karnataka", "560001", "12.9716,77.5946"),
    ("Mumbai", "Maharashtra", "400001", "19.0760,72.8777"),
    ("Delhi", "Delhi", "110001", "28.6139,77.2090"),
    ("Hyderabad", "Telangana", "500001", "17.3850,78.4867"),
    ("Pune", "Maharashtra", "411001", "18.5204,73.8567"),
    ("Chennai", "Tamil Nadu", "600001", "13.0827,80.2707"),
    ("Kolkata", "West Bengal", "700001", "22.5726,88.3639"),
    ("Ahmedabad", "Gujarat", "380001", "23.0225,72.5714"),
    ("Jaipur", "Rajasthan", "302001", "26.9124,75.7873"),
    ("Gurugram", "Haryana", "122001", "28.4595,77.0266"),
]

CARRIERS = ["Bluedart Express", "Delhivery Logistics", "Ekart Logistics", "DTDC India", "Shadowfax"]


def pick_merchant() -> Tuple[str, str, str]:
    return random.choice(MERCHANTS)


def pick_city() -> Tuple[str, str, str, str]:
    return random.choice(INDIAN_CITIES)


def generate_auth_3ds(verdict: str, amount: float) -> Auth3DSData:
    if verdict == "win":
        return Auth3DSData(
            auth_type=random.choice(["3DS_V2", "UPI_PIN"]),
            cavv_eci=random.choice(["05", "02"]),
            auth_timestamp="2026-08-15T14:22:10Z",
            status="authenticated",
            transaction_reference=f"tx_auth_{random.randint(100000, 999999)}",
            bank_reference_number=f"BRN{random.randint(100000000, 999999999)}",
            ip_address="103.21.124.55",
            device_fingerprint="fp_and_98a76bc1209e",
            vpn_detected=False,
            geo_location_match=True,
        )
    elif verdict == "lose":
        return Auth3DSData(
            auth_type="NONE",
            cavv_eci="07",
            auth_timestamp="2026-08-15T14:22:10Z",
            status="bypassed",
            transaction_reference=f"tx_auth_{random.randint(100000, 999999)}",
            bank_reference_number=None,
            ip_address="185.220.101.4",
            device_fingerprint="fp_tor_unknown_00",
            vpn_detected=True,
            geo_location_match=False,
        )
    else:  # ambiguous
        return Auth3DSData(
            auth_type="3DS_V1",
            cavv_eci="06",
            auth_timestamp="2026-08-15T14:22:10Z",
            status="attempted",
            transaction_reference=f"tx_auth_{random.randint(100000, 999999)}",
            bank_reference_number=f"BRN{random.randint(100000000, 999999999)}",
            ip_address="103.21.124.89",
            device_fingerprint="fp_and_77a90b11",
            vpn_detected=False,
            geo_location_match=False,
        )
