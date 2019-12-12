import json
from flask import Flask, render_template
import pandas as pd
import numpy as np

app = Flask(__name__, 
            static_url_path='',
            static_folder='static',
            template_folder='template')

COL_CARE = ["loan_amnt", "loan_status", "zip_code", "annual_inc", "term", "int_rate",
            "grade", "purpose", "issue_d", "addr_state"]

def memoize(function):
  memo = {}
  def wrapper(*args):
    if args in memo:
      return memo[args]
    else:
      rv = function(*args)
      memo[args] = rv
      return rv
  return wrapper

def load_data():
    raw_data = pd.read_csv("loan.csv")
    data = raw_data[COL_CARE]
    
    return data

def process_stats():
    data = load_data()
    data = data.groupby(["issue_d"])[["loan_amnt"]].agg(np.sum).reset_index() 
    data = data.to_dict(orient="records")

    return data

def process_bytime():
    data = load_data()
    data = data.groupby(["issue_d", "addr_state"])[["loan_amnt"]].agg(np.sum).reset_index() 
    data = data.to_dict(orient="records")

    return data

def process_bygeo():
    data = load_data()
    data["addr_state"] = "US." + data["addr_state"]
    data = data.groupby(["addr_state", "zip_code"])[["loan_amnt", "annual_inc"]].agg(np.sum).reset_index() 
    data = data.to_dict(orient="records")

    return data

@memoize
def dataprocess(data_type):
    PROCESS_FUNC = {"bystats": process_stats,
                    "bytime": process_bytime,
                    "bygeo": process_bygeo}
    data = PROCESS_FUNC[data_type]()

    # data1, data2 = {data_type: {
    #     "state": data1,
    #     "county": data2,
    # }}

    return json.dumps(data, indent=2)
    

@app.route("/")
def index():
    jsonify_data = dataprocess("bystats")  
    return render_template("test.html", data=jsonify_data)

@app.route("/bytime")
def bytime():
    jsonify_data = dataprocess("bytime")  
    return render_template("index.html", data=jsonify_data)

@app.route("/bygeo")
def bygeo():
    jsonify_data = dataprocess("bygeo")  
    return render_template("index.html", data=jsonify_data)

if __name__ == "__main__":
    app.run(debug=True)
