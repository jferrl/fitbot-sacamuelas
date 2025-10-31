import argparse
import json
import time
from datetime import datetime, timedelta


from client import AimHarderClient
from exceptions import (
    NoBookingGoal,
    BoxClosed,
    MESSAGE_BOX_IS_CLOSED,
)
from exceptions import BookingFailed
from logger import logger


def wait_until_exact_time(target_time: datetime, max_wait_seconds: int = 300):
    """
    Wait until the exact target time is reached.
    
    Args:
        target_time: The datetime to wait until
        max_wait_seconds: Maximum seconds to wait (default 300 = 5 minutes)
    """
    logger.info("⏰ Precision timing mode activated - calculating wait time...")
    
    now = datetime.now()
    wait_seconds = (target_time - now).total_seconds()
    
    if wait_seconds <= 0:
        logger.info(f"Target time {target_time.strftime('%Y-%m-%d %H:%M:%S')} has already passed. Executing immediately.")
        return
    
    if wait_seconds > max_wait_seconds:
        logger.warning(
            f"Target time is {wait_seconds:.1f}s away (>{max_wait_seconds}s). "
            f"Consider triggering the job closer to booking time. Executing immediately."
        )
        return
    
    logger.info(
        f"Waiting {wait_seconds:.2f} seconds until booking window opens at "
        f"{target_time.strftime('%Y-%m-%d %H:%M:%S')}..."
    )
    time.sleep(wait_seconds)
    logger.info("Booking window is now open! Executing booking...")


def get_booking_goal_time(day: datetime, booking_goals):
    """Get the booking goal that satisfies the given day of the week"""
    try:
        return (
            booking_goals[str(day.weekday())]["time"],
            booking_goals[str(day.weekday())]["name"],
        )
    except KeyError:  # did not find a matching booking goal
        raise NoBookingGoal(
            f"There is no booking-goal for {day.strftime('%A, %Y-%m-%d')}."
        )


def get_class_to_book(classes: list[dict], target_time: str, class_name: str):
    if not classes or len(classes) == 0:
        raise BoxClosed(MESSAGE_BOX_IS_CLOSED)

    classes = list(filter(lambda _class: target_time in _class["timeid"], classes))
    _class = list(filter(lambda _class: class_name in _class["className"], classes))
    if len(_class) == 0:
        raise NoBookingGoal(
            f"No class with the text `{class_name}` in its name at time `{target_time}`"
        )
    return _class[0]


def main(
    email,
    password,
    booking_goals,
    box_name,
    box_id,
    days_in_advance=None,
    hours_in_advance=None,
    family_id=None,
    proxy=None,
):
    """
    Main booking function.
    
    Args:
        email: User email
        password: User password
        booking_goals: Dict with booking goals by day of week
        box_name: Name of the box
        box_id: ID of the box
        days_in_advance: Days in advance to book (deprecated, use hours_in_advance)
        hours_in_advance: Hours in advance to book (e.g., 46 for 46 hours)
        family_id: Optional family member ID
        proxy: Optional proxy URL
    """
    # Calculate target day using hours_in_advance or fallback to days_in_advance
    if hours_in_advance is not None:
        advance_timedelta = timedelta(hours=hours_in_advance)
    elif days_in_advance is not None:
        advance_timedelta = timedelta(days=days_in_advance)
    else:
        raise ValueError("Either hours_in_advance or days_in_advance must be provided")
    
    target_day = datetime.now() + advance_timedelta
    
    try:
        target_time, target_name = get_booking_goal_time(target_day, booking_goals)
    except NoBookingGoal as e:
        logger.info(str(e))
        return
    
    # Parse the target class time (e.g., "0800" -> 08:00)
    class_hour = int(target_time[:2])
    class_minute = int(target_time[2:])
    class_datetime = target_day.replace(hour=class_hour, minute=class_minute, second=0, microsecond=0)
    
    # Calculate when booking window opens (e.g., 46 hours before class)
    if hours_in_advance is not None:
        booking_opens_at = class_datetime - timedelta(hours=hours_in_advance)
    else:
        booking_opens_at = class_datetime - timedelta(days=days_in_advance)
    
    logger.info(f"Target class: {class_datetime.strftime('%A, %Y-%m-%d at %H:%M')} ({target_name})")
    logger.info(f"Booking window opens: {booking_opens_at.strftime('%A, %Y-%m-%d at %H:%M:%S')}")
    
    # Wait until exact booking time (precision timing always enabled)
    wait_until_exact_time(booking_opens_at)
    
    client = AimHarderClient(
        email=email, password=password, box_id=box_id, box_name=box_name, proxy=proxy
    )
    classes = client.get_classes(target_day, family_id)
    _class = get_class_to_book(classes, target_time, target_name)
    if _class["bookState"] == 1:
        logger.info("Class already booked. Nothing to do")
        return
    
    # Try to book with retry logic for "too soon" errors
    max_retries = 3
    retry_delay_seconds = 5
    
    for attempt in range(1, max_retries + 1):
        try:
            client.book_class(target_day, _class["id"], family_id)
            logger.info("Class booked successfully")
            return
        except BookingFailed as e:
            error_message = str(e)
            
            # If it's "too soon" error and we have retries left, wait and retry
            if "Too soon to book" in error_message and attempt < max_retries:
                logger.warning(
                    f"Booking window not yet open (attempt {attempt}/{max_retries}). "
                    f"Waiting {retry_delay_seconds} seconds before retry..."
                )
                time.sleep(retry_delay_seconds)
            else:
                # For other errors or if we've exhausted retries, fail
                logger.error(f"Booking failed: {error_message}")
                return


if __name__ == "__main__":
    """
    python src/main.py
     --email your.email@mail.com
     --password 1234
     --box-name lahuellacrossfit
     --box-id 3984
     --booking-goals '{"0":{"time": "1815", "name": "Provenza"}}'
     --hours-in-advance 46
     --family-id 123456
     --proxy socks5://89.58.45.94:34472
    
    Note: Precision timing is always enabled. The script will wait until the exact
    booking window opening time before executing.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", required=True, type=str)
    parser.add_argument("--password", required=True, type=str)
    parser.add_argument("--booking-goals", required=True, type=json.loads)
    parser.add_argument("--box-name", required=True, type=str)
    parser.add_argument("--box-id", required=True, type=int)
    parser.add_argument(
        "--days-in-advance",
        required=False,
        type=int,
        default=None,
        help="Days in advance to book (deprecated, use --hours-in-advance)",
    )
    parser.add_argument(
        "--hours-in-advance",
        required=False,
        type=float,
        default=None,
        help="Hours in advance to book (e.g., 46 for 46 hours, supports decimals)",
    )
    parser.add_argument("--proxy", required=False, type=str, default=None)
    parser.add_argument(
        "--family-id",
        required=False,
        type=int,
        default=None,
        help="ID of the family member (optional)",
    )
    args = parser.parse_args()
    
    # Validate that at least one advance parameter is provided
    if args.hours_in_advance is None and args.days_in_advance is None:
        parser.error("Either --hours-in-advance or --days-in-advance must be provided")
    
    input = {key: value for key, value in args.__dict__.items() if value != ""}
    main(**input)
