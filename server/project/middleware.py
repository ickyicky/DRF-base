import logging


class WebRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        self.save(request, response)

        return response

    def save(self, request, response):
        if response.status_code >= 300:
            req = response.__dict__.get("renderer_context", {}).get("request", None)
            if req:
                logging.error("REQUEST:")

                def hide_pass(d):
                    if not hasattr(d, "items"):
                        return d

                    result = {}

                    for k, v in d.items():
                        if isinstance(v, list):
                            result[k] = [hide_pass(vv) for vv in v]
                        elif "pass" in k.lower():
                            result[k] = "**************"
                        else:
                            result[k] = hide_pass(v)

                    return result

                logging.error(hide_pass(req._data))

            logging.error("RESPONSE:")
            logging.error(response.__dict__.get("data"))
