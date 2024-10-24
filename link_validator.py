from abc import ABC, abstractmethod
import os
from urllib.parse import urlparse, parse_qs


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
    def validate(self):
        # TODO: complete
        return True, "Success"


class UnclLinkValidator(LinkValidator):
    def validate(self):
        # TODO: complete
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