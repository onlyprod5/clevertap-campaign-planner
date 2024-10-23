import requests

# link is a k-v pair (dict)

def validate_layout_link(link):
    if not "pageId" in link:
        return False
    if not "layoutId" in link:
        return False
    
    pageId = link["pageId"]
    layoutId = link["layoutId"]
    api = f"https://api.zepto.co.in/api/v1/config/layout/layout-widgets/?page_type={pageId}&layout_id={layoutId}"

    resp = requests.get(api)

    if resp.status_code == 200:
        parsed_resp = resp.json()
        if "detail" in parsed_resp and parsed_resp["detail"] == "Invalid Layout Id":
            return False
        return True
    else:
        return False

def validate_product_detail_link(link):
    if not "productId" in link:
        return False
    if not "productVariantId" in link:
        return False
    
    productId = link["productId"]
    productVariantId = link["productVariantId"]

    ## TODO: verify the productId and productVariantId from BE, require API for this 

    return True