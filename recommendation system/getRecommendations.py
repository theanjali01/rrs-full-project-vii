# coding: utf-8

import pickle
import json


def load_obj(name):
    try:
        with open(name + '.pkl', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        print(f"Error: {name}.pkl file not found!")
        return None


def loadDataset(reviews, restaurants):
    if not reviews or not restaurants:
        print("Error: Reviews or restaurants data is missing!")
        return {}

    restaurant = {}
    for data in restaurants:
        res_id = data['business_id']
        name = data['name']
        restaurant[res_id] = name

    prefs = {}
    for data in reviews:
        user_id = data['user_id']
        res_id = data['restaurant_id']
        rating = data['rating']
        prefs.setdefault(user_id, {})
        prefs[user_id][restaurant[res_id]] = float(rating)

    print(f"Loaded preferences for {len(prefs)} users")
    return prefs


from math import sqrt


def sim_pearson(prefs, p1, p2):
    si = {}
    for item in prefs[p1]:
        if item in prefs[p2]:
            si[item] = 1

    n = len(si)
    if n == 0:
        return 0

    sum1 = sum([prefs[p1][it] for it in si])
    sum2 = sum([prefs[p2][it] for it in si])
    sum1Sq = sum([pow(prefs[p1][it], 2) for it in si])
    sum2Sq = sum([pow(prefs[p2][it], 2) for it in si])
    pSum = sum([prefs[p1][it] * prefs[p2][it] for it in si])

    num = pSum - (sum1 * sum2 / n)
    den = sqrt((sum1Sq - pow(sum1, 2) / n) * (sum2Sq - pow(sum2, 2) / n))

    if den == 0:
        return 0

    return num / den


def getRecommendations(prefs, person, similarity=sim_pearson):
    totals = {}
    simSums = {}

    for other in prefs:
        if other == person:
            continue

        sim = similarity(prefs, person, other)

        if sim <= 0:
            continue

        for item in prefs[other]:
            if item not in prefs[person] or prefs[person][item] == 0:
                totals.setdefault(item, 0)
                totals[item] += prefs[other][item] * sim

                simSums.setdefault(item, 0)
                simSums[item] += sim

    rankings = [(total / simSums[item], item) for item, total in totals.items()]
    rankings.sort()
    rankings.reverse()

    return rankings


def main():
    # Load data
    reviews = load_obj('reviews')
    restaurants = load_obj('restaurants')

    if not reviews or not restaurants:
        print("Failed to load data. Check your pickle files.")
        return

    # Create preferences dataset
    prefs = loadDataset(reviews, restaurants)

    # Choose a specific user (you might want to modify this)
    user_id = 'rLtl8ZkDX5vH5nAx9C3q5Q'

    # Get recommendations
    rec = getRecommendations(prefs, user_id)

    print(f"\nTop 15 Recommendations for user {user_id}:")
    for i, (score, restaurant) in enumerate(rec[:15], 1):
        print(f"{i}. {restaurant} (Similarity Score: {score:.2f})")

    # Prepare recommendations for JSON
    recommendations = {
        'recommendations': [
            {'sim_score': i[0], 'id': i[1]} for i in rec
        ]
    }

    # Save to JSON
    with open('userrec.json', 'w') as userrec:
        json.dump(recommendations, userrec, indent=2)

    print(f"\nTotal recommendations: {len(rec)}")
    print("Recommendations saved to userrec.json")


if __name__ == "__main__":
    main()