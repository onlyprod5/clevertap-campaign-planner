import requests

# link is a k-v pair (dict)

def validate_mandatory_keys(link, keys):
    for key in keys:
        if not key in link:
            return False
    return True

def validate_layout_link(link):
    if not validate_mandatory_keys(link, ["pageId", "layoutId"]):
        return False
    
    pageId = link["pageId"]
    layoutId = link["layoutId"]
    api = f"https://api.zepto.co.in/api/v1/config/layout/layout-widgets/?page_type={pageId}&layout_id={layoutId}"
    resp = None
    retries = 0

    while (resp is not None) and (retries <= 2):
        try:
            resp = requests.get(api)
        except:
            retries += 1
        

    if resp is not None and resp.status_code == 200:
        parsed_resp = resp.json()
        if "detail" in parsed_resp and parsed_resp["detail"] == "Invalid Layout Id":
            return False
        return True
    else:
        return False

def validate_product_detail_link(link):
    if not validate_mandatory_keys(link, ["productId", "productVariantId"]):
        return False
    
    productId = link["productId"]
    productVariantId = link["productVariantId"]

    ## TODO: verify the productId and productVariantId from BE, require API for this 

    return True