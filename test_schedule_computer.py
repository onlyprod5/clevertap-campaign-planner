from unittest import TestCase
from datetime import datetime
from campaign import Campaign, CampaignBuilder
from schedule_computer import compute_best_schedule


class Test(TestCase):
    def test_compute_best_schedule(self):
        campaigns = [
            CampaignBuilder().
                set_campaign_id('1').
                set_original_schedule_time(datetime.strptime("20 Sep, 2024 12:55:00", "%d %b, %Y %H:%M:%S")).
                set_total_audience(1200000).
                set_throttle(1300000).build(),
            CampaignBuilder().
                set_campaign_id('2').
                set_original_schedule_time(datetime.strptime("20 Sep, 2024 14:55:00", "%d %b, %Y %H:%M:%S")).
                set_total_audience(700000).
                set_throttle(300000).build(),
            CampaignBuilder().
                set_campaign_id('3').
                set_original_schedule_time(datetime.strptime("20 Sep, 2024 12:55:00", "%d %b, %Y %H:%M:%S")).
                set_total_audience(500000).
                set_throttle(199999).build(),
            CampaignBuilder().
                set_campaign_id('4').
                set_original_schedule_time(datetime.strptime("20 Sep, 2024 12:55:00", "%d %b, %Y %H:%M:%S")).
                set_total_audience(500000).
                set_throttle(200000).build(),
            CampaignBuilder().
                set_campaign_id('5').
                set_original_schedule_time(datetime.strptime("20 Sep, 2024 14:55:00", "%d %b, %Y %H:%M:%S")).
                set_total_audience(1500000).
                set_throttle(400000).build(),
            CampaignBuilder().
            set_campaign_id('6').
            set_original_schedule_time(datetime.strptime("20 Sep, 2024 12:55:00", "%d %b, %Y %H:%M:%S")).
            set_total_audience(500000).
            set_throttle(200000).build(),
        ]

        compute_best_schedule(campaigns, 500000)
        # asserts..tba

