#!/home/alex/venv_alex/bin/python

import re
import subprocess as sub
import logging
from datetime import datetime
import smtplib
from smtplib import SMTPException
from email.mime.text import MIMEText
import os
import yaml

def send_mail(msg, timestamp, service, problem_IS):
    sender = 'alex944591@gmail.com'
    AP_PASS = os.environ.get('AP_PASS')
    msg = MIMEText(msg)
    msg['Subject'] = f'Problem with {service=}|{problem_IS=} as at {timestamp}'
    msg['From'] = sender
    for receiver in info_set[problem_IS]:
        msg['To'] = receiver
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as srv:
                srv.ehlo()
                srv.starttls()
                srv.login(sender, AP_PASS)
                srv.sendmail(sender, receiver, msg.as_string())
                srv.quit()
                logging.info(f"mail with subject {msg['Subject']} successfully sent to {receiver}")
        except  SMTPException as ERROR:
            logging.warning(f"Sending to {receiver} ended up with the ERROR: {ERROR}")

def check_web_serv(url):
    regex = re.compile(r'(?:Connecting to.+\.{3} (\w+))|(?:HTTP request.+?\.{3} (\w+))')
    result = sub.run(f'wget {url}'.split(), stderr=sub.PIPE, encoding='utf-8')
   #for line in result.stderr.split('\n'):
   #     match = regex.search(line)
   #     if match and match.group(1)=='connected':
   #         return True
    m = regex.findall(result.stderr)
    connect, _ = m[0]
    if connect == 'connected':
        _, http_code = m[-1]
        if http_code == '200':
            logging.info(f"{url}: TCP=OK/HTTP=200")
            return True
    return result.stderr


if __name__ == "__main__":
    with open('emails_services.yml') as f:
        info_set = yaml.safe_load(f)
    logging.basicConfig(filename='journal_chk_web.log', format='{asctime} {levelname} {message}', level=logging.INFO, style='{', datefmt= '%Y-%m-%d %H:%M')
    for url_iss in info_set['services']:
        url, IS = url_iss.split('|')
        cur_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result = check_web_serv(url)
        if result == True:
            logging.info(f"{url}|{IS} is REACHABLE")
        else:
            logging.error(f"{url}|{IS} is UNREACHABLE")
            send_mail(result, cur_time, url, IS)
