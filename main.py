import os
import re
import shutil
import sys
from collections import Counter, defaultdict
from datetime import datetime

from dotenv import load_dotenv
from loguru import logger

import bot
import config
import mail
import utils

load_dotenv()

logger.add("log", rotation="10 MB", retention=5)

def analyze (log_dir) :
    logger.info(f"log dir {log_dir}")

    user_targets = defaultdict(list)
    hourly_counts = defaultdict(int)

    log_pattern = re.compile(r'access-.+\.log')

    count = 0
    lognames = []

    for filename in os.listdir(log_dir):

        lognames.append(filename)

        if log_pattern.match(filename):
            filepath = os.path.join(log_dir, filename)

            logger.info(f"load {filename}")

            with open(filepath, 'r', errors='ignore') as f:
                for line in f :
                    count += 1

                    ret = parse_line(line)

                    if ret is None:
                        # logger.info(f"{line} - None")
                        continue

                    dt, fr, to = ret

                    hour_key = dt.strftime("%Y-%m-%d %H")
                    hourly_counts[hour_key] += 1

                    user_targets[fr].append(to)

    logger.debug(count)

    yesterday = datetime.today() - timedelta(days=1)

    date_str = yesterday.strftime("%Y-%m-%d")

    contents = date_str + "\n\n" + str(len(lognames)) + " logs\n\n" + "\n".join(lognames)

    bot.send_msg( contents )

    contents += f"\n==========\n\ntop target\n---------\n\n"
    toptarget = utils.format_top_target(get_top_target(user_targets))
    contents += toptarget

    bot.send_file(toptarget, f"top target - {date_str}.txt")

    contents += "\n==========\n\ntop user\n----------\n\n"
    topuser = utils.format_top_user(get_top_user(user_targets))
    contents += topuser

    bot.send_file(topuser, f"top user - {date_str}.txt")

    contents += "\n==========\n\ntop country\n---------\n\n"
    topcountry = get_top_user_country(user_targets)
    contents += topcountry

    bot.send_msg(topcountry)

    image_buffer = get_timeline_image(hourly_counts)

    logger.info("image buffer len = {}", len(image_buffer.getvalue()))

    bot.send_photo(image_buffer, f"chart-{date_str}.png")

    fr = os.getenv("MAIL_FROM")
    to = os.getenv("MAIL_TO")

    mail.send_email(fr=fr, to=to, subject=f"network stat: {date_str}", content=contents, image_buffer=image_buffer)


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


def get_top_target(user_targets) -> list:
    N = config.top_N_target
    all_targets = []
    for targets in user_targets.values():
        all_targets.extend(targets)

    global_top = Counter(all_targets).most_common(N)
    logger.info(f"\ntop {N} target：")

    data = []
    for target, count in global_top:

        asn = None
        if utils.is_ip_address(target):
            asn = utils.get_ip_asn(target)

        logger.info(f"{target} -> {count},  {asn }")

        data.append((target, count, asn.get('Organization') if asn else 'None' ))

    return data

def get_top_user(user_targets) -> list:
    ip_access_counts = {ip: len(sites) for ip, sites in user_targets.items()}
    top_n = config.top_N_user

    data = []

    for ip, count in sorted(ip_access_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]:

        loc = utils.get_ip_location(ip)
        asn = utils.get_ip_asn(ip)

        data.append((ip, count, loc.get('country') if asn else 'None',
                     loc.get('city') if asn else 'None', asn.get('Organization') if asn else 'None'))

        logger.info(f"{ip} -> {count}, {loc}, {asn}" )

    return data

def get_top_user_country(user_targets) -> str:
    country_counter = Counter()

    data = ""
    for ip in user_targets.keys():
        try:
            response = utils.get_ip_location(ip)
            country_name = response["country"] or "Unknown"
            country_counter[country_name] += 1
        except Exception as e:
            logger.error(f"IP: {ip}, err: {e}")
            country_counter["Unknown"] += 1

    top_n = 100
    total_count = 0

    for country, count in country_counter.most_common(top_n):
        data += f"{country}: {count} \n"
        total_count += count
        logger.info(f"{country}: {count}")

    data += f"---------\ntotal:{total_count}"

    return data

def get_timeline_image(hourly_counts):
    for hour, count in sorted(hourly_counts.items()):
        logger.info(f"{hour}:00 - {count}")

    return utils.draw(hourly_counts)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python main.py <log_directory>")
        sys.exit(1)

    log_dir = sys.argv[1]

    try:
        analyze(log_dir)
    except Exception as e:
        logger.error(f"err: {e}")

    logger.info("==========end=============")
