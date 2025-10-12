import requests
from bs4 import BeautifulSoup
import time
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# ==========================================================
# 1️⃣ DATA FETCHING - Get current product data by mode
# ==========================================================

def get_current_price(url, mode="amazon"):
    """
    Fetch product data from the specified source based on mode.
    Returns a dict: { 'name': str, 'price': float, 'in_stock': bool }
    """

    if mode == "amazon":
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.google.com/",
            "DNT": "1",  # Do Not Track header
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.find(id="productTitle").get_text(strip=True)

        price = None
        whole = soup.find("span", {"class": "a-price-whole"})
        fraction = soup.find("span", {"class": "a-price-fraction"})
        if whole:
            price_text = whole.get_text(strip=True)
            if fraction:
                price_text += fraction.get_text(strip=True)
            price = float(price_text.replace(",", ""))

        print(f"title: {title}")
        print(f"price: {price}")

        return {"name": title, "price": price, "in_stock": True}

    elif mode == "test":
        # Fetch JSON data (GitHub Pages)
        cache_buster = f"?_t={int(time.time())}"
        response = requests.get(url + cache_buster, timeout=10)
        response.raise_for_status()
        data = response.json()

        return {
            "name": data.get("product_name", "Unknown Product"),
            "price": float(data.get("current_price", 0)),
            "in_stock": data.get("in_stock", False),
        }

    else:
        raise ValueError(f"Unsupported mode: {mode}")


# ==========================================================
# 2️⃣ COMPARISON - Compare to previous price and update
# ==========================================================

def check_price(url, mode="amazon", cache_file="last_prices.json"):
    """
    Compares current price to the last saved value.
    Prints change info, updates cache, returns current data.
    """

    current = get_current_price(url, mode)
    if not current:
        print("⚠️ Failed to fetch current product info.")
        return None

    # Load previous price data
    last_prices = {}
    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            try:
                last_prices = json.load(f)
            except json.JSONDecodeError:
                last_prices = {}

    last_price = last_prices.get(current["name"])
    changed = last_price is not None and last_price != current["price"]

    if changed:
        print(f"🔔 Price change detected for {current['name']}: {last_price} → {current['price']}")
        send_email_alert(current["name"], last_price, current["price"])
    else:
        print(f"✅ {current['name']} | ${current['price']:.2f} | {'In stock' if current['in_stock'] else 'Out of stock'}")

    # Update cache with the new price
    last_prices[current["name"]] = current["price"]
    with open(cache_file, "w") as f:
        json.dump(last_prices, f, indent=2)

    return current


# ==========================================================
# 3️⃣ ALERTS - Email notification setup
# ==========================================================

def send_email_alert(product_name, old_price, new_price):
    """
    Sends an email alert when a price changes.
    (You can configure your credentials here.)
    """
    sender_email = "youremail@gmail.com"
    app_password = "your-app-password"
    receiver_email = "youremail@gmail.com"

    subject = f"Price Alert: {product_name}"
    body = f"""
    The price for {product_name} has changed!
    Old Price: ${old_price}
    New Price: ${new_price}
    """

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.send_message(msg)
        print("📧 Email alert sent successfully.")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")


# ==========================================================
# 4️⃣ MAIN - Manual testing entry point
# ==========================================================

if __name__ == "__main__":
    # Example usage for testing
    print("🚀 Flask app starting up...")
    test_url = "https://pricealerttest321.github.io/priceAlertTest/sample_product_data.json"
    amazon_url = "https://www.amazon.com/ATHMILE-Sandals-Comfortable-Fashion-Available/dp/B0BXKVWK7M/?th=1&psc=1"
    check_price(amazon_url, mode="amazon")
