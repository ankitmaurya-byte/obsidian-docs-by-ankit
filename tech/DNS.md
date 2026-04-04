# DNS

## What is DNS
```
overview:
  full_name: Domain Name System
  type: Hierarchical distributed naming system
  purpose: Translates human-readable domain names to IP addresses
  transport: UDP port 53 (queries), TCP port 53 (zone transfers, large responses)
  analogy: Phone book of the internet

key_features:
  - Distributed database (no single point of failure)
  - Hierarchical namespace (root -> TLD -> domain -> subdomain)
  - Caching at every level for performance
  - Supports multiple record types (A, AAAA, CNAME, MX, etc.)
  - Anycast routing for root and TLD servers
  - DNSSEC for authentication and integrity
```

## How DNS Resolution Works
```
resolution_flow:
  example: "Browser wants to resolve api.example.com"

  1_browser_cache:
    check: Browser checks its own DNS cache
    if_found: Use cached IP, done
    if_not: Proceed to OS resolver

  2_os_resolver:
    check: Operating system checks /etc/hosts and local DNS cache
    linux_cache: systemd-resolved or nscd
    macos_cache: mDNSResponder
    if_not: Query the configured recursive resolver

  3_recursive_resolver:
    who: ISP DNS server or public resolver (8.8.8.8, 1.1.1.1)
    behavior: Does the heavy lifting of walking the DNS tree
    check_cache: If answer is cached and TTL not expired, return it

  4_root_nameserver:
    query: "Where is .com?"
    response: "Ask these TLD nameservers for .com"
    note: 13 root server clusters (a.root-servers.net through m.root-servers.net)
    count: Hundreds of actual servers via anycast

  5_tld_nameserver:
    query: "Where is example.com?"
    response: "Ask these authoritative nameservers for example.com"
    examples: ".com, .org, .net, .io, .dev"

  6_authoritative_nameserver:
    query: "What is the IP of api.example.com?"
    response: "api.example.com -> 93.184.216.34"
    note: This is the definitive source of truth for the domain

  7_response_propagates:
    flow:
      - Authoritative server responds to recursive resolver
      - Recursive resolver caches the answer (for TTL duration)
      - Recursive resolver responds to OS
      - OS caches and responds to browser
      - Browser caches and connects to IP

  total_time: "Typically 20-120ms for uncached, <1ms for cached"
```

## DNS Record Types
```
record_types:
  A:
    purpose: Maps domain to IPv4 address
    format: "example.com. IN A 93.184.216.34"
    example: "example.com -> 93.184.216.34"
    note: Most common record type

  AAAA:
    purpose: Maps domain to IPv6 address
    format: "example.com. IN AAAA 2606:2800:220:1:248:1893:25c8:1946"
    note: "Quad-A (four A's because IPv6 is 4x longer)"

  CNAME:
    purpose: Alias one domain to another (canonical name)
    format: "www.example.com. IN CNAME example.com."
    use_case: Point www to root domain, CDN aliases
    rules:
      - Cannot coexist with other records for same name
      - Cannot be used at zone apex (root domain)
      - Causes extra DNS lookup (resolve CNAME then resolve target)

  MX:
    purpose: Mail exchange server for the domain
    format: "example.com. IN MX 10 mail.example.com."
    priority: Lower number = higher priority
    example: |
      example.com. IN MX 10 mail1.example.com.
      example.com. IN MX 20 mail2.example.com.
    note: mail1 is primary, mail2 is fallback

  TXT:
    purpose: Arbitrary text data for a domain
    format: 'example.com. IN TXT "v=spf1 include:_spf.google.com ~all"'
    use_cases:
      - SPF (email sender verification)
      - DKIM (email signing)
      - DMARC (email authentication policy)
      - Domain ownership verification (Google, Let's Encrypt)
      - Custom metadata

  NS:
    purpose: Specifies authoritative nameservers for a domain
    format: "example.com. IN NS ns1.example.com."
    example: |
      example.com. IN NS ns1.cloudflare.com.
      example.com. IN NS ns2.cloudflare.com.
    note: Set at registrar to delegate to hosting provider

  SOA:
    purpose: Start of Authority - primary nameserver and zone parameters
    format: |
      example.com. IN SOA ns1.example.com. admin.example.com. (
        2024010101  ; serial number (incremented on changes)
        3600        ; refresh (seconds before slave checks master)
        900         ; retry (seconds before retry after failed refresh)
        1209600     ; expire (seconds before slave stops serving)
        86400       ; minimum TTL (negative caching TTL)
      )

  SRV:
    purpose: Service location (host and port for a service)
    format: "_service._proto.name. IN SRV priority weight port target."
    example: "_http._tcp.example.com. IN SRV 10 60 8080 server1.example.com."
    use_case: Service discovery, SIP, XMPP, Kubernetes

  PTR:
    purpose: Reverse DNS - maps IP address to domain name
    format: "34.216.184.93.in-addr.arpa. IN PTR example.com."
    use_case: Email server verification, logging
```

