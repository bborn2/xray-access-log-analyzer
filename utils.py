import dns.resolver
import dns.reversename
from loguru import logger
import ipaddress
import geoip2.database
from geoip2.errors import AddressNotFoundError
import socket
import matplotlib.pyplot as plt

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
    
reader_city = geoip2.database.Reader("GeoLite2-City.mmdb")

def get_ip_location(ip : str): 

    realip = is_ip_address(ip)
    
    if realip is None:
        return None

    try:
        r = reader_city.city(realip)
        result = {
            "country": r.country.name,
            "city": r.city.name,
            "lat": r.location.latitude,
            "lon": r.location.longitude
        }
    except AddressNotFoundError:
        result = None
    # finally:
    #     reader.close()

    return result

reader_asn = geoip2.database.Reader('GeoLite2-ASN.mmdb')

def get_ip_asn(ip : str):
    realip = is_ip_address(ip)
    
    if realip is None:
        return None

    ret = None
    try:
        response = reader_asn.asn(realip)
        ret = {
            "ASN": response.autonomous_system_number,
            "Organization": response.autonomous_system_organization
        }
 
    except geoip2.errors.AddressNotFoundError:
        ret = None
    # finally:
    #     reader.close()
        
    return ret

def get_host_by_name(domain):
    try:
        ip = socket.gethostbyname(domain)
        return ip
    except Exception as e:
        return None
    
def get_domain_asn(domian : str):
    ip = get_host_by_name(domian.split(":")[0])
    
    if ip is None:
        return None
    
    return get_ip_asn(ip)

def draw(hourly_counts):

    sorted_hours = sorted(hourly_counts.items())

    # 提取X、Y
    x = [h for h, _ in sorted_hours]
    y = [count for _, count in sorted_hours]
     
    plt.rcParams['axes.unicode_minus'] = False    # 正确显示负号

    plt.figure(figsize=(12, 6))
    plt.plot(x, y, marker='o')
    plt.xticks(rotation=45)
    plt.xlabel("hours")
    plt.ylabel("visit count")
    plt.title("count per hour")
    plt.grid(True)
    plt.tight_layout()
    # plt.show()
    plt.savefig("access_per_hour.png", dpi=300)