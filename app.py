from flask import Flask, render_template, request, send_file
from sqlalchemy import or_

from database import Session, Cutoff, init_db
from predictor import classify

import pandas as pd

app = Flask(__name__)

# Create database tables
init_db()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():

    percentile = float(request.form["percentile"])
    category = request.form["category"]
    branch = request.form["branch"]
    city = request.form["city"]

    db = Session()

    query = db.query(Cutoff)

    # Category Filter
    if category != "All":
        query = query.filter(
            Cutoff.category.ilike(f"%{category}%")
        )

    # City Filter
    if city != "All":
        query = query.filter(
            Cutoff.city.ilike(f"%{city}%")
        )

    # Branch Filter
    if branch != "All":

        if branch == "Computer / IT":

            query = query.filter(
                or_(
                    Cutoff.branch_name.ilike("%computer%"),
                    Cutoff.branch_name.ilike("%computer science%"),
                    Cutoff.branch_name.ilike("%information technology%"),
                    Cutoff.branch_name.ilike("%artificial intelligence%"),
                    Cutoff.branch_name.ilike("%ai%"),
                    Cutoff.branch_name.ilike("%data science%"),
                    Cutoff.branch_name.ilike("%machine learning%"),
                    Cutoff.branch_name.ilike("%cyber%"),
                    Cutoff.branch_name.ilike("%software%"),
                    Cutoff.branch_name.ilike("%iot%"),
                    Cutoff.branch_name.ilike("%electronics and computer%")
                )
            )

        else:

            query = query.filter(
                Cutoff.branch_name.ilike(f"%{branch}%")
            )

    colleges = query.all()

    results = []

    for c in colleges:

        chance = classify(
            percentile,
            c.percentile
        )

        results.append({
            "college": c.college_name,
            "branch": c.branch_name,
            "city": c.city,
            "cutoff": round(c.percentile, 2),
            "chance": chance
        })

    # Separate by chance
    safe_results = [
        r for r in results
        if r["chance"] == "Safe"
    ]

    moderate_results = [
        r for r in results
        if r["chance"] == "Moderate"
    ]

    dream_results = [
        r for r in results
        if r["chance"] == "Dream"
    ]

    # Sort each group
    safe_results.sort(
        key=lambda x: x["cutoff"],
        reverse=True
    )

    moderate_results.sort(
        key=lambda x: x["cutoff"],
        reverse=True
    )

    dream_results.sort(
        key=lambda x: x["cutoff"],
        reverse=True
    )

    # Final order
    results = (
        safe_results +
        moderate_results +
        dream_results
    )

    # Stats
    safe_count = len(safe_results)
    moderate_count = len(moderate_results)
    dream_count = len(dream_results)

    # Limit results
    results = results[:300]

    # Save for Excel download
    app.config["LAST_RESULTS"] = results

    return render_template(
        "results.html",
        percentile=percentile,
        results=results,
        safe_count=safe_count,
        moderate_count=moderate_count,
        dream_count=dream_count
    )


import io

@app.route("/download")
def download():

    results = app.config.get("LAST_RESULTS", [])

    if not results:
        return "No results available. Please run prediction first."

    df = pd.DataFrame(results)

    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)

    output.seek(0)

    return send_file(
        output,
        download_name="college_report.xlsx",
        as_attachment=True,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )