import requests

def check_odoo_online():
    url = "https://fareed.odoo.com"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"✅ Odoo is ONLINE at {url} (Status Code: 200)")
        else:
            print(f"⚠️ Odoo is REACHABLE but returned Status Code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Odoo is OFFLINE or Unreachable. Error: {e}")

if __name__ == "__main__":
    check_odoo_online()
