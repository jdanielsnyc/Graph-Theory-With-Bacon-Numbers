#!/usr/bin/env python3

import pickle
# NO ADDITIONAL IMPORTS ALLOWED!

# Note that part of your checkoff grade for this lab will be based on the
# style/clarity of your code.  As you are working through the lab, be on the
# lookout for things that would be made clearer by comments/docstrings, and for
# opportunities to rearrange aspects of your code to avoid repetition (for
# example, by introducing helper functions).


class Queue:

    def __init__(self, start=None):
        self.newest = -1
        self.oldest = 0
        self.items = {}
        if start is not None:
            self.add(start)

    def next(self):
        # FIFO
        next_item = self.items.get(self.oldest, None)
        del self.items[self.oldest]
        # Will fail if dictionary is empty (I could put an if statement here but it would slow things down)
        self.oldest += 1
        return next_item

    def add(self, val):
        self.newest += 1
        self.items[self.newest] = val

    def is_empty(self):
        return self.newest < self.oldest  # Probably slightly faster than len(self.items) == 0

    def get_items(self):
        return list(self.items.values())

    def print_items(self):
        print(list(self.items.values()))


def find_path(start, is_goal, get_children, return_all_paths=False):
    """Do BFS lol"""
    q = Queue()
    paths = {}  # Dictionary of paths to each index
    seen = set()  # Set of items we've already operated on
    if isinstance(start, list):
        # If we start off with a list of values
        for item in start:
            q.add(item)
            paths[item] = [item]
            seen.add(item)
    else:
        # If we start off with a single value
        q.add(start)
        paths[start] = [start]
        seen.add(start)

    #  T H E  S E A R C H  L O O P
    while not q.is_empty():
        this = q.next()
        if is_goal(this):
            # If we've found what we're looking for, return the path to that object
            return paths[this]
        children = get_children(this)  # Get children of our current item
        for child in children:
            if child not in seen:
                # If we haven't already operated on this child, add it to queue and calculate its path
                q.add(child)
                paths[child] = paths.get(this, []) + [child]
                seen.add(child)
    if return_all_paths:
        return paths
    return None


def transform_data(raw_data):
    actor_data = {}
    film_data = {}

    for pair in raw_data:
        # Retrieve or create data set of first actor
        a1_data = actor_data.get(pair[0], {"acted with": {pair[0]}, "acted in": set()})
        a1_data["acted with"] |= {pair[1]}  # Add second actor to the set of actors that the first has worked with
        a1_data["acted in"] |= {pair[2]}  # Add film to the set of films that the actor one has acted in
        actor_data[pair[0]] = a1_data  # Update data in main dataset

        # Retrieve or create data set of second actor
        a2_data = actor_data.get(pair[1], {"acted with": {pair[1]}, "acted in": set()})
        a2_data["acted with"] |= {pair[0]}  # Add first actor to the set of actors that the second has worked with
        a2_data["acted in"] |= {pair[2]}  # Add film to the set of films that the actor two has acted in
        actor_data[pair[1]] = a2_data  # Update data in main dataset

        # Retrieve or create data set of films, and add the two actors to the list of actors that acted in it
        film_data[pair[2]] = film_data.get(pair[2], set()) | {pair[0], pair[1]}

    if 4724 not in actor_data:
        # If Kevin Bacon doesn't exist in our dataset, the concept of bacon numbers doesn't really make sense
        # Why did I include this? Because test_actor_to_actor_path_07 decided to go ahead and exist
        return {
            "actor data": actor_data,
            "film data": film_data
        }

    bacon_number_sets = {}
    bacon_paths = find_path(4724, lambda x: False, lambda actor_id: actor_data[actor_id]["acted with"], True)
    for actor_id in bacon_paths:
        path = bacon_paths[actor_id]
        bacon_number = len(path) - 1
        # Either add this actor to the set of actors with this bacon number, or create such a set in bacon_data
        bacon_number_sets[bacon_number] = bacon_number_sets.get(bacon_number, set()) | {actor_id}

    return {
        "actor data": actor_data,
        "film data": film_data,
        "bacon number sets": bacon_number_sets,
        "bacon paths": bacon_paths
    }


def acted_together(data, actor_id_1, actor_id_2):
    if actor_id_1 not in data["actor data"]:
        return False
    return actor_id_2 in data["actor data"][actor_id_1]["acted with"]


def actors_with_bacon_number(data, n):
    return data["bacon number sets"].get(n, [])


def bacon_path(data, actor_id):
    return data["bacon paths"].get(actor_id)


def actor_to_actor_path(data, actor_id_1, actor_id_2):
    return find_path(
        actor_id_1,
        lambda actor_id: actor_id == actor_id_2,
        lambda actor_id: data["actor data"][actor_id]["acted with"]
    )


def actor_path(data, actor_id_1, goal_test_function):
    return find_path(
        actor_id_1,
        goal_test_function,
        lambda actor_id: data["actor data"][actor_id]["acted with"]
    )


def actor_to_actor_film_path(data, actor_id_1, actor_id_2):
    actor1_films = data["actor data"][actor_id_1]["acted in"]
    actor2_films = data["actor data"][actor_id_2]["acted in"]

    def get_next_films(film_id):
        actors = data["film data"][film_id]
        next_films = set()
        for actor in actors:
            next_films |= data["actor data"][actor]["acted in"]
        return next_films

    return find_path(
        list(actor1_films),
        lambda film_id: film_id in actor2_films,
        get_next_films
    )


def actors_connecting_films(data, film1, film2):
    actors_in_film1 = data["film data"][film1]
    actors_in_film2 = data["film data"][film2]
    return find_path(
        list(actors_in_film1),
        lambda actor_id: actor_id in actors_in_film2,
        lambda actor_id: data["actor data"][actor_id]["acted with"]
    )


if __name__ == '__main__':
    with open('resources/names.pickle', 'rb') as f:
        namesdb = pickle.load(f)
    names = list(namesdb.keys())
    IDs = list(namesdb.values())

    def name(ID):
        return names[IDs.index(ID)]

    def ID(name):
        return IDs[names.index(name)]

    print(namesdb)  # Q2.2.2
    print(name(19974))  # Q2.2.3

    with open('resources/large.pickle', 'rb') as f:
        large = pickle.load(f)

    with open('resources/movies.pickle', 'rb') as f:
        moviesdb = pickle.load(f)
    movie_names = list(moviesdb.keys())
    movie_ids = list(moviesdb.values())

    def movie_name(ID):
        return movie_names[movie_ids.index(ID)]

    def movie_ID(name):
        return movie_ids[movie_names.index(name)]

    largeTransform = transform_data(large)
    film_path = actor_to_actor_film_path(largeTransform, ID("Toi Svane Stepp"), ID("Iva Ilakovac"))
    print([movie_name(film_id) for film_id in film_path])  # Q7


