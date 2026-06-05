def classify(user_percentile, cutoff):

    diff = user_percentile - cutoff

    if diff >= 2:
        return "Safe"

    elif diff >= -1:
        return "Moderate"

    else:
        return "Dream"