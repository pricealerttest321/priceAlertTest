from flask import Flask, render_template, request
from price_scraper import check_price  # reuse your existing logi

import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    print("✅ Request received")
    result = None
    error = None

    if request.method == "POST":
        url = request.form.get("product_url", "").strip()
        mode = request.form.get("mode", "amazon")

        if not url:
            error = "Please enter a product URL."
        else:
            try:
                # Default mode: 'amazon' (but could use 'test' or 'github' too)
                result = check_price(url, mode)
                if result is None:
                    error = "Unable to fetch or parse the product information."
            except Exception as e:
                error = f"Error: {e}"

    return render_template("index.html", result=result, error=error)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
