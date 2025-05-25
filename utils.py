from loguru import logger
import ipaddress
import geoip2.database
from geoip2.errors import AddressNotFoundError
import socket
import matplotlib.pyplot as plt
import re
import io

def is_ip_address(addr: str) -> bool:
    try:
        ipaddress.ip_address(addr)
        return addr
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

region_asn_cache = {}

def get_region_and_asn(ip):
    if ip == "Unknown IP":
        return "Unknown Country, Unknown Region, Unknown ASN"
    if ip in region_asn_cache:
        return region_asn_cache[ip]

    unknown_country = "Unknown Country"
    unknown_region = "Unknown Region"
    try:
        city_response = reader_city.city(ip)
        country = city_response.country.name or unknown_country
        region = city_response.subdivisions.most_specific.name or unknown_region
    except Exception:
        country, region = unknown_country, unknown_region

    unknown_asn = "Unknown ASN"
    try:
        asn_response = reader_asn.asn(ip)
        asn = f"AS{asn_response.autonomous_system_number} {asn_response.autonomous_system_organization}"
    except Exception:
        asn = unknown_asn

    result = f"{country}, {region}, {asn}"
    region_asn_cache[ip] = result
    return result


def draw(hourly_counts) -> io.BytesIO:

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
    # plt.savefig("access_per_hour.png", dpi=300)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return buf
     

def strip_port(host: str) -> str:
    # IPv6 带方括号：[::1]:443
    if host.startswith('['):
        match = re.match(r'^\[(.*)\](?::\d+)?$', host)
        if match:
            return match.group(1)

    # 如果 host 是合法的 IP（v4 或 v6），说明没有端口
    try:
        ipaddress.ip_address(host)
        return host
    except ValueError:
        pass

    # 如果是域名或IPv4带端口，如 google.com:443 / 1.2.3.4:443
    if ':' in host:
        parts = host.rsplit(':', 1)
        if parts[1].isdigit():
            return parts[0]

    return host

def format_top_target(data) -> str:
    lines = []
    for target, count, org in data:
        org_str = org if org and org != 'None' else 'Unknown'
        lines.append(f"{target:<40} {count:>5}    {org_str}")

    return "\n".join(lines)

def escape_markdown_v2(text: str) -> str:
    special_chars = r'_*[]()~`>#+-=|{}.!'
    for ch in special_chars:
        text = text.replace(ch, f'\\{ch}')
    return text

def format_top_user(data) -> str:
    header = f"{'IP':<17} {'Count':<6} {'Country':<10} {'City':<15} {'Org'}\n"
    lines = [header, "-" * 80]
    for ip, count, country, city, org in data:
        city = city if city else "-"
        lines.append(f"{ip:<17} {count:<6} {country:<10} {city:<15} {org}")
    return "\n".join(lines)