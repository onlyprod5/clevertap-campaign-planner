from abc import ABC, abstractmethod
import os
import requests
from urllib.parse import urlparse, parse_qs


def payload_base_validation(payload):
    if not "c_name" in payload:
        return (False, "Missing c_name")
    if payload["c_name"] != payload["campaignId"]:
        return (False, "c_name not equal to campaignId")

    if "url" in payload:
        if not "page" in payload:
            return (False, "url present but page missing")
        if not "value" in payload:
            return (False, "url present, page present, but value missing")
        if payload["value"] != "layout_engine":
            return (False, "url present, page present, but value is not `layout_engine`")

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

        validationApi = os.getenv('LAYOUT_LINK_VALIDATION_API')
        if not validationApi:
            return (False, "Unable to find layout link validation API")

        pageId = self.link["pageId"]
        layoutId = self.link["layoutId"]
        api = validationApi.format(pageId=pageId, layoutId=layoutId)
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
                return (False, "Invalid Layout Id")
            return (True, "Success")
        else:
            return (False, "Error checking data validity from config/layout/layout-widgets api")


class ProductLinkValidator(LinkValidator):
    def validate(self, link):
        if not self.validate_mandatory_keys(["productId", "productVariantId"]):
            return False

        variant_validation_api = os.getenv("PRODUCT_LINK_PID_VALIDATION_API")
        variant_validation_api_headers = os.getenv(
            "PRODUCT_LINK_PID_VALIDATION_API_HEADERS")
        if not variant_validation_api:
            return (False, "Unable to find layout link validation API")
        if not variant_validation_api_headers:
            return (False, "Unable to find layout link validation API headers")

        product_id = link["productId"]
        product_variant_id = link["productVariantId"]
        retries = 0
        variant_resp = None

        # TODO: verify the productId from BE, require API for this
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

            return (False, "Error validating product variant id")

        return (True, "Success")


def LinkValidatorFactory(link, params):
    # TODO: determine link type and update the if block below
    if link == "1":
        return LayoutLinkValidator(link=link, params=params)
    elif link == "2":
        return ProductLinkValidator(link=link, params=params)
    else:
        pass
