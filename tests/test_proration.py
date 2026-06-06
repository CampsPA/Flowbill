# run -> python -m pytest tests/test_proration.py

# This test proves the billing engine charges or credits the correct amount when a
#customer changes plans mid-cycle

# This follows a different pattern from .post() and .get(), calculate_proration()
# is not and endpoint, its a plain Python function, no HTTP request, 
# Here I import the function directly and call just like any other Python function.
from app.billing.proration import calculate_proration
from datetime import datetime, timezone, timedelta

def test_upgrade_proration():
    # Define the rates
    current_plan_price_cents = 100
    new_plan_price_cents = 175
    # Define the periods
    current_period_start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    current_period_end = datetime(2024, 1, 31, tzinfo=timezone.utc)
    now = datetime(2024, 1, 16, tzinfo=timezone.utc)
    

    # Call calculate_proration
    result = calculate_proration(current_plan_price_cents, new_plan_price_cents, current_period_start, current_period_end, now=now)
    assert result == 38

def test_downgrade_proration():
    # Define the rates
    current_plan_price_cents = 150
    new_plan_price_cents = 90
    # Define the periods
    current_period_start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    current_period_end = datetime(2024, 1, 31, tzinfo=timezone.utc)
    now = datetime(2024, 1, 16, tzinfo=timezone.utc)
      

    # Call calculate_proration
    result = calculate_proration(current_plan_price_cents, new_plan_price_cents, current_period_start, current_period_end, now=now)
    
    assert result == -30


def test_same_plan():
    # Define the rates
    current_plan_price_cents = 150
    new_plan_price_cents = 150
    # Define the periods
    current_period_start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    current_period_end = datetime(2024, 1, 31, tzinfo=timezone.utc)
    now = datetime(2024, 1, 16, tzinfo=timezone.utc)
    result = calculate_proration(current_plan_price_cents, new_plan_price_cents, current_period_start, current_period_end, now=now)
    assert result == 0
    


def test_mid_period_accuracy():
    # Define the rates
    current_plan_price_cents = 100
    new_plan_price_cents = 175
    # Define the periods
    current_period_start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    current_period_end = datetime(2024, 1, 31, tzinfo=timezone.utc)
    now = datetime(2024, 1, 21, tzinfo=timezone.utc)
    result = calculate_proration(current_plan_price_cents, new_plan_price_cents, current_period_start, current_period_end, now=now)
    assert result == 25




    