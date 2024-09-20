class Campaign:
    def __init__(self, campaign_id, total_audience, throttle, original_schedule_time, preferred_schedule_time):
        self.campaign_id = campaign_id
        self.total_audience = total_audience
        self.throttle = throttle
        self.original_schedule_time = original_schedule_time
        self.preferred_schedule_time = preferred_schedule_time

    def __str__(self):
        return (f"Campaign ID: {self.campaign_id}, Start Time: {self.original_schedule_time}, Total Audience: {self.total_audience}, Throttle: {self.throttle},"
                f"Preferred Start Time {self.preferred_schedule_time}")

class CampaignBuilder:
    def __init__(self):
        self.original_schedule_time = None
        self.throttle = None
        self.total_audience = None
        self.campaign_id = None
        self.preferred_schedule_time = None

    def set_campaign_id(self, campaign_id):
        self.campaign_id = campaign_id
        return self

    def set_total_audience(self, total_audience):
        self.total_audience = total_audience
        return self

    def set_throttle(self, throttle):
        self.throttle = throttle
        return self

    def set_original_schedule_time(self, original_schedule_time):
        self.original_schedule_time = original_schedule_time
        return self

    def set_preferred_schedule_time(self, preferred_schedule_time):
        self.preferred_schedule_time = preferred_schedule_time
        return self


    def build(self):
        return Campaign(self.campaign_id, self.total_audience, self.throttle, self.original_schedule_time, self.preferred_schedule_time)
