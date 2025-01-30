import subprocess
import re
import json
import requests
import time
import os

# پیکربندی وب‌هوک و تنظیمات ایمیل
WEBHOOK_URL = "https://your-webhook-url.com/endpoint"
TARGET_IP = "8.8.8.8"  # آدرس مقصد برای بررسی شبکه
THRESHOLD_PACKET_LOSS = 10  # درصد از دست رفتن بسته
CHECK_INTERVAL = 300  # بررسی هر 5 دقیقه یکبار

def run_mtr(target_ip):
    """اجرای دستور mtr و بازگشت نتایج آن"""
    try:
        result = subprocess.run(['mtr', '--report', '--report-cycles', '1', target_ip], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running mtr: {e}")
        return None

def analyze_mtr_output(output):
    """تحلیل خروجی mtr و بررسی میزان از دست رفتن بسته‌ها"""
    packet_loss = None
    lines = output.splitlines()
    for line in lines:
        # استفاده از regex برای استخراج اطلاعات مربوط به packet loss
        match = re.search(r'(\d+)% packet loss', line)
        if match:
            packet_loss = int(match.group(1))
            break
    return packet_loss, output

def send_webhook_alert(message):
    """ارسال هشدار به وب‌هوک"""
    payload = {
        "text": message,
        "severity": "high"  # می‌توانید severity را بسته به نوع خطا تغییر دهید
    }
    headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(WEBHOOK_URL, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            print("Alert sent to webhook successfully!")
        else:
            print(f"Failed to send alert: {response.status_code} {response.text}")
    except Exception as e:
        print(f"Error sending alert: {e}")

def check_network_status():
    """بررسی وضعیت شبکه و ارسال هشدار در صورت بروز مشکل"""
    print(f"Running mtr on {TARGET_IP}...")
    mtr_output = run_mtr(TARGET_IP)
    
    if mtr_output:
        packet_loss, report = analyze_mtr_output(mtr_output)
        
        # اگر از دست رفتن بسته‌ها بیشتر از آستانه باشد
        if packet_loss is not None:
            if packet_loss >= THRESHOLD_PACKET_LOSS:
                message = f"High packet loss detected: {packet_loss}% on {TARGET_IP}. \n\nMTR Output:\n{report}"
                print(message)
                send_webhook_alert(message)
            else:
                print(f"Packet loss is within acceptable limits: {packet_loss}%")
        else:
            print("Unable to determine packet loss from mtr output.")

if __name__ == "__main__":
    while True:
        check_network_status()
        time.sleep(CHECK_INTERVAL)
