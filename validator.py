
from constants import PAYLOAD_CAMPAIGNID, PAYLOAD_CNAME, PAYLOAD_PAGE, PAYLOAD_URL


def validate_metadata_for_ios_and_android(ios_metadata, android_metadata, campaign_name):
    if ios_metadata != android_metadata:
        return False, "different metadata/kv pair found for ios and android"

    return validate_metadata(ios_metadata, campaign_name)


def validate_metadata(payload):
    if not PAYLOAD_CNAME in payload:
        return False, f"Missing {PAYLOAD_CNAME}"
    if payload[PAYLOAD_CNAME] != payload[PAYLOAD_CAMPAIGNID]:
        return False, f"{PAYLOAD_CNAME} not equal to {PAYLOAD_CAMPAIGNID}"

    url_present = PAYLOAD_URL in payload
    page_present = PAYLOAD_PAGE in payload
    page_value = payload[PAYLOAD_PAGE]

    if (url_present and not page_present) or (not url_present and page_present):
        return False, f"Both {PAYLOAD_URL} and {PAYLOAD_PAGE} should be present concurrently"

    if page_present and page_value != "layout_engine":
        return False, f"{PAYLOAD_URL} present, {PAYLOAD_PAGE} present, but value is not `layout_engine`"

    return True, "Success"
