import dns.resolver
import dns.reversename
from loguru import logger
import ipaddress

def reverse_dns_lookup(ip):
    
    realip = is_ip_address(ip)
    if realip is None:
        # logger.error("{} is not ip", ip)
        return None
    
    try:
        rev_name = dns.reversename.from_address(realip)
        
        answer = dns.resolver.resolve(rev_name, "PTR")
        return str(answer[0])
    except Exception as e:
        return None
    
def is_ip_address(addr: str) -> bool:
    host = addr.split(":")[0]
    
    try:
        ipaddress.ip_address(host)
        return host
    except ValueError:
        return None