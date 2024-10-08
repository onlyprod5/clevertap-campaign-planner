from datetime import timedelta
from collections import defaultdict


def compute_best_schedule(campaigns, max_limit, st_time, end_time):
    # Data structure to keep track of users being served per 5-minute interval (across all campaigns)
    global_schedule = defaultdict(int)

    notification_order = { 'push': 1, 'sms': 2, '': 3 }

    # Sort campaigns by start time
    campaigns.sort(key=lambda c: (c.original_schedule_time, notification_order[c.channel]))

    # Function to get the time slots a campaign will occupy (for ex: [3:00, 3:05, 3:10, 3:15])
    def get_time_slots(start_time, userbase, throttle):
        slots = []
        while userbase > 0:
            slots.append(start_time)
            serve = min(userbase, throttle)
            userbase -= serve
            start_time += timedelta(minutes=5)  # Move to the next 5-minute interval
        return slots

    campaign_notes_dict = {}

    for campaign in campaigns:
        userbase = campaign.total_audience
        throttle = campaign.throttle
        start_time = campaign.original_schedule_time

        started_rescheduling = False

        # Find the earliest valid start time for the current campaign
        while st_time <= start_time <= end_time:
            temp_start_time = start_time
            temp_userbase = userbase

            # Compute the slots for the current campaign
            slots = get_time_slots(temp_start_time, userbase, throttle)

            # Check if the campaign exceeds the max limit for any slot it was assigned
            exceeds_limit = False
            for slot in slots:
                remaining_userbase = temp_userbase if temp_userbase <= throttle else throttle
                if global_schedule[slot] + remaining_userbase > max_limit:
                    exceeds_limit = True
                    break
                temp_userbase -= remaining_userbase

            if not exceeds_limit:
                temp_userbase = userbase
                for slot in slots:
                    serve = min(temp_userbase, throttle)
                    global_schedule[slot] += serve
                    temp_userbase -= serve

                if start_time == campaign.original_schedule_time:
                    campaign_notes_dict[campaign.campaign_id] = "NO CHANGE"
                else:
                    campaign_notes_dict[campaign.campaign_id] = "NEW TIME"

                campaign.preferred_schedule_time = start_time
                break
            else: # if exceeds limit
                if not started_rescheduling: # If not yet started rescheduling, start checking from the st_time of this script window
                    started_rescheduling = True
                    start_time = st_time
                else: # move the start time by 5 mins and check
                    start_time += timedelta(minutes=5)

        if campaign.preferred_schedule_time is None:
            print(f"Exceeded aligned limit for campaign_id {campaign.campaign_id} between {st_time} - {end_time}")
            campaign_notes_dict[campaign.campaign_id] = "EXCEEDED ALIGNED LIMIT"

    print("After computing preferred schedule time")
    for campaign in campaigns:
        print(campaign)

    return campaigns, campaign_notes_dict
