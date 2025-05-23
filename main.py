import re
from collections import Counter
import csv
import json

# Load config
with open("config.json", "r") as config_file:
    config = json.load(config_file)

ip_counter = Counter()
user_counter = Counter()
failed_attempts = []
pair_counter = Counter()

# Read and parse log file
with open(config["log_file"], "r") as file:
    for line in file:
        if any(keyword in line for keyword in config["filter_keywords"]):
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

# Generate TXT report
with open(config["output_txt_report"], "w") as report:
    report.write("=== Failed Login Summary Report ===\n\n")
    report.write("Top IPs by failed login attempts:\n")
    for ip, count in ip_counter.most_common(config["top_n_results"]):
        report.write(f"{ip}: {count} attempts\n")
    report.write("\nTop usernames by failed login attempts:\n")
    for user, count in user_counter.most_common(config["top_n_results"]):
        report.write(f"{user}: {count} attempts\n")
    report.write("\nTotal unique IPs: " + str(len(ip_counter)) + "\n")
    report.write("Total unique usernames: " + str(len(user_counter)) + "\n")

# Write username summary to CSV
with open(config["output_user_csv"], "w", newline="") as user_csv:
    writer = csv.writer(user_csv)
    writer.writerow(["username", "failed_attempts"])
    for user, count in user_counter.most_common():
        writer.writerow([user, count])

# Write IP summary to CSV
with open(config["output_ip_csv"], "w", newline="") as ip_csv:
    writer = csv.writer(ip_csv)
    writer.writerow(["ip_address", "failed_attempts"])
    for ip, count in ip_counter.most_common():
        writer.writerow([ip, count])

# Write combined user/IP attempt data to CSV
with open(config["output_combined_csv"], "w", newline="") as combo_csv:
    writer = csv.writer(combo_csv)
    writer.writerow(["username", "ip_address", "attempt_count"])
    for (user, ip), count in pair_counter.items():
        writer.writerow([user, ip, count])

top_n_display = 20  # Max user/IP pairs to show before collapsing

with open(config["output_html"], "w") as html:
    html.write("<html><head><title>Failed Login Report</title></head><body>")
    html.write("<h1>Failed Login Summary</h1>")

    html.write("<h2>Top IP Addresses</h2><ul>")
    for ip, count in ip_counter.most_common(config["top_n_results"]):
        html.write(f"<li>{ip} — {count} attempts</li>")
    html.write("</ul>")

    html.write("<h2>Top Usernames</h2><ul>")
    for user, count in user_counter.most_common(config["top_n_results"]):
        html.write(f"<li>{user} — {count} attempts</li>")
    html.write("</ul>")

    html.write("<h2>Top User/IP Pairs</h2>")
    html.write("<table border='1'><tr><th>Username</th><th>IP Address</th><th>Attempts</th></tr>")
    for (user, ip), count in pair_counter.most_common(top_n_display):
        html.write(f"<tr><td>{user}</td><td>{ip}</td><td>{count}</td></tr>")
    html.write("</table>")

    html.write("<details><summary><strong>View Full List of All User/IP Attempt Pairs</strong></summary>")
    html.write("<p>(Full list available in CSV: <code>" + config["output_combined_csv"] + "</code>)</p>")
    html.write("<table border='1'><tr><th>Username</th><th>IP Address</th><th>Attempts</th></tr>")
    for (user, ip), count in pair_counter.items():
        html.write(f"<tr><td>{user}</td><td>{ip}</td><td>{count}</td></tr>")
    html.write("</table></details>")

    html.write("</body></html>")