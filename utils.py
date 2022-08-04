def ensure_scheme(domain):
    """Helper utility for ensuring a domain has a scheme. If none is attached
       this will use the https scheme.

       Note: this will break if domain has a non http(s) scheme.
       example.com ==> https://example.com
       http://example.com ==> http://example.com
       file://example.com ==> https://file://example.com
    """
    if not domain.startswith('http'):
        domain = f'https://{domain}'
    return domain
