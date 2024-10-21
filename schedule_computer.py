from datetime import timedelta
from collections import defaultdict

import constants


def get_existing_schedule_per_min(campaigns):
    global_schedule = defaultdict(int)

    for campaign in campaigns:
        throttle = campaign.get_throttle_per_minute()
        slots = get_time_slots(campaign.original_schedule_time, campaign.total_audience, throttle)
        global_schedule = populate_schedule(global_schedule, slots, campaign.total_audience, throttle)

    print("Schedule per min before suggested timings")
    for k, v in global_schedule.items():
        print(k, " -> ", v)

    return global_schedule


# Function to get the time slots a campaign will occupy (for ex: [3:00, 3:01, 3:02, 3:03])
def get_time_slots(start_time, userbase, throttle):
    slots = []
    while userbase > 0:
        slots.append(start_time)
        serve = min(userbase, throttle)
        userbase -= serve
        start_time += timedelta(minutes=1)  # Move to the next-minute interval
    return slots

def populate_schedule(global_schedule, slots, userbase, throttle):
    for slot in slots:
        serve = min(userbase, throttle)
        global_schedule[slot] += serve
        userbase -= serve
    return global_schedule


def can_fit_in_schedule(global_schedule, slots, userbase, throttle, max_limit_per_min):
    for slot in slots:
        serve = min(userbase, throttle)
        if global_schedule[slot] + serve > max_limit_per_min:
            return False
        userbase -= serve
    return True

def get_campaign_preferred_time_and_status(campaign, global_schedule, max_limit_per_min, st_time, end_time):
    throttle = campaign.get_throttle_per_minute()
    userbase = campaign.total_audience
    start_time = campaign.original_schedule_time
    started_rescheduling = False

    while st_time <= start_time <= end_time:
        slots = get_time_slots(start_time, userbase, throttle)
        if can_fit_in_schedule(global_schedule, slots, userbase, throttle, max_limit_per_min):
            populate_schedule(global_schedule, slots, userbase, throttle)
            return start_time, constants.NO_CHANGE if start_time == campaign.original_schedule_time else constants.NEW_TIME
        else:
            if not started_rescheduling:
                started_rescheduling = True
                start_time = st_time
            else:
                start_time += timedelta(minutes=1)

    return None, constants.EXCEEDED_ALIGNED_LIMIT

def compute_best_schedule(campaigns, max_limit, max_limit_interval_minutes, st_time, end_time):
    max_limit_per_min = max_limit / max_limit_interval_minutes
    notification_order = { 'push': 1, 'sms': 2 }

    campaigns.sort(key=lambda c: (notification_order.get(c.channel, 99), c.original_schedule_time))

    get_existing_schedule_per_min(campaigns)

    campaign_notes_dict = {}
    global_schedule = defaultdict(int)

    for campaign in campaigns:
        preferred_time, note = get_campaign_preferred_time_and_status(campaign, global_schedule, max_limit_per_min, st_time, end_time)
        campaign.preferred_schedule_time = preferred_time
        campaign_notes_dict[campaign.campaign_id] = note

    print("After computing preferred schedule time")
    for campaign in campaigns:
        print(campaign)

    print("Schedule per min after suggested timings")
    for k,v in global_schedule.items():
        print(k, " -> ", v)

    return campaigns, campaign_notes_dict
