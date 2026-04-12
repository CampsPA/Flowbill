# This file contains one function, calculate_proration, that:

# takes the current plan, the new plan, and the current period dates, 
# and returns the prorated amount in cents.

from datetime import datetime, timezone, timedelta


# Define the required parameters:
# current_plan_price_cents
# new_plan_price_cents
# current_period_start
# current_period_end
# round results to whole cents

# Create the proration function
def calculate_proration(current_plan_price_cents : int, new_plan_price_cents : int, 
                        current_period_start : datetime, current_period_end : datetime) -> int:
    
    # The current_period_start and end were alredy calculated in subscriptions/service.py
    # inside create_subscriptio()
    
    # Calculate days in the priod and remaining days
    days_in_period = (current_period_end - current_period_start).days
    remaining_days = (current_period_end - datetime.now(timezone.utc)).days

    # Calculate daily rate for the current and new plan
    current_daily_rate = current_plan_price_cents / days_in_period
    new_daily_rate = new_plan_price_cents / days_in_period

    # Calculate crediy amount -> current daily rate * remaining days
    credit_amount = current_daily_rate * remaining_days

    # Charge -> new daily rate * remaing days
    charge = new_daily_rate * remaining_days

    # Calculate proration amount -> charge - credit
    proration_amount = charge - credit_amount

    # Return proration amount rounded to whode cents
    return round(proration_amount)