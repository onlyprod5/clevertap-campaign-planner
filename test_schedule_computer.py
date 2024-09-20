# from datetime import datetime
# from campaign import CampaignBuilder
# from schedule_computer import compute_best_schedule
#
# campaigns = [
# CampaignBuilder().
#         set_campaign_id('4').
#         set_original_schedule_time(datetime.strptime("20 Sep, 2024 17:50:00", "%d %b, %Y %H:%M:%S")).
#         set_total_audience(3595145).
#         set_throttle(350000).build(),
#     CampaignBuilder().
#         set_campaign_id('5').
#         set_original_schedule_time(datetime.strptime("20 Sep, 2024 17:50:00", "%d %b, %Y %H:%M:%S")).
#         set_total_audience(1014135).
#         set_throttle(350000).build(),
#     CampaignBuilder().
#         set_campaign_id('6').
#         set_original_schedule_time(datetime.strptime("20 Sep, 2024 18:00:00", "%d %b, %Y %H:%M:%S")).
#         set_total_audience(222823).
#         set_throttle(350000).build(),
#     CampaignBuilder().
#         set_campaign_id('1').
#         set_original_schedule_time(datetime.strptime("20 Sep, 2024 18:05:00", "%d %b, %Y %H:%M:%S")).
#         set_total_audience(2365583).
#         set_throttle(750000).build(),
#     CampaignBuilder().
#         set_campaign_id('2').
#         set_original_schedule_time(datetime.strptime("20 Sep, 2024 18:05:00", "%d %b, %Y %H:%M:%S")).
#         set_total_audience(4887267).
#         set_throttle(750000).build(),
#     CampaignBuilder().
#         set_campaign_id('3').
#         set_original_schedule_time(datetime.strptime("20 Sep, 2024 18:05:00", "%d %b, %Y %H:%M:%S")).
#         set_total_audience(803985).
#         set_throttle(550000).build()
# ]
#
# compute_best_schedule(campaigns,1500000)