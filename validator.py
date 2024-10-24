
def validate_metadata_for_ios_and_android(ios_metadata, android_metadata, campaign_name):
    if ios_metadata != android_metadata:
        return False, "different metadata/kv pair found for ios and android"

    return validate_metadata(ios_metadata, campaign_name)

def validate_metadata(metadata, campaign_name):
    if "c_name" not in metadata:
        return False, "Missing c_name"

    if metadata["c_name"] != campaign_name:
        return False, "c_name not equal to campaign name"

    if "url" in metadata:
        if "page" not in metadata:
            return False, "url present but page missing"
        if metadata["page"] != "layout_engine":
            return False, "url present, page present, but value is not `layout_engine`"

    if "page" in metadata and "url" not in metadata:
        if metadata["page"] != "layout_engine":
            return False, "page value is not `layout_engine`; also url is missing"

        return False, "page present but url missing"

    return True, "Success"