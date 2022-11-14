import browser_cookie3


class Cookies:
    def __init__(self, domain_name):
        self.cookies = {}
        self.domain_name = domain_name
        self.cookies = list(browser_cookie3.edge(domain_name=domain_name))

    def get(self, key):
        for cookie in self.cookies:
            if cookie.name == key:
                return cookie.value

