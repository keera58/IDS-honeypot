import os, time
from datetime import datetime
from datetime import date
import requests
import csv
import re
from bs4 import BeautifulSoup
import urllib.request
import socket
import urllib.request
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib

"""                 Sending Email                """

"""
This function will:

    1) call the getIP details function
    2) separate IP address from log file
    2) send the email with the alert and the IP details


"""

def alertmail():

    files = ["results.csv", "intruder_logs.txt"]

    email_id = ""
    password = ""
    

    subject = "ALERT! Someone is trying to hack you!!"

    fromaddr = email_id
    msg = MIMEMultipart()

    msg['From'] = fromaddr
    msg['To'] = toadr
    msg['Subject'] = subject

    body = '<html><body><h2>Caution!</h2>Someone is trying to break into your network. Their details along with the log files are attached with this email. <br>Please make sure you secure your network before your digital assets get compromised.<br>The intruder has been blocked for your network security. <br><br> Stay safe, netizen!</body></html>'

    part = MIMEText(body,"html")
    msg.attach(part)


    for filename in files:
        try:
            attachment = open(filename, 'rb')
            p = MIMEBase('application', 'octet-stream')
            p.set_payload((attachment).read())
            encoders.encode_base64(p)
            p.add_header('Content-Disposition', "attachment;filename = %s" % filename)
            msg.attach(p)
        except:
            print("Could not attach file",filename)


    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(fromaddr, password)
    text = msg.as_string()
    try:
        s.sendmail(fromaddr, toadr, text)
        s.quit()
        print("\nEmail sent via alert system")
    except:
        print("Invalid email address")



"""         Web Scraping        """
# getting geographic details

def getIP():
    fs = open("logs.txt","r")
    x = fs.readlines()
    fs.close()
    #ip_start = x[0].find(",",x[0].find(",")+1)+1
    #ip_end = x[0].find("]")
    ipaddr = set()
    r = "([0-9]{1,3}\.){3}[0-9]{1,3}"
    for i in x:
        try:
            y = re.search(r,i).group()
            ipaddr.add(y)
        except:
            continue

    return ipaddr 
 
def getGeo(ip):
    parameters = {"ip": ip}
    response = requests.post("https://www.ipaddress.my/", data = parameters)
    soup = BeautifulSoup(response.text, 'html.parser') 
    res = {"Hostname:":"","Domain Name:":"","ISP:":"","City:":"","Country:":"","Latitude:":"","Longitude:":"","ZIP Code:":"","Area Code:":""}
    for i in res:
        res[i] = soup.find("td", text=i).find_next_sibling("td",text=True)
        if res[i]!=None:
            res[i] = res[i].get_text()
    res["Domain Name:"] = soup.find("td", text="Domain Name:").find_next().findChild("a")
    if res["Domain Name:"]!=None:
        res["Domain Name:"] = res["Domain Name:"].get_text()
    r = []
    for i in res:
        r.append([i,res[i]])
    r.append(["IP Address:",ip])
    write_to_file(r,ip)
        
                
def write_to_file(r,ip):
    file = open('results.csv', 'w', encoding='utf-8', newline='')
    with file:
        write = csv.writer(file)
        write.writerows([[ip],[""]])
        write.writerows(r)
        write.writerows([[""], [""]])

def block_IP(ip):
    os.system("sudo iptables -A INPUT -s "+ip+" -j DROP")
    # to delete rule: os.system("sudo iptables -D INPUT -s "+ip+" -j DROP")
    
def get_logs():
    os.system("cat /home/cowrie/cowrie/var/log/cowrie/cowrie.log | grep 'New\ connection\| login\ attempt\| lost' > /home/pi/Documents/logs.txt")
    fs = open("logs.txt","r")
    x = fs.readlines()
    fs.close()
    x.reverse()
    return x

def latest_log(x):
    log = []
    for i in x:
        if i[:26] >= current_datetime:
            log.insert(0,i)               
    file = open("intruder_logs.txt","w")
    with file as f:
        f.writelines("%s\n" % place for place in log)
    file.close()

def take_action():
    latest_log(get_logs())
    
    ipaddr = getIP()
    for ip in ipaddr:
        block_IP(ip)
    
    print("\nClosing connection with hacker. Intrusion Prevented.")
    
    for ip in ipaddr:
        getGeo(ip)
    print("Resuts.csv file generated.")
    latest_log(get_logs())
    
    alertmail()

# starting the program that will check if the log file is modified or not

toadr = input("Enter the email ID for alert system: ")
print("Intrusion Detection System activated...")

moddate = os.stat("/home/cowrie/cowrie/var/log/cowrie/cowrie.log")[8]
newdate = moddate


while (newdate == moddate): # checking if the date of the log file is not changed
    newdate = os.stat("/home/cowrie/cowrie/var/log/cowrie/cowrie.log")[8]
    
else: # the log file is modified
    
    # creating sub-log file of only login attempts
    current_date = str(date.today())
    current_datetime = str(datetime.now()).replace(" ","T")
    
    x = get_logs()
    while (len(x)==0):
        x = get_logs() # in the case the log file is to be created for the first time
    else:
        print("\nHoneypot activated. Checking for intrusion...")
        while (x[0][:26] < current_datetime):
            x = get_logs()
        else:
            
            print("\nSuspicious activity detected!\nWaiting to collect more information...")
            time.sleep(10)                       
            take_action()
    
