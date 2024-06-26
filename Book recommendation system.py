import numpy as np
import pandas as pd
from scipy.sparse.linalg import svds

# Replace with your correct absolute paths
books_file = r"C:/Users/Hp/Downloads/Books.csv/Books.csv"
ratings_file = r"C:/Users/Hp/Desktop/Ratings.csv/Ratings.csv"
users_file = r"C:/Users/Hp/Desktop/Users.csv/Users.csv"


def main():
    try:
        # Read CSV file into a DataFrame
        books_df = pd.read_csv(books_file, low_memory=False)  # Adjust as needed
        print(books_df.head())  # Example: Print the first few rows of the DataFrame

        # Your data processing and recommendation logic here

    except FileNotFoundError:
        print(f"File not found at path: {books_file}")
    except Exception as e:
        print(f"Error occurred: {e}")

    # Perform data processing and recommendation logic
    books_df = pd.read_csv(books_file)
    ratings_df = pd.read_csv(ratings_file).sample(40000)
    user_df = pd.read_csv(users_file)

    # Merge ratings and user data
    user_rating_df = ratings_df.merge(user_df, on='User-ID')

    # Merge books and user ratings
    book_user_rating = books_df.merge(user_rating_df, on='ISBN')
    book_user_rating = book_user_rating[['ISBN', 'Book-Title', 'Book-Author', 'User-ID', 'Book-Rating']]
    book_user_rating.reset_index(drop=True, inplace=True)

    # Create a mapping for unique book IDs
    d = {}
    for i, j in enumerate(book_user_rating['ISBN'].unique()):
        d[j] = i
    book_user_rating['unique_id_book'] = book_user_rating['ISBN'].map(d)

    # Create pivot table for user-book ratings
    users_books_pivot_matrix_df = book_user_rating.pivot(index='User-ID', 
                                                        columns='unique_id_book', 
                                                        values='Book-Rating').fillna(0)

    # Convert pivot table to numpy array
    users_books_pivot_matrix = users_books_pivot_matrix_df.values

    # Perform matrix factorization
    NUMBER_OF_FACTORS_MF = 15
    U, sigma, Vt = svds(users_books_pivot_matrix, k=NUMBER_OF_FACTORS_MF)
    sigma = np.diag(sigma)

    # Predicted ratings
    all_user_predicted_ratings = np.dot(np.dot(U, sigma), Vt)

    def top_cosine_similarity(data, book_id, top_n=10):
        index = book_id 
        book_row = data[index, :]
        magnitude = np.sqrt(np.einsum('ij, ij -> i', data, data))
        similarity = np.dot(book_row, data.T) / (magnitude[index] * magnitude)
        sort_indexes = np.argsort(-similarity)
        return sort_indexes[:top_n]

    def similar_books(book_user_rating, book_id, top_indexes):
        recommendations = []
        for id in top_indexes:
            title = book_user_rating.loc[book_user_rating['unique_id_book'] == id, 'Book-Title'].iloc[0]
            recommendations.append(title)
        return recommendations

        def get_recommendations(book_title):
    # Find the book ID for the given title
            try:
                print(f"Searching for book with title: '{book_title}'")
                matching_books = book_user_rating[book_user_rating['Book-Title'].str.lower().str.contains(book_title.lower())]
            except Exception as e:
                print(f"An error occurred: {e}")
                return []
            
            if matching_books.empty:
                print(f"No books found containing '{book_title}' in the title.")
                return []
        
            if len(matching_books) > 1:
                print("Multiple matching books found. Please choose one:")
                for idx, title in enumerate(matching_books['Book-Title'].unique(), 1):
                    print(f"{idx}. {title}")
                choice = int(input("Enter the number of your choice: ")) - 1
                book_id = matching_books.iloc[choice]['unique_id_book']
                chosen_title = matching_books.iloc[choice]['Book-Title']
            else:
                book_id = matching_books['unique_id_book'].iloc[0]
                chosen_title = matching_books['Book-Title'].iloc[0]
        
            print(f"Found book ID {book_id} for title '{chosen_title}'")

        # Compute similarity based on SVD results
            k = 50
            sliced = Vt.T[:, :k]  # representative data
            top_n = 10
            top_indexes = top_cosine_similarity(sliced, book_id, top_n)
            recommendations = similar_books(book_user_rating, book_id, top_indexes)
            return recommendations

    # User interaction
    while True:
        book_title = input("Enter the title of a book to get recommendations (Type 'exit' to end): ")
        if book_title.lower() == 'exit':
            break
       
        recommendations = get_recommendations(book_title)
        if recommendations:
         print(f"\nRecommendations for '{book_title}':")
    
        for i, book in enumerate(recommendations, 1):
            print(f"{i}. {book}")

if __name__ == "__main__":
    main()