## TTL (Time to Live)
```
ttl:
  what: How long (in seconds) a DNS record should be cached
  set_by: Domain owner in DNS zone configuration

  common_values:
    "300": "5 minutes - for records that change often"
    "3600": "1 hour - standard for most records"
    "86400": "24 hours - for stable records"
    "604800": "7 days - for very static records"

  trade_offs:
    low_ttl:
      pros:
        - Changes propagate quickly
        - Fast failover to backup servers
      cons:
        - More DNS queries (higher load on DNS servers)
        - Slightly higher latency for users

    high_ttl:
      pros:
        - Fewer DNS queries (better performance)
        - More resilient to DNS outages
      cons:
        - Changes take longer to propagate
        - Harder to do quick failovers

  best_practice:
    normal: "3600 (1 hour) for most records"
    before_migration: "Lower TTL to 300 (5 min) 24-48 hours before changing records"
    after_migration: "Raise TTL back to 3600 after confirming new records work"
    cdn_load_balancer: "60-300 seconds for dynamic routing"
```

## DNS Caching and Propagation
```
caching:
  layers:
    browser: "Chrome caches DNS for ~60 seconds"
    os: "OS resolver cache (systemd-resolved, mDNSResponder)"
    router: "Home/office router may cache DNS"
    isp_resolver: "ISP recursive resolver caches per TTL"

  flush_cache:
    chrome: "chrome://net-internals/#dns -> Clear host cache"
    macos: "sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder"
    linux: "sudo systemd-resolve --flush-caches"
    windows: "ipconfig /flushdns"

propagation:
  what: Time for DNS changes to be seen globally
  depends_on:
    - Previous TTL value (caches hold old record until TTL expires)
    - Resolver behavior (some ignore TTL, cache longer)
    - Number of caching layers
  typical_time: "Minutes to 48 hours (usually under 1 hour with low TTL)"
  note: "DNS propagation is really just cache expiration at different resolvers"
```

## DNS Commands
```
commands:
  dig:
    description: DNS lookup utility (most detailed)
    basic: "dig example.com"
    specific_record: "dig example.com MX"
    specific_server: "dig @8.8.8.8 example.com"
    short_output: "dig example.com +short"
    trace_resolution: "dig example.com +trace"
    all_records: "dig example.com ANY"
    reverse_lookup: "dig -x 93.184.216.34"
    output_sections:
      QUESTION: "What was asked"
      ANSWER: "The DNS records returned"
      AUTHORITY: "Nameservers that are authoritative"
      ADDITIONAL: "Extra info (glue records)"

  nslookup:
    description: Simple DNS lookup (available everywhere)
    basic: "nslookup example.com"
    specific_type: "nslookup -type=MX example.com"
    specific_server: "nslookup example.com 8.8.8.8"

  host:
    description: Simple DNS lookup (clean output)
    basic: "host example.com"
    specific_type: "host -t AAAA example.com"

  example_dig_output:
    command: "dig example.com A +short"
    output: "93.184.216.34"

    command_verbose: "dig example.com A"
    output_verbose: |
      ;; QUESTION SECTION:
      ;example.com.                   IN      A

      ;; ANSWER SECTION:
      example.com.            3600    IN      A       93.184.216.34

      ;; Query time: 23 msec
      ;; SERVER: 1.1.1.1#53(1.1.1.1)
```

