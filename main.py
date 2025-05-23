import re
from collections import Counter
import csv 

ip_counter = Counter()
user_counter = Counter()
failed_attempts = []
pair_counter = Counter()

with open("enhanced_mock_auth_log.txt", "r") as file:
#with opens the file and ensures closure regardless of potential errors

    for line in file:
#loop that goes through each line executing the following
        if (
        "Failed password" in line
        or "Authentication failure" in line
        or "Invalid user attempt" in line
        or "Failed login" in line
        ):
            ip_match = re.search(r"\d{1,3}(?:\.\d{1,3}){3}", line)
            
            
            user_match = re.search(r"(?:invalid user|illegal user|user|for)\s+(\w+)", line)

            if ip_match and user_match:
                ip = ip_match.group()
                user = user_match.group(1)
                ip_counter[ip] += 1
                user_counter[user] += 1
                pair_counter[(user, ip)] += 1
                failed_attempts.append((user, ip))
                print(f"Failed login attempt by user: {user} from IP: {ip}")

            print("\nTop 5 IPs by failed login attempts:")
            for ip, count in ip_counter.most_common(5):
                    print(f"{ip}: {count} attempts")

            print("\nTop 5 usernames by failed login attempts:")
            for user, count in user_counter.most_common(5):
                    print(f"{user}: {count} attempts")
with open("failed_login_report.txt", "w") as report:
    report.write("=== Failed Login Summary Report ===\n\n")

    report.write("Top 5 IPs by failed login attempts:\n")
    for ip, count in ip_counter.most_common(5):
        report.write(f"{ip}: {count} attempts\n")

    report.write("\nTop 5 usernames by failed login attempts:\n")
    for user, count in user_counter.most_common(5):
        report.write(f"{user}: {count} attempts\n")

    report.write("\nTotal unique IPs: " + str(len(ip_counter)) + "\n")
    report.write("Total unique usernames: " + str(len(user_counter)) + "\n")

with open("failed_usernames.csv", "w", newline="") as user_csv:
    writer = csv.writer(user_csv)
    writer.writerow(["username", "failed_attempts"])
    for user, count in user_counter.most_common():
        writer.writerow([user, count])

with open("failed_ips.csv", "w", newline="") as ip_csv:
    writer = csv.writer(ip_csv)
    writer.writerow(["ip_address", "failed_attempts"])
    for ip, count in ip_counter.most_common():
        writer.writerow([ip, count])

with open("failed_attempts_combined.csv", "w", newline="") as combo_csv:
    writer = csv.writer(combo_csv)
    writer.writerow(["username", "ip_address", "attempt_count"])
    for (user, ip), count in pair_counter.items():
        writer.writerow([user, ip, count])

with open("failed_login_report.html", "w") as html:
    html.write("<html><head><title>Failed Login Report</title></head><body>")
    html.write("<h1>Failed Login Summary</h1>")
    html.write("<h2>Top 5 IP Addresses</h2><ul>")
    for ip, count in ip_counter.most_common(5):
        html.write(f"<li>{ip} — {count} attempts</li>")
    html.write("</ul>")
    html.write("<h2>Top 5 Usernames</h2><ul>")
    for user, count in user_counter.most_common(5):
        html.write(f"<li>{user} — {count} attempts</li>")
    html.write("</ul>")
    html.write("<h2>All User/IP Attempt Pairs</h2>")
    html.write("<table border='1'><tr><th>Username</th><th>IP Address</th><th>Attempts</th></tr>")
    for (user, ip), count in pair_counter.items():
        html.write(f"<tr><td>{user}</td><td>{ip}</td><td>{count}</td></tr>")
    html.write("</table>")
    html.write("</body></html>")