
# Deploy an Nginx server with any static website (find on github) hosted with following requirements:-

- Site must use cache for js files only (no images or anything)
- No one must be able to find the server its being hosted on by using inspect mode (headers and all)
- There must be a dynamic rate limiter which can change request quotas (RPS) based on the client
- Server should throttle any pdf downloads to 200Kbps  (none other type files must be throttled)
- Server must only support PCI-DSS cipher suites
- Any request for a file named "Secret.json" must be dropped at TCP level (no response at all like 403 or 404)
- And I want custom error response for 3 types of error 404, 403 and last one of your choice

- Don't modify the content keep it as it is. You can breif about it by writing below the main content tagged as AI Generated content: your brief

## AI Generated content:

This write-up lists configuration requirements for hosting a static site on Nginx with strict security and traffic controls: cache only for JS, header/media obfuscation to hide server identity, dynamic per-client rate limiting, PDF-specific bandwidth throttling at 200Kbps, PCI-DSS-only TLS ciphers, dropping any request for "Secret.json" at the TCP layer, and three custom error pages (404, 403, and one additional of your choice). These requirements map directly to Nginx features (cache-control, header manipulation, ngx_http_limit_req_module or external rate-limiter, limit_rate for PDF responses, TLS cipher configuration, firewall-level drop for specific paths, and custom error_page directives).
