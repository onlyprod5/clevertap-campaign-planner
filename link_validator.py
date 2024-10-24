import os
import requests

from abc import ABC, abstractmethod
from urllib.parse import urlparse, parse_qs
from ast import literal_eval
import requests


class LinkValidator(ABC):
    def __init__(self, link):
        self.link = link
        self.params = self.extract_params()

    def extract_params(self):
        parsed_url = urlparse(self.link)
        return parse_qs(parsed_url.query)

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
            return False, "pageId or layoutId not found for layout link"

        validation_success, msg = self.validate_data()
        if not validation_success:
            return validation_success, msg

        return True, "Success"

    def validate_data(self):
        validation_api = os.getenv("LAYOUT_LINK_VALIDATION_API")
        validation_api_headers = os.getenv(
            "LAYOUT_LINK_VALIDATION_API_HEADERS")
        if not validation_api:
            return False, "Unable to find layout link validation API"
        if not validation_api_headers:
            return False, "Unable to find layout link validation API headers"

        # pageId and layoutId are present (see the callee func for ref)
        page_id = self.params.get("pageId")[0]
        layout_id = self.params.get("layoutId")[0]
        api = validation_api.format(pageId=page_id, layoutId=layout_id)
        resp = None
        retries = 0

        while resp is None and retries <= 2:
            try:
                resp = requests.get(
                    api, headers=literal_eval(validation_api_headers))
            except:
                retries += 1

        if resp is None:
            return False, "Could not validate page and layout ids"

        if resp.status_code != 200:
            parsed_resp = resp.json()
            if resp.status_code == 400:
                if "detail" in parsed_resp:
                    if parsed_resp.get("detail") == "Invalid Layout Id":
                        return False, "Invalid Layout Id"
                    if parsed_resp.get("detail") == "Invalid app version":
                        return False, "Invalid app version, please contact the maintainer of this service"
                    if parsed_resp.get("detail") == "Invalid store ID in the headers":
                        return False, "Invalid store ID in the headers, please contact the maintainer of this service"
                return False, f"Error checking data validity from layout-widgets api: status code {resp.status_code}"
            elif resp.status_code == 500:
                if "error_type" in parsed_resp:
                    if parsed_resp.get("error_type") == "UNHANDLED_EXCEPTION":
                        return False, "Invalid page or layout id"
                return False,  f"Error checking data validity from layout-widgets api: status code {resp.status_code}"
            return False, f"Unhandled error at page and layout id validation: status code {resp.status_code}"

        return True, None


class ProductLinkValidator(LinkValidator):
    def validate(self):
        if not self.validate_mandatory_keys(["productId", "productVariantId"]):
            return False, "Missing productId or productVariantId"

        validation_resp, msg = self.validate_data()
        if not validation_resp:
            return validation_resp, msg

        return True, "Success"

    def validate_data(self):
        variant_validation_api = os.getenv("PRODUCT_LINK_PID_VALIDATION_API")
        variant_validation_api_headers = os.getenv(
            "PRODUCT_LINK_PID_VALIDATION_API_HEADERS")
        if not variant_validation_api:
            return False, "Unable to find layout link validation API"
        if not variant_validation_api_headers:
            return False, "Unable to find layout link validation API headers"

        # productId and productVariantId are present (see the callee func for ref)
        product_id = self.params.get("productId")[0]
        product_variant_id = self.params.get("productVariantId")[0]
        retries = 0
        resp = None

        while resp is None and retries <= 3:
            try:
                resp = requests.post(variant_validation_api, json={
                    "productVariantIds": [
                        product_variant_id
                    ],
                    "field": [
                        "productDetails"
                    ]
                }, headers=literal_eval(variant_validation_api_headers))
            except Exception as e:
                resp = None
                retries += 1

        if resp is None:
            return False, "Unable to validate product variant id"

        if resp.status_code != 200:
            if resp.status_code == 401:
                return False, "Unauthorised to validate product variant id, please contact the maintainer of this service"
            if resp.status_code == 400:
                return False, "Bad request: please check the product variant id"

            return False, f"Error validating product variant id: status code {resp.status_code}"

        parsed_vresp = resp.json()
        pvdata = parsed_vresp["pvDetails"][0]

        if pvdata is None:
            return False, "Invalud product variant id"

        if pvdata.get("productDetails").get("productId") != product_id:
            return False, "ProductVariantId does not align with the ProductId"

        return True, None


