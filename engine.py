# engine.py
import pandas as pd
import json
from math import sqrt
from collections import defaultdict

def conjunctive_search(processed_query, voc_df, inverted_index, df):
    """
    Args:
        processed_query (list): A list of pre-processed query terms.
        voc_df (DataFrame): A DataFrame containing vocabulary terms and their IDs.
        inverted_index (dict): An inverted index mapping term IDs to document IDs.
        df (DataFrame): A DataFrame containing the documents.

    Returns:
        DataFrame: A DataFrame containing the documents that match the query, 
                   or an empty DataFrame if no matches are found.
    """
    # Initialize an empty dictionary to store term IDs
    term_ids = {} 
    # Iterate over each word in the processed query
    for word in processed_query:
      # If the word exists in the vocabulary DataFrame
      if word in voc_df['term'].values:
           # Get the corresponding term ID from the vocabulary DataFrame
          term_ids[word] = voc_df[voc_df['term'] == word]['term_id'].values[0]

    # Initialize an empty list to store lists of document IDs
    lists = []
    # Iterate over each term and its ID in the term_ids dictionary
    for term, term_id in term_ids.items():
      if term_id is not None:
        # Get the list of document IDs from the inverted index for the current term ID
        result_doc_ids = inverted_index.get(str(term_id), [])
        lists.append(result_doc_ids)

    # Initialize an empty list to store the common document IDs
    common_numbers_list = [] 
    # If the lists list is not empty
    if lists:
      # Convert the first list of document IDs to a set
      common_numbers = set(lists[0])
      # Iterate over the remaining lists of document IDs
      for other_list in lists[1:]:
        # Update the common_numbers set with the intersection of itself and the current list
        common_numbers.intersection_update(other_list)
      
      # Convert the common_numbers set back to a list
      common_numbers_list = list(common_numbers)
      # Sort the common_numbers_list
      common_numbers_list.sort()
      # Print the common document IDs
      print("Common numbers:", common_numbers_list)

    # Handle empty results:
    if not common_numbers_list:
      print("No documents found matching the query.")
      return df.iloc[[]]  # Return an empty DataFrame

    return df.iloc[common_numbers_list]

def ranked_search(processed_query, inverted_index_tfidf, df, k=10):
    """
    Args:
        processed_query: A list of preprocessed query terms.
        inverted_index_tfidf: The inverted index with TF-IDF scores.
        df: The DataFrame containing the restaurant data.
        k: The number of top results to return.

    Returns:
        A list of dictionaries, each representing a restaurant,
        ranked by relevance to the query.
    """

    query_vector = {}
    for word in processed_query:
        if word in inverted_index_tfidf:
            for doc_id, tfidf in inverted_index_tfidf[word]:
                query_vector[doc_id] = query_vector.get(doc_id, 0) + tfidf

    doc_vectors = []
    for i in range(len(df)):
        doc_vector = {}
        for word in df['description_cleaned'][i].split():
            if word in inverted_index_tfidf:
                for doc_id, tfidf in inverted_index_tfidf[word]:
                    if doc_id == i:
                        doc_vector[doc_id] = doc_vector.get(doc_id, 0) + tfidf
        doc_vectors.append(doc_vector)

    similarities = []
    for doc_vector in doc_vectors:
        dot_product = sum(query_vector.get(key, 0) * doc_vector.get(key, 0) for key in set(query_vector) | set(doc_vector))
        query_magnitude = sqrt(sum(value ** 2 for value in query_vector.values()))
        doc_magnitude = sqrt(sum(value ** 2 for value in doc_vector.values()))
        if query_magnitude == 0 or doc_magnitude == 0:
            similarity = 0
        else:
            similarity = dot_product / (query_magnitude * doc_magnitude)
        similarities.append(similarity)

    top_indices = sorted(range(len(similarities)), key=lambda i: similarities[i], reverse=True)[:k]

    results = []
    for i in top_indices:
        result = df.iloc[i].to_dict()
        result['similarity'] = similarities[i]
        results.append(result)

    return results

def calculate_similarity(document, query, inverted_index_tfidf):
    """
    Args:
        document (str): The document to compare with the query.
        query (list of str): The preprocessed search query.
        inverted_index_tfidf (dict): The inverted index with TF-IDF weights.

    Returns:
        float: The cosine similarity between the document and the query.
    """

    document_vector = defaultdict(lambda: 0)  # Initialize a dictionary to store document term weights
    for term in document.split():  # Iterate over each term in the document
        if term in inverted_index_tfidf:  # Check if the term is in the inverted index
            for doc_id, tfidf in inverted_index_tfidf[term]:  # Get the TF-IDF weight for the term
                document_vector[term] = tfidf  # Store the TF-IDF weight in the document vector

    query_vector = defaultdict(lambda: 0)  # Initialize a dictionary to store query term weights
    for term in query:  # Iterate over each term in the query
        if term in inverted_index_tfidf:  # Check if the term is in the inverted index
            for doc_id, tfidf in inverted_index_tfidf[term]:  # Get the TF-IDF weight for the term
                query_vector[term] = tfidf  # Store the TF-IDF weight in the query vector

    # Calculate the dot product of the document and query vectors
    dot_product = sum(document_vector[term] * query_vector[term] for term in set(document_vector) & set(query_vector))  

    # Calculate the magnitudes of the document and query vectors
    doc_magnitude = sqrt(sum(value ** 2 for value in document_vector.values()))  
    query_magnitude = sqrt(sum(value ** 2 for value in query_vector.values())) 

    # If either magnitude is 0, return 0 (to avoid division by zero)
    if doc_magnitude == 0 or query_magnitude == 0:  
        return 0

    # Calculate and return the cosine similarity
    return dot_product / (doc_magnitude * query_magnitude) 

def calculate_score(restaurant, query, similarity):
    """
    Args:
        restaurant (dict): The dictionary containing the restaurant information.
        query (list of str): The preprocessed search query.
        similarity (float): The similarity score between the query and the restaurant description.

    Returns:
        float: The calculated new score.
    """
    
    # Weights for the different attributes
    weights = {
        'description_match': 0.2,
        'cuisine_match': 0.3,
        'facilities_and_services': 0.3,
        'price_range': 0.2
    }

    score = 0

    # Description Match
    score += weights['description_match'] * similarity

    # Cuisine Match
    cuisine_score = 0
    restaurant_cuisines = restaurant['cuisineType'].lower().split(',')  # Split cuisines into a list
    for cuisine in restaurant_cuisines:
        cuisine = cuisine.strip()  # Remove leading/trailing whitespace
        for q in query:
            if q in cuisine:
                cuisine_score += 1  # Increment score for each query word present in the cuisine

    score += weights['cuisine_match'] * cuisine_score

    # Facilities and Services
    facilities_score = 0
    if restaurant['facilitiesServices']:
        facilities = restaurant['facilitiesServices'].lower()
        for q in query:
            if q in facilities:
                facilities_score += 1  # Increment score for each query word present in facilities

    score += weights['facilities_and_services'] * facilities_score

    # Price Range
    price_score = 0
    if restaurant['priceRange']:
        price_range = restaurant['priceRange'].count('€')  # Count the number of € symbols
        # Assign a score based on the number of € symbols
        price_score = 1 - (price_range / 4)  # Lower price = higher score
    score += weights['price_range'] * price_score

    return score