# Import the modules
import wikipedia
import imdb
import random

# Create an IMDb object
ia = imdb.IMDb()

# Define a function to get the movie summary from Wikipedia


def get_summary(movie):
    # Try to get the summary from Wikipedia
    try:
        summary = wikipedia.summary(movie)
    # If the movie is not found, return None
    except wikipedia.exceptions.PageError:
        summary = None
    # Return the summary
    return summary

# Define a function to get the movie rating from IMDb


def get_rating(movie):
    # Try to get the movie rating from IMDb
    try:
        # Search for the movie on IMDb
        results = ia.search_movie(movie)
        # Get the first result
        result = results[0]
        # Get the movie ID
        movie_id = result.movieID
        # Get the movie object
        movie_obj = ia.get_movie(movie_id)
        # Get the movie rating
        rating = movie_obj["rating"]
    # If the movie is not found, return None
    except (IndexError, KeyError):
        rating = None
    # Return the rating
    return rating

# Define a function to get the movie genre from IMDb


def get_genre(movie):
    # Try to get the movie genre from IMDb
    try:
        # Search for the movie on IMDb
        results = ia.search_movie(movie)
        # Get the first result
        result = results[0]
        # Get the movie ID
        movie_id = result.movieID
        # Get the movie object
        movie_obj = ia.get_movie(movie_id)
        # Get the movie genre
        genre = movie_obj["genre"]
    # If the movie is not found, return None
    except (IndexError, KeyError):
        genre = None
    # Return the genre
    return genre

# Define a function to get a movie recommendation based on a genre


def get_recommendation(genre):
    # Try to get a movie recommendation based on a genre
    try:
        # Get the top 250 movies from IMDb
        top_movies = ia.get_top250_movies()
        # Filter the movies by the genre
        filtered_movies = [
            movie for movie in top_movies if genre in movie["genre"]]
        # Choose a random movie from the filtered movies
        recommendation = random.choice(filtered_movies)
    # If the genre is not found, return None
    except (IndexError, KeyError):
        recommendation = None
    # Return the recommendation
    return recommendation

# Define a function to create a chatbot that can answer questions about movies


def chatbot():
    # Print a welcome message
    print("Hello, I am a chatbot that can answer questions about movies.")
    # Loop until the user says bye
    while True:
        # Get the user input
        user_input = input("You: ")
        # Check if the user input is not empty
        if user_input:
            # Check if the user input is a question
            if user_input.endswith("?"):
                # Check if the user input is about a movie summary
                if "summary" in user_input.lower():
                    # Get the movie name from the user input
                    movie = user_input.split()[-1].replace("?", "")
                    # Get the movie summary from Wikipedia
                    summary = get_summary(movie)
                    # Check if the summary is not None
                    if summary:
                        # Print the summary
                        print(f"Chatbot: The summary of {movie} is: {summary}")
                    else:
                        # Print an error message
                        print(
                            f"Chatbot: Sorry, I could not find the summary of {movie}.")
                # Check if the user input is about a movie rating
                elif "rating" in user_input.lower():
                    # Get the movie name from the user input
                    movie = user_input.split()[-1].replace("?", "")
                    # Get the movie rating from IMDb
                    rating = get_rating(movie)
                    # Check if the rating is not None
                    if rating:
                        # Print the rating
                        print(f"Chatbot: The rating of {
                              movie} is: {rating}/10")
                    else:
                        # Print an error message
                        print(
                            f"Chatbot: Sorry, I could not find the rating of {movie}.")
                # Check if the user input is about a movie genre
                elif "genre" in user_input.lower():
                    # Get the movie name from the user input
                    movie = user_input.split()[-1].replace("?", "")
                    # Get the movie genre from IMDb
                    genre = get_genre(movie)
                    # Check if the genre is not None
                    if genre:
                        # Print the genre
                        print(f"Chatbot: The genre of {
                              movie} is: {', '.join(genre)}")
                    else:
                        # Print an error message
                        print(
                            f"Chatbot: Sorry, I could not find the genre of {movie}.")
                # Check if the user input is about a movie recommendation
                elif "recommendation" in user_input.lower():
                    # Get the genre name from the user input
                    genre = user_input.split()[-1].replace("?", "")
                    # Get the movie recommendation based on the genre
                    recommendation = get_recommendation(genre)
                    # Check if the recommendation is not None
                    if recommendation:
                        # Print the recommendation
                        print(f"Chatbot: A movie recommendation for {
                              genre} is: {recommendation}")
                    else:
                        # Print an error message
                        print(
                            f"Chatbot: Sorry, I could not find a movie recommendation for {genre}.")
                else:
                    # Invalid question
                    print("Chatbot: Sorry, I don't know how to answer that question. Please ask me about movie summaries, ratings, genres, or recommendations.")
            # Check if the user input is bye
            elif user_input.lower() == "bye":
                # Exit the chatbot
                print("Chatbot: Bye, have a nice day!")
                break
            else:
                # Invalid input
                print(
                    "Chatbot: Sorry, I don't understand you. Please ask me a question about movies.")
        else:
            # Empty input
            print("Chatbot: Please say something.")


# Run the chatbot function
chatbot()
