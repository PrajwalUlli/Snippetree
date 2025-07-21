# PyPI Modules
from rnet import BlockingClient, Cookie, Impersonate

# Local Modules
from Structlog.create_logger import setup_logging


class Spider:
    def __init__(
        self,
        logging: bool = False,
        impersonate: Impersonate = Impersonate.Chrome133,
        timeout: int = 30,
        connect_timeout: int = 10,
        pool_max_idle_per_host: int = 10,
    ) -> None:
        self.log = setup_logging(enable_log=logging)
        self.client = BlockingClient(
            impersonate=impersonate,
            cookie_store=True,
            timeout=timeout,
            connect_timeout=connect_timeout,
            pool_max_idle_per_host=pool_max_idle_per_host,
            gzip=True,  # Always enabled for better performance
            brotli=True,  # Always enabled for better performance
        )

    def _set_cookie(self, cookie: list) -> None:
        # handle value missing cases
        if len(cookie) != 3:
            message = "Missing fields in cookie"
            raise ValueError(message)

        # setting cookie
        self.client.set_cookie(cookie[0], Cookie(name=cookie[1], value=cookie[2]))
        self.log.info("Cookie set")

    def json_data(self, url: str, cookie: list | None = None) -> dict:
        if cookie:
            self._set_cookie(cookie)

        self.log.info("Starting spider : %s", url)

        try:
            response = self.client.get(url)
            if response is not None:
                # Check response status
                if response.status >= 400:
                    self.log.warning("HTTP error %d for URL: %s", response.status, url)
                    return {}

                self.log.info("URL data found! Status: %d", response.status)
                return response.json()
            # else:
            self.log.error("No response received: %s", url)
            return {}

        except Exception:
            self.log.exception("Request failed for %s", url)
            return {}

    def html_data(self, url: str, cookie: list | None = None) -> str:
        if cookie:
            self._set_cookie(cookie)

        self.log.info("Starting spider : %s", url)

        try:
            response = self.client.get(url)
            if response is not None:
                # Check response status
                if response.status >= 400:
                    self.log.warning("HTTP error %d for URL: %s", response.status, url)
                    return ""

                # checking for redirects
                if response.status == 302:
                    self.log.warning(
                        "Redirect detected from %s to %s", url, response.headers.get("Location")
                    )
                    return ""

                self.log.info("URL data found! Status: %d", response.status)
                return response.text()
            # else:
            self.log.error("No response received: %s", url)
            return ""
        except Exception:
            self.log.exception("Request failed for %s", url)
            return ""
