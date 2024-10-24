class Campaign:
    def __init__(self, campaign_id, name, total_audience, throttle, original_schedule_time, preferred_schedule_time, channel, custom_metadata,
                 schedule_time_notes, validation_notes):
        self.campaign_id = campaign_id
        self.name = name
        self.total_audience = total_audience
        self.throttle = throttle
        self.original_schedule_time = original_schedule_time
        self.preferred_schedule_time = preferred_schedule_time
        self.channel = channel
        self.custom_metadata = custom_metadata
        self.schedule_time_notes = schedule_time_notes
        self.validation_notes = validation_notes

    def get_throttle_per_minute(self):
        return self.throttle / 5  # todo: make this unit variable/dynamic later.

    def __str__(self):
        return (f"Campaign ID: {self.campaign_id}, Name: {self.name}, Total Audience: {self.total_audience}, Throttle: {self.throttle}"
                f"Original Schedule Time: {self.original_schedule_time}, Preferred Schedule Time {self.preferred_schedule_time}, "
                f"Metadata {self.custom_metadata}, Schedule Time Notes: {self.schedule_time_notes}, Validation Notes: {self.validation_notes}")

class CampaignBuilder:
    def __init__(self):
        self.original_schedule_time = None
        self.throttle = None
        self.total_audience = None
        self.campaign_id = None
        self.preferred_schedule_time = None
        self.channel = None
        self.name = None
        self.custom_metadata = None
        self.schedule_time_notes = None
        self.validation_notes = None

    def set_campaign_id(self, campaign_id):
        self.campaign_id = campaign_id
        return self

    def set_name(self, name):
        self.name = name
        return self

    def set_channel(self, channel):
        self.channel = channel
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

    def set_custom_metadata(self, custom_metadata):
        self.custom_metadata = custom_metadata
        return self

    def set_schedule_time_notes(self, schedule_time_notes):
        self.schedule_time_notes = schedule_time_notes
        return self

    def set_validation_notes(self, validation_notes):
        self.validation_notes = validation_notes
        return self

    def build(self):
        return Campaign(self.campaign_id, self.name, self.total_audience, self.throttle, self.original_schedule_time, self.preferred_schedule_time, self.channel,
                        self.custom_metadata, self.schedule_time_notes, self.validation_notes)
