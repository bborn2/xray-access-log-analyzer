import json
import os
import re
from loguru import logger
from collections import defaultdict, Counter
import dns.resolver
import dns.reversename

import utils


logger.add("log", rotation="10 MB")  

def analyze () :
    user_targets = defaultdict(list)
    
   
    # user_phone =  {"default" : ["0"  , "1"]}
 
    line_str  =  " "
     
    count = 0
    
    output = "./output/"
    path_log = "./access.log"
    
    ignore_urls = ["1.1.1.1"  , "mtalk.google.com" , "android.apis.google.com" , "dns.google" , "8.8.8.8" , "gstatic" , "10.10." , "1.0.0.1" , "8.8.4.4" , "cloudflare"]
 
    #  user dir check :
    if not os.path.exists(output):
        os.makedirs(output)
        logger.info(f"Directory '{dir}' created.")
    else:
        logger.info(f"Directory '{dir}' already exists.")

    with open (path_log , "r") as file :
        for line in file :
            count += 1
            
            # if count == 10000:
            #     break
            
            pattern = r"email: (\S+)"
            #if user in line :
            if re.findall(pattern, line):
                skip = False
                for url in ignore_urls:
                    if url in line:
                        skip = True
                        break
                
                if skip:
                    continue

                parts = line.split()
               
                if parts[2] == "DNS" : 
                    continue
                
                
                ip_port = parts[3]
    
                # 有些行开头多了 tcp:，先去掉 tcp: 前缀
                if ip_port.startswith("tcp:") or ip_port.startswith("udp:"):
                    ip_port = ip_port.split(":", 1)[1]
                    
                dest = parts[5]
                if dest.startswith("tcp:") or dest.startswith("udp:"):
                    dest = dest[4:]
                  
                                
                user_targets[ip_port].append(dest)
                

                #porn detection :
                pattern_porn = r"\b\w*\s*(porn|xnxx|xvideos|sex|brazzer|xxx|erotica|hardcore|BDSM|fetish|Nude|NSFW|PNP|CYOC|OnlyFans|camgirl|webcam)\s*\w*\b"
                # if re.findall(pattern_porn, line_str):
                #     with open (f"{path}porn_detection.txt" , "a" , encoding="utf-8") as file : 
                #         file.writelines(line_str)
                #     if user not in p_user :
                #         p_user.append(user)
                    
                # phone detection : 
                pattern = r"\b\w*\s*(xiaomi|samsung|dbankcloud)\s*\w*\b"
                matches = re.findall(pattern, line_str)
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
 
 
            
            logger.info(count)
            
    get_global_top_target(user_targets)
            


def get_global_top_target(user_targets):
    N = 100
    all_targets = []
    for targets in user_targets.values():
        all_targets.extend(targets)

    global_top = Counter(all_targets).most_common(N)
    logger.info(f"\n🌐 全部用户访问量最多的前 {N} 个目标：")
    for target, count in global_top:
        domain = utils.reverse_dns_lookup(target)
        
        logger.info(f"{target} -> {count} 次, {domain}")    

    
import socket
if __name__ == "__main__":
    analyze()
    
    ips = ["149.154.167.41"]

    for ip in ips:
        try:
            domain = socket.gethostbyaddr(ip)
            print(f"{ip} -> {domain[0]}")
        except socket.herror:
            print(f"{ip} -> 无法解析")