## DNS in Microservices (Service Discovery)
```
service_discovery:
  description: Using DNS to find services in a microservice architecture

  internal_dns:
    description: Private DNS for services within infrastructure
    examples:
      - "user-service.internal -> 10.0.1.5"
      - "order-service.internal -> 10.0.2.8"
      - "redis.internal -> 10.0.3.2"

  kubernetes_dns:
    description: CoreDNS provides automatic DNS for all services
    format: "<service>.<namespace>.svc.cluster.local"
    examples:
      service: "user-service.default.svc.cluster.local -> ClusterIP"
      pod: "10-0-1-5.default.pod.cluster.local"
      headless: "Returns individual pod IPs instead of ClusterIP"
    resolution: |
      From same namespace: curl http://user-service:8080
      From other namespace: curl http://user-service.production.svc.cluster.local:8080

  consul_dns:
    description: HashiCorp Consul provides DNS-based service discovery
    format: "<service>.service.consul"
    example: "user-service.service.consul -> healthy instance IP"
    features:
      - Health-check aware (only returns healthy instances)
      - Supports SRV records (includes port)
      - Multi-datacenter

  dns_based_load_balancing:
    round_robin:
      description: Multiple A records for same domain
      example: |
        api.example.com. IN A 10.0.1.1
        api.example.com. IN A 10.0.1.2
        api.example.com. IN A 10.0.1.3
      behavior: Resolver returns records in rotating order
      limitation: No health checking, uneven distribution

    weighted:
      description: Use DNS provider features for traffic distribution
      use_case: Gradual rollout (90% old, 10% new)

    geolocation:
      description: Return different IPs based on client location
      use_case: Route users to nearest data center
      providers: Cloudflare, Route 53, NS1

  dns_vs_service_mesh:
    dns:
      pros: Simple, universal, works with any language
      cons: No health checking, coarse load balancing, TTL caching delays
    service_mesh:
      pros: Health-aware routing, fine-grained load balancing, mTLS, retries
      cons: More complex, sidecar overhead
      examples: Istio, Linkerd, Consul Connect
```

## Code Examples

### DNS Lookup in Go
```go
package main

import (
	"context"
	"fmt"
	"log"
	"net"
	"time"
)

func main() {
	resolver := &net.Resolver{
		PreferGo: true,
		Dial: func(ctx context.Context, network, address string) (net.Conn, error) {
			// Use custom DNS server (e.g., Cloudflare)
			d := net.Dialer{Timeout: 5 * time.Second}
			return d.DialContext(ctx, "udp", "1.1.1.1:53")
		},
	}

	ctx := context.Background()

	// A record lookup
	ips, err := resolver.LookupHost(ctx, "example.com")
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println("A/AAAA records:")
	for _, ip := range ips {
		fmt.Printf("  %s\n", ip)
	}

	// MX record lookup
	mxRecords, err := resolver.LookupMX(ctx, "example.com")
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println("MX records:")
	for _, mx := range mxRecords {
		fmt.Printf("  %s (priority %d)\n", mx.Host, mx.Pref)
	}

	// TXT record lookup
	txtRecords, err := resolver.LookupTXT(ctx, "example.com")
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println("TXT records:")
	for _, txt := range txtRecords {
		fmt.Printf("  %s\n", txt)
	}

	// CNAME lookup
	cname, err := resolver.LookupCNAME(ctx, "www.example.com")
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("CNAME: %s\n", cname)

	// NS record lookup
	nsRecords, err := resolver.LookupNS(ctx, "example.com")
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println("NS records:")
	for _, ns := range nsRecords {
		fmt.Printf("  %s\n", ns.Host)
	}

	// Reverse DNS lookup
	names, err := resolver.LookupAddr(ctx, "93.184.216.34")
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println("Reverse DNS:")
	for _, name := range names {
		fmt.Printf("  %s\n", name)
	}

	// SRV record lookup (service discovery)
	_, srvRecords, err := resolver.LookupSRV(ctx, "http", "tcp", "example.com")
	if err != nil {
		fmt.Printf("SRV lookup: %v\n", err)
	} else {
		fmt.Println("SRV records:")
		for _, srv := range srvRecords {
			fmt.Printf("  %s:%d (priority=%d, weight=%d)\n",
				srv.Target, srv.Port, srv.Priority, srv.Weight)
		}
	}
}
```

