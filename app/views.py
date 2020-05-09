# all API endpoint routes are defined here

from flask import Flask, request

@app.route('/search', methods=['GET'])
def search_with_keywords():
    """
    searches by text match MongoDB based on keywords

    Returns
    -------
    JSON
        {
            "url": [list of URLs for matched Zenodo artifacts]
        }
    """
    if "keywords" not in request.args:
        return 'keywords missing!', 400
    
    kwrds = request.args.get('keywords')
    if kwrds == "":
        docs = mongo.db.raw_artifacts.find({"tfidf_score": {"$gt": 13}}).limit(20)
    else:
        docs = mongo.db.raw_artifacts.find({"$text":{"$search": kwrds}, "tfidf_score": {"$gt": 13}})
    res = ["https://doi.org/" + doc["doi"] for doc in docs]
    return {"url": res}, 200
