import json
import os
import re
from loguru import logger
from collections import defaultdict, Counter
from datetime import datetime
import config
import utils

logger.add("log", rotation="10 MB", retention=5)  

def analyze () :
    user_targets = defaultdict(list)
    hourly_counts = defaultdict(int)

    path_log = "./access.log"
     
    with open (path_log , "r") as file :
        for line in file :
            
            ret = parse_line(line)
            
            if ret is None:
                # logger.info(f"{line} - None")
                continue
            
            dt, fr, to = ret
            
            hour_key = dt.strftime("%Y-%m-%d %H")
            hourly_counts[hour_key] += 1

            user_targets[fr].append(to)
            

            #porn detection :
            pattern_porn = r"\b\w*\s*(porn|xnxx|xvideos|sex|brazzer|xxx|erotica|hardcore|BDSM|fetish|Nude|NSFW|PNP|CYOC|OnlyFans|camgirl|webcam)\s*\w*\b"
            # if re.findall(pattern_porn, line_str):
            #     with open (f"{path}porn_detection.txt" , "a" , encoding="utf-8") as file : 
            #         file.writelines(line_str)
            #     if user not in p_user :
            #         p_user.append(user)
                
            # phone detection : 
            pattern = r"\b\w*\s*(xiaomi|samsung|dbankcloud)\s*\w*\b"
            matches = re.findall(pattern, line)
            # if matches :
            #     if user not in user_phone:
            #         user_phone[user] = ["0"]
            #     for match in matches:
            #         if match in ["xiaomi", "samsung"] and match not in user_phone[f"{user}"]:
            #             user_phone[user].append(match)
            #         if match == "dbankcloud" and "huawei" not in user_phone[f"{user}"]:
            #             user_phone[user].append("huawei")
            
            apple_pattern = r"\b\w*\s*gsp\s*\w*\b"
            apple_pattern_2 = r"\b\w*\s*apple\s*\w*\b"
            # if re.findall(apple_pattern, line_str):
            #     if re.findall(apple_pattern_2 , line_str) :
            #         if user not in user_phone :
            #             user_phone[f"{user}"] = ["0"]
            #         if "apple" not in user_phone[f"{user}"] :
            #             user_phone[f"{user}"].append("apple")
            
            # specific inbound detector  :

    get_top_target(user_targets)
    get_top_user(user_targets)
    get_top_user_country(user_targets)
    
    for hour, count in sorted(hourly_counts.items()):
        logger.info(f"{hour}:00 - {count} 次访问")
        
    utils.draw(hourly_counts)

def parse_line(line : str):
    pattern = r"email: (\S+)"

    if re.findall(pattern, line):
        for url in config.ignore_urls:
            if url in line:
                return None

        parts = line.split()

        if parts[2] == "DNS":
            return None

        time_str = line[:19]
        dt = datetime.strptime(time_str, "%Y/%m/%d %H:%M:%S")
        
        ip_port = parts[3]
        
        if ip_port.startswith("tcp:") or ip_port.startswith("udp:"):
            ip_port = ip_port.split(":", 1)[1]
            
        dest = parts[5]
        if dest.startswith("tcp:") or dest.startswith("udp:"):
            dest = dest.split(":", 1)[1]

        return dt, utils.strip_port(ip_port), utils.strip_port(dest)
         
    else:
        return None


def get_top_target(user_targets):
    N = 100
    all_targets = []
    for targets in user_targets.values():
        all_targets.extend(targets)

    global_top = Counter(all_targets).most_common(N)
    logger.info(f"\n🌐 全部用户访问量最多的前 {N} 个目标：")
    for target, count in global_top:
        
        asn = None
        if utils.is_ip_address(target):
            asn = utils.get_ip_asn(target)
        
        logger.info(f"{target} -> {count} 次,  {asn }")    

def get_top_user(user_targets):
    ip_access_counts = {ip: len(sites) for ip, sites in user_targets.items()}
    top_n = 100
    for ip, count in sorted(ip_access_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]:
        
        loc = utils.get_ip_location(ip)
        asn = utils.get_ip_asn(ip)
        
        logger.info(f"{ip} -> {count} 次, {loc}, {asn}" )
        
def get_top_user_country(user_targets):
    country_counter = Counter()

    for ip in user_targets.keys():
        try:
            response = utils.get_ip_location(ip)
            country_name = response["country"] or "Unknown"
            country_counter[country_name] += 1
        except Exception as e:
            logger.error(f"IP 查询失败: {ip}, 错误: {e}")
            country_counter["Unknown"] += 1

    top_n = 100
    for country, count in country_counter.most_common(top_n):
        logger.info(f"{country}: {count} 个用户")

if __name__ == "__main__":
    analyze()