### DNS Lookup in JavaScript (Node.js)
```javascript
const dns = require("dns");
const { Resolver } = dns;

// Create resolver with custom DNS server
const resolver = new Resolver();
resolver.setServers(["1.1.1.1", "8.8.8.8"]);

// A record lookup
dns.resolve4("example.com", (err, addresses) => {
  if (err) throw err;
  console.log("A records:", addresses);
  // [ '93.184.216.34' ]
});

// AAAA record lookup
dns.resolve6("example.com", (err, addresses) => {
  if (err) throw err;
  console.log("AAAA records:", addresses);
});

// MX record lookup
dns.resolveMx("example.com", (err, records) => {
  if (err) throw err;
  console.log("MX records:", records);
  // [ { exchange: 'mail.example.com', priority: 10 } ]
});

// TXT record lookup
dns.resolveTxt("example.com", (err, records) => {
  if (err) throw err;
  console.log("TXT records:", records);
});

// NS record lookup
dns.resolveNs("example.com", (err, records) => {
  if (err) throw err;
  console.log("NS records:", records);
});

// Reverse DNS lookup
dns.reverse("93.184.216.34", (err, hostnames) => {
  if (err) throw err;
  console.log("Reverse DNS:", hostnames);
});

// Using promises (dns.promises)
async function lookupAll(domain) {
  const { promises: dnsPromises } = require("dns");

  const [ipv4, mx, txt, ns] = await Promise.all([
    dnsPromises.resolve4(domain),
    dnsPromises.resolveMx(domain),
    dnsPromises.resolveTxt(domain),
    dnsPromises.resolveNs(domain),
  ]);

  console.log(`DNS records for ${domain}:`);
  console.log("  IPv4:", ipv4);
  console.log("  MX:", mx);
  console.log("  TXT:", txt);
  console.log("  NS:", ns);
}

lookupAll("example.com");
```

### Simple DNS Health Checker in Go
```go
package main

import (
	"context"
	"fmt"
	"log"
	"net"
	"time"
)

type ServiceCheck struct {
	Name   string
	Domain string
}

func checkDNS(ctx context.Context, service ServiceCheck) {
	start := time.Now()
	ips, err := net.DefaultResolver.LookupHost(ctx, service.Domain)
	duration := time.Since(start)

	if err != nil {
		fmt.Printf("[FAIL] %s (%s) - %v\n", service.Name, service.Domain, err)
		return
	}

	fmt.Printf("[OK]   %s (%s) -> %v (%s)\n",
		service.Name, service.Domain, ips, duration)
}

func main() {
	services := []ServiceCheck{
		{Name: "User Service", Domain: "user-service.internal"},
		{Name: "Order Service", Domain: "order-service.internal"},
		{Name: "Redis", Domain: "redis.internal"},
		{Name: "PostgreSQL", Domain: "postgres.internal"},
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	fmt.Println("DNS Health Check")
	fmt.Println("================")
	for _, svc := range services {
		checkDNS(ctx, svc)
	}

	// Periodic check
	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()

	for range ticker.C {
		fmt.Printf("\n--- Check at %s ---\n", time.Now().Format(time.RFC3339))
		for _, svc := range services {
			checkDNS(ctx, svc)
		}
	}
}
```
