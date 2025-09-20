from flask import Flask, request, jsonify
import requests
import json

# --- Configuration ---
HALFBLOOD_URL = "https://halfblood.famapp.in/vpa/verifyExt"
RAZORPAY_IFSC_URL = "https://ifsc.razorpay.com/"
HEADERS = {
    'User-Agent': "A015 | Android 15 | Dalvik/2.1.0 | Tetris | 318D0D6589676E17F88CCE03A86C2591C8EBAFBA |  (Build -1) | 3DB5HIEMMG",
    'Accept': "application/json",
    'Content-Type': "application/json",
    'authorization': "Token eyJlbmMiOiJBMjU2Q0JDLUhTNTEyIiwiZXBrIjp7Imt0eSI6Ik9LUCIsImNydiI6Ilg0NDgiLCJ4IjoidHlSR1NIak1heW5SRFBGbGxLVDFIY3owWTZSRVFUUkM3WW1ueURpUGJFZzBlenIyeGRMTi03QmZ3MGExZDZabWVmT2NSMU5UVnUwIn0sImFsZyI6IkVDREgtRVMifQ..RCO9yZSnrEvVHywcR4Drww.p8zp6Vd-YkuDVH2MBwyBMJedMfrfwpWCN2yDc9K1JnNZ1Mkj6Wqy5ZMqdiEZW72Db_DoebWD-68B7wIFKySQAKI0wiHxBNfio3UtFAcUFG-R90P3r-YkTVBxdIO9LrqDaUHkes_Rdce5suLt8E51pW4kOPttBqPQEl0vaqSn2WTDyApu45wy6RZinOi7osFcLUX5fGKOIWnFR8lpEBN5l59vmaw6E3b_SZPbeyRZK0OMeGUZBQZIHxfM7C7z7I7qNd_XWkVvGxIPa7seF2qFqQ.iXJ-yqepcGrXu8R_7--IepHJlNyCcFjDqZXdA-Ts7ww"
}

app = Flask(__name__)

def fetch_and_chain(upi_id):
    # --- Step 1: Fetch data from FamPay API ---
    vpa_payload = {"upi_string": f"upi://pay?pa={upi_id}"}
    vpa_details = None
    ifsc_code = None
    
    try:
        response_vpa = requests.post(HALFBLOOD_URL, data=json.dumps(vpa_payload), headers=HEADERS, timeout=10)
        response_vpa.raise_for_status()
        vpa_info = response_vpa.json().get("data", {}).get("verify_vpa_resp", {})
        
        if not vpa_info:
            return {"error": "'verify_vpa_resp' object not found in FamPay response."}, 400

        vpa_details = {
            "name": vpa_info.get("name"),
            "vpa": vpa_info.get("vpa"),
            "ifsc": vpa_info.get("ifsc")
        }
        ifsc_code = vpa_details.get("ifsc")
    
    except requests.exceptions.RequestException as e:
        return {"error": f"FamPay API call failed: {str(e)}"}, 500

    # --- Step 2: Fetch raw bank details from Razorpay API ---
    final_output = {
        "vpa_details": vpa_details,
        "bank_details_raw": None
    }

    if ifsc_code:
        try:
            response_ifsc = requests.get(f"{RAZORPAY_IFSC_URL}{ifsc_code}", timeout=10)
            if response_ifsc.status_code == 200:
                final_output["bank_details_raw"] = response_ifsc.json()
            else:
                final_output["bank_details_raw"] = {"warning": f"Razorpay returned status {response_ifsc.status_code}"}
        
        except requests.exceptions.RequestException as e:
            final_output["bank_details_raw"] = {"warning": f"Error during Razorpay API call: {str(e)}"}

    return final_output, 200


@app.route("/api/upi", methods=["GET"])
def api_upi_lookup():
    upi_id = request.args.get("upi_id")
    if not upi_id:
        return jsonify({"error": "Missing required parameter: upi_id"}), 400

    result, status = fetch_and_chain(upi_id)
    return jsonify(result), status


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
