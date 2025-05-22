import dns.resolver
import dns.reversename
from loguru import logger
import ipaddress
import geoip2.database
from geoip2.errors import AddressNotFoundError

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
    

def get_ip_location(ip : str):
    reader = geoip2.database.Reader("GeoLite2-City.mmdb")

    realip = is_ip_address(ip)
    
    if realip is None:
        return None

    try:
        r = reader.city(realip)
        result = {
            "country": r.country.name,
            "city": r.city.name,
            "lat": r.location.latitude,
            "lon": r.location.longitude
        }
    except AddressNotFoundError:
        result = None
    finally:
        reader.close()

    return result

def get_ip_asn(ip : str):
    reader = geoip2.database.Reader('GeoLite2-ASN.mmdb')
 
    realip = is_ip_address(ip)
    
    if realip is None:
        return None

    ret = None
    try:
        response = reader.asn(realip)
        ret = {
            "ASN": response.autonomous_system_number,
            "Organization": response.autonomous_system_organization
        }
 
    except geoip2.errors.AddressNotFoundError:
        ret = None
    finally:
        reader.close()
        
    return ret