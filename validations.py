from abc import ABC, abstractmethod
import os
import requests
from urllib.parse import urlparse, parse_qs

from constants import PAYLOAD_CNAME, PAYLOAD_PAGE, PAYLOAD_URL


def validate_payload_metadata(payload):
    if not PAYLOAD_CNAME in payload:
        return (False, "Missing c_name")
    if payload[PAYLOAD_CNAME] != payload["campaignId"]:
        return (False, "c_name not equal to campaignId")

    url_present = PAYLOAD_URL in payload
    page_present = PAYLOAD_PAGE in payload
    page_value = payload[PAYLOAD_PAGE]

    if (url_present and not page_present) or (not url_present and page_present):
        return False, "Both url and page should be present concurrently"

    if page_present and page_value != "layout_engine":
        return False, "url present, page present, but value is not `layout_engine`"

    return (True, "Success")


class LinkValidator(ABC):
    def __init__(self, link, params={}):
        self.link = link
        self.params = params

    def extract_params(self):
        parsed_url = urlparse(self.link)
        parsed_query = parse_qs(parsed_url.query)
        for key in parsed_query:
            self.params[key] = parsed_query[key][0]

    def validate_mandatory_keys(self, keys):
        for key in keys:
            if not key in self.params:
                return False
        return True

    @abstractmethod
    def validate(self):
        pass


class LayoutLinkValidator(LinkValidator):
    def validate(self):
        if not self.validate_mandatory_keys(["pageId", "layoutId"]):
            return (False, "pageId or layoutId not found for layout link")

        validation_api = os.getenv("LAYOUT_LINK_VALIDATION_API")
        validation_api_headers = os.getenv(
            "LAYOUT_LINK_VALIDATION_API_HEADERS")
        if not validation_api:
            return (False, "Unable to find layout link validation API")
        if not validation_api_headers:
            return (False, "Unable to find layout link validation API headers")

        page_id = self.link["pageId"]
        layout_id = self.link["layoutId"]
        api = validation_api.format(pageId=page_id, layoutId=layout_id)
        resp = None
        retries = 0

        while (resp is not None) and (retries <= 2):
            try:
                resp = requests.get(api, headers=dict(validation_api_headers))
            except:
                retries += 1

        if resp is not None and resp.status_code == 200:
            parsed_resp = resp.json()
            if "detail" in parsed_resp:
                if parsed_resp["detail"] == "Invalid Layout Id":
                    return (False, "Invalid Layout Id")
                if parsed_resp["detail"] == "Invalid app version":
                    return (False, "Invalid app version, please contact the maintainer of this service")
                if parsed_resp["detail"] == "Invalid store ID in the headers":
                    return (False, "Invalid store ID in the headers, please contact the maintainer of this service")
            if "error_type" in parsed_resp:
                if parsed_resp["error_type"] == "UNHANDLED_EXCEPTION":
                    return (False, "Unhandled exception, please recheck the pageId and layoutId")
        else:
            return (False,  f"Error checking data validity from layout-widgets api: status code {resp.status_code}")

        return (True, "Success")


class ProductLinkValidator(LinkValidator):
    def validate(self):
        if not self.validate_mandatory_keys(["productId", "productVariantId"]):
            return False

        variant_validation_api = os.getenv("PRODUCT_LINK_PID_VALIDATION_API")
        variant_validation_api_headers = os.getenv(
            "PRODUCT_LINK_PID_VALIDATION_API_HEADERS")
        if not variant_validation_api:
            return (False, "Unable to find layout link validation API")
        if not variant_validation_api_headers:
            return (False, "Unable to find layout link validation API headers")

        product_id = self.link["productId"]
        product_variant_id = self.link["productVariantId"]
        retries = 0
        variant_resp = None

        while variant_resp is None and retries <= 3:
            try:
                api = variant_validation_api.format(
                    productVariantId=product_variant_id)
                variant_resp = requests.get(
                    api, headers=dict(variant_validation_api_headers))
            except:
                variant_resp = None
                retries += 1

        if variant_resp is not None and variant_resp.status_code != 200:
            if variant_resp.status_code == 204:
                return (False, "No data exists for given product variant id")
            if variant_resp.status_code == 401:
                return (False, "Unauthorised to validate product variant id, please contact the maintainer of this service")

            return (False, f"Error validating product variant id: status code {variant_resp.status_code}")

        parsed_vresp = variant_resp.json()
        if parsed_vresp["productId"] != product_id:
            return (False, "ProductVariantId does not align with the ProductId")

        return (True, "Success")


class CategoriesLinkValidator(LinkValidator):
    def validate(self):
        # TODO: complete
        pass


class UnclLinkValidator(LinkValidator):
    def validate(self):
        # TODO: complete
        pass


def LinkValidatorFactory(link, params):
    # TODO: determine link type and update the if block below
    # below is a dummy piece of code
    if link == "1":
        return LayoutLinkValidator(link=link, params=params)
    elif link == "2":
        return ProductLinkValidator(link=link, params=params)
    else:
        pass