class CategoryLinkValidator(LinkValidator):

    def validate_category_subcategory(self, category_id, sub_category_id):
        headers = {
            'x_requester_id': os.getenv('CMS_REQUESTER_ID'),
        }
        response = requests.get(
            f"{os.getenv('CMS_HOST')}/api/v1/subcategory/{sub_category_id}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            resp_category_id = data.get("category", {}).get("id")
            if category_id == resp_category_id:
                return True, "Success"
            else:
                return False, "Invalid category - subcategory mapping"
        elif response.status_code == 400:
            return False, "Invalid category or subcategory"
        else:
            return False, "Could not validate category/subcategory"

    def validate(self):
        required_params = ['categoryId', 'subCategoryId']
        if not self.validate_mandatory_keys(required_params):
            return False, f"Missing params: {', '.join(required_params)}"

        sub_category_id = self.params.get('subCategoryId', [None])[0]
        category_id = self.params.get('categoryId', [None])[0]
        if not sub_category_id or not category_id:
            return False, "no subCategoryId or categoryId provided"

        valid, message = self.validate_category_subcategory(
            category_id, sub_category_id)
        if not valid:
            return False, message

        return True, "Success"


class UnclLinkValidator(LinkValidator):
    def validate_subcategory(self, sub_category_id):
        headers = {
            'x_requester_id': os.getenv('CMS_REQUESTER_ID'),
        }
        response = requests.get(
            f"{os.getenv('CMS_HOST')}/api/v1/subcategory/{sub_category_id}", headers=headers)
        if response.status_code == 200:
            return True, "Success"
        elif response.status_code == 400:
            return False, "Invalid subcategory"
        else:
            return False, "Could not validate subcategory"

    def validate(self):
        required_params = ['scid']
        if not self.validate_mandatory_keys(required_params):
            return False, f"Missing params: {', '.join(required_params)}"

        sub_category_id = self.params.get('scid', [None])[0]

        if not sub_category_id:
            return False, "no subCategoryId provided"

        valid, message = self.validate_subcategory(sub_category_id)
        if not valid:
            return False, message

        return True, "Success"


class DefaultLinkValidator(LinkValidator):
    def validate(self):
        return False, "Unknown link: script only validates categories, ProductDetail, LayoutEngine and uncl link as of now"


class LinkValidatorFactory:
    @staticmethod
    def get_link_validator(link):
        try:
            path_first_segment = LinkValidatorFactory.validate_and_extract_path(
                link)
            if path_first_segment == "Categories":
                return CategoryLinkValidator(link)
            elif path_first_segment == "ProductDetail":
                return ProductLinkValidator(link)
            elif path_first_segment == "LayoutEngine":
                return LayoutLinkValidator(link)
            elif path_first_segment == "uncl":
                return UnclLinkValidator(link)
            else:
                return DefaultLinkValidator(link)
        except Exception as e:
            print(f"Unknown error while validating link: {link}, {str(e)}")
            raise e

    @staticmethod
    def validate_and_extract_path(url):
        parsed_url = urlparse(url)
        path = parsed_url.path

        if path.startswith('/'):
            path = path[1:]

        path_segments = path.split("/")
        return path_segments[0]


def validate_link_domain(url):
    parsed_url = urlparse(url)

    if parsed_url.netloc != os.getenv('DOMAIN') and parsed_url.netloc != f"www.{os.getenv('DOMAIN')}":
        return False, "Non org domain detected"

    return True, ""
