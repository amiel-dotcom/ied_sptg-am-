# app.py
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # allow cross-origin requests for frontend access

# Sample job data (could be loaded from a database)
jobs = [
    {
        "id": 1,
        "title": "Software Engineer",
        "company": "GoTechno Inc.",
        "location": "Remote",
        "category": ["Technology", "Remote"],
        "description": "Help build and scale modern web apps using cutting-edge technologies.",
        "image": "./images/job1.jpg"
    },
    {
        "id": 2,
        "title": "UI/UX Designer",
        "company": "CreativeX",
        "location": "New York, NY",
        "category": ["Design", "Remote"],
        "description": "Design sleek, user-friendly interfaces for our mobile and web products.",
        "image": "./images/job2.jpg"
    },
    {
        "id": 3,
        "title": "Marketing Strategist",
        "company": "Growthly",
        "location": "San Francisco, CA",
        "category": ["Marketing"],
        "description": "Plan and execute creative marketing campaigns to boost brand awareness.",
        "image": "./images/job3.jpg"
    },
    {
        "id": 4,
        "title": "Finance Analyst",
        "company": "FinLogic",
        "location": "Remote",
        "category": ["Finance","Remote"],
        "description": "Analyze trends and provide financial insights to support business decisions.",
        "image": "./images/job4.jpg"
    },
    {
        "id": 5,
        "title": "Data Analyst",
        "company": "DataWiz",
        "location": "Chicago, IL",
        "category": ["Data"],
        "description": "Interpret complex data to help drive business decisions and strategy.",
        "image": "./images/job5.jpg"
    },
    {
        "id": 6,
        "title": "DevOps Engineer",
        "company": "CloudFlow",
        "location": "Seattle, WA",
        "category": ["Infastructure"],
        "description": "Automate deployments and manage cloud infrastructure efficiently.",
        "image": "./images/job6.jpg"
    }
]

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    category_filter = request.args.getlist('category')
    
    if category_filter:
        filtered_jobs = [job for job in jobs if any(cat in job['category'] for cat in category_filter)]
        return jsonify(filtered_jobs)
    
    return jsonify(jobs)

if __name__ == '__main__':
    app.run(debug=True)
