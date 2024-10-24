from abc import ABC, abstractmethod
import os
from urllib.parse import urlparse, parse_qs
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
        return True, "Success"


class ProductLinkValidator(LinkValidator):
    def validate(self):
        return True, "Success"


class CategoryLinkValidator(LinkValidator):

    def validate_category_subcategory(self, category_id, sub_category_id):
        headers = {
            'x_requester_id': os.getenv('CMS_REQUESTER_ID'),
        }
        response = requests.get(f"{os.getenv('CMS_HOST')}/api/v1/subcategory/{sub_category_id}", headers=headers)
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

        valid, message = self.validate_category_subcategory(category_id, sub_category_id)
        if not valid:
            return False, message

        return True, "Success"


class UnclLinkValidator(LinkValidator):
    def validate_subcategory(self, sub_category_id):
        headers = {
            'x_requester_id': os.getenv('CMS_REQUESTER_ID'),
        }
        response = requests.get(f"{os.getenv('CMS_HOST')}/api/v1/subcategory/{sub_category_id}", headers=headers)
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
            path_first_segment = LinkValidatorFactory.validate_and_extract_path(link)
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