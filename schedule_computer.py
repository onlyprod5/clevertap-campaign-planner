from datetime import timedelta
from collections import defaultdict


def compute_best_schedule(campaigns, max_limit):
    # Data structure to keep track of users being served per 5-minute interval
    global_schedule = defaultdict(int)

    # Sort campaigns by priority (highest first) and then by start time
    campaigns.sort(key=lambda c: (c.original_schedule_time))

    # Function to get the time slots a campaign will occupy
    def get_time_slots(start_time, userbase, throttle):
        slots = []
        while userbase > 0:
            slots.append(start_time)
            serve = min(userbase, throttle)
            userbase -= serve
            start_time += timedelta(minutes=5)  # Move to the next 5-minute interval
        return slots

    campaign_notes_dict = {}

    # Iterate through campaigns and allocate time slots
    for campaign in campaigns:
        userbase = campaign.total_audience
        throttle = campaign.throttle
        start_time = campaign.original_schedule_time

        try_count = 10
        # Find the earliest valid start time for the current campaign
        while try_count > 0:
            # temp_schedule = defaultdict(int)
            temp_start_time = start_time
            temp_userbase = userbase

            # Compute the slots for the current campaign
            slots = get_time_slots(temp_start_time, userbase, throttle)

            # Check if the schedule exceeds the max limit
            exceeds_limit = False
            for slot in slots:
                remaining_userbase = temp_userbase if temp_userbase <= throttle else throttle
                if global_schedule[slot] + remaining_userbase > max_limit:
                    exceeds_limit = True
                    break
                temp_userbase -= remaining_userbase

            if not exceeds_limit:
                # If within limits, finalize this schedule
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
            else:
                # Adjust the start time to the next available slot
                try_count -= 1
                start_time += timedelta(minutes=5)

        if try_count == 0:
            print(f"Can't schedule this campaign {campaign.campaign_id}")
            campaign_notes_dict[campaign.campaign_id] = "Can't schedule this campaign as could not find time within system limits"

    print("After computing")
    for campaign in campaigns:
        print(campaign)

    return campaigns, campaign_notes_dict
