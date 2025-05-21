import json
import os
import re
from loguru import logger
from collections import defaultdict, Counter

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
                    
                dest = parts[6]
                
                user_targets[ip_port].append(parts[5])
                
                
                if user not in user_list :
                    user_list[user]  = 0
                if user not in user_list : 
                    with open (f"{path_user}{user}.txt"  , "w") as user_log :
                        user_log.writelines(line_str)
                else  :
                    with open (f"{path_user}{user}.txt"  , "a") as user_log :
                        user_log.writelines(line_str)
                user_list[user] = line[0] + " " +  line[1]
                
                #create url list request per user:
                if "[" in  line[4] :
                    url = line[4].split("[")[1].split("]")[0]
                else :
                    # print(line)
                    url = str(line[5].split(":")[1])
                #print(url)
                if user not in url_user_list : 
                    url_user_list.append(user)
                    with open (f"{path_user}{user}_url.txt"  , "w") as file :
                        file.writelines("default")

                else  :
                    with open (f"{path_user}{user}_url.txt"  , "r") as file :
                        with open (f"{path_user}{user}_url.txt"  , "a") as file_2 :
                            for line_url in file :
                                if url in line_url :
                                    flag  = True
                                else :
                                    flag = False
                            if flag == False:
                                file_2.writelines("\n")
                                file_2.writelines(url)

                
                #porn detection :
                pattern_porn = r"\b\w*\s*(porn|xnxx|xvideos|sex|brazzer|xxx|erotica|hardcore|BDSM|fetish|Nude|NSFW|PNP|CYOC|OnlyFans|camgirl|webcam)\s*\w*\b"
                if re.findall(pattern_porn, line_str):
                    with open (f"{path}porn_detection.txt" , "a" , encoding="utf-8") as file : 
                        file.writelines(line_str)
                    if user not in p_user :
                        p_user.append(user)
                    
                # phone detection : 
                pattern = r"\b\w*\s*(xiaomi|samsung|dbankcloud)\s*\w*\b"
                matches = re.findall(pattern, line_str)
                if matches :
                    if user not in user_phone:
                        user_phone[user] = ["0"]
                    for match in matches:
                        if match in ["xiaomi", "samsung"] and match not in user_phone[f"{user}"]:
                            user_phone[user].append(match)
                        if match == "dbankcloud" and "huawei" not in user_phone[f"{user}"]:
                            user_phone[user].append("huawei")
                
                apple_pattern = r"\b\w*\s*gsp\s*\w*\b"
                apple_pattern_2 = r"\b\w*\s*apple\s*\w*\b"
                if re.findall(apple_pattern, line_str):
                    if re.findall(apple_pattern_2 , line_str) :
                        if user not in user_phone :
                            user_phone[f"{user}"] = ["0"]
                        if "apple" not in user_phone[f"{user}"] :
                            user_phone[f"{user}"].append("apple")
                
                # specific inbound detector  :
                inbound_pattern = re.search(r"VMESS\s+\+\s+TCP", line_str, flags=re.IGNORECASE)
                if inbound_pattern:
                    if user not in inbound_user :
                        inbound_user.append(user)
                

                line_str = " "
            
            logger.info(count)
            
    file_path = f"{path}last_online_per_user.txt"
    json_data = json.dumps(user_list)
    p_data =  json.dumps(p_user)
    phone_data = json.dumps(user_phone)
    inbound_data = json.dumps(inbound_user)
    with open (file_path , "w") as file : 
        file.writelines(json_data)
    with open (f"{path}p_user.txt" , "w" , encoding="utf-8") as file :
        file.writelines(p_data)
    with open (f"{path}phone_user.txt" , "w" , encoding="utf-8") as file :
        file.writelines(phone_data)
    with open (f"{path}inbound_specific.txt" , "w" , encoding="utf-8") as file :
        file.writelines(inbound_data)

  
    
    

if __name__ == "__main__":
    analyze()