#!/usr/bin/env python3

import pickle
import random
# NO ADDITIONAL IMPORTS ALLOWED!

# Note that part of your checkoff grade for this lab will be based on the
# style/clarity of your code.  As you are working through the lab, be on the
# lookout for things that would be made clearer by comments/docstrings, and for
# opportunities to rearrange aspects of your code to avoid repetition (for
# example, by introducing helper functions).


def transform_data(raw_data):
    actorData = {}
    movieData = {}
    baconData = {}

    # Initialize Kevin Bacon Data
    KBID = 4724
    baconData[0] = {KBID}
    actorData[KBID] = actorData.get(KBID, actor(KBID))
    actorData[KBID].baconNum = 0
    actorData[KBID].baconPath = [KBID]

    for pair in raw_data:
        # Re-organize actor-movie relations data
        actor1ID = pair[0]
        actor2ID = pair[1]
        movieID = pair[2]

        actor1 = actorData.get(actor1ID, actor(actor1ID))  # Either get the existing actor object or create a new one
        actor1.addPair(actor1ID, movieID)
        actor1.addPair(actor2ID, movieID)

        actor2 = actorData.get(actor2ID, actor(actor2ID))  # Either get the existing actor object or create a new one
        actor2.addPair(actor1ID, movieID)
        actor2.addPair(actor2ID, movieID)

        movie = movieData.get(movieID, set())  # Either get the existing set or create a new one
        movie.update({actor1ID, actor2ID})

        actorData[actor1ID] = actor1
        actorData[actor2ID] = actor2
        movieData[movieID] = movie

    alreadySearched = set()  # Any actor contained in this set that turns up in our search results is removed
    searchBase = {4724}  # We search all actors who have acted with the those contained in this set
    baconNumber = 1
    while True:
        results = set()
        for base in searchBase:
            actedWith = actorData[base].actedWith.keys() - searchBase - alreadySearched
            # IDs of actors that base has acted with
            # We remove all actors that have previously been returned as search results or are search bases
            for ID in actedWith:
                # For each actor in our set of actors that base has worked with, update Bacon data
                thisActor = actorData[ID]  # Get actor object corresponding to ID
                thisActor.baconNum = baconNumber
                thisActor.baconPath = actorData[base].baconPath + [ID]
            results |= actedWith  # Add all actors that base has acted with to results
        if len(results) <= 0:
            break
        baconData[baconNumber] = results  # Create the set of actors with this Bacon Number and store it in baconData
        alreadySearched |= searchBase
        searchBase = results
        baconNumber += 1

    return(actorData, baconData, movieData)


class actor:
    def __init__(self, ID):
        self.ID = ID
        self.baconNum = None
        self.baconPath = []
        self.actedWith = {}  # actedWith[actor ID] = set of movie IDs
        self.actedIn = {}  # actedIn[movie ID] = set of actor IDs

    def addPair(self, actorID, movieID):
        # Adds an actor movie pair to the actor's database

        # Add to dictionary of actors worked with
        if actorID in self.actedWith:
            self.actedWith[actorID].add(movieID)
        else: self.actedWith[actorID] = {movieID}

        # Add to dictionary of movies acted in
        if movieID in self.actedIn:
            self.actedIn[movieID].add(actorID)
        else: self.actedIn[movieID] = {actorID}

    def hasActedWith(self, actorID):
        return actorID in self.actedWith

    def hasActedIn(self, movieID):
        return movieID in self.actedIn


def acted_together(data, actor_id_1, actor_id_2):
    actors = data[0]
    return actor_id_2 in actors[actor_id_1].actedWith


def actors_with_bacon_number(data, n):
    baconNumberLists = data[1]
    return baconNumberLists.get(n, set())


def bacon_path(data, actor_id):
    actor = data[0].get(actor_id, 0)
    if actor == 0:
        return None
    path = actor.baconPath
    if not path:
        return None
    return actor.baconPath


def actor_to_actor_path(data, actor_id_1, actor_id_2):
    pathTo = {actor_id_1: [actor_id_1]}  # paths[ending actor] = [list of actors starting at actor_id_1]
    actorData = data[0]

    alreadySearched = set()  # Any actor contained in this set that turns up in our search results is removed
    searchBase = {actor_id_1}  # We search all actors who have acted with the those contained in this set
    while True:
        results = set()
        for base in searchBase:
            actedWith = actorData[base].actedWith.keys() - searchBase - alreadySearched
            # IDs of actors that base has acted with
            # We remove all actors that have previously been returned as search results or are search bases
            for ID in actedWith:
                # For each actor in our set of actors that base has worked with, update Bacon data
                pathTo[ID] = pathTo.get(base, []) + [ID]
                if ID == actor_id_2:
                    return pathTo[ID]
            results |= actedWith  # Add all actors that base has acted with to results
        if len(results) <= 0:
            return None
        alreadySearched |= searchBase
        searchBase = results


def movie_actor_to_actor_path(data, actor_id_1, actor_id_2):
    raise NotImplementedError("Implement me!")

def actor_path(data, actor_id_1, goal_test_function):
    pathTo = {actor_id_1: [actor_id_1]}  # paths[ending actor] = [list of actors starting at actor_id_1]
    actorData = data[0]

    alreadySearched = set()  # Any actor contained in this set that turns up in our search results is removed
    searchBase = {actor_id_1}  # We search all actors who have acted with the those contained in this set
    while True:
        results = set()
        for ID in searchBase:
            if goal_test_function(ID):
                return pathTo[ID]
        for base in searchBase:
            actedWith = actorData[base].actedWith.keys() - searchBase - alreadySearched
            # IDs of actors that base has acted with
            # We remove all actors that have previously been returned as search results or are search bases
            for ID in actedWith:
                # For each actor in our set of actors that base has worked with, update Bacon data
                pathTo[ID] = pathTo.get(base, []) + [ID]
            results |= actedWith  # Add all actors that base has acted with to results
        if len(results) <= 0:
            return None
        alreadySearched |= searchBase
        searchBase = results


def actors_connecting_films(data, film1, film2):
    pathTo = {}  # paths[ending actor] = [list of actors starting at actor_id_1]
    actorData = data[0]
    film1Actors = data[2][film1]
    for actor in film1Actors:
        pathTo[actor] = [actor]

    alreadySearched = set()  # Any actor contained in this set that turns up in our search results is removed
    searchBase = film1Actors  # We search all actors who have acted with the those contained in this set
    while True:
        results = set()
        for ID in searchBase:
            if actorData[ID].hasActedIn(film2):
                return pathTo[ID]
        for base in searchBase:
            actedWith = actorData[base].actedWith.keys() - searchBase - alreadySearched
            # IDs of actors that base has acted with
            # We remove all actors that have previously been returned as search results or are search bases
            for ID in actedWith:
                # For each actor in our set of actors that base has worked with, update Bacon data
                pathTo[ID] = pathTo.get(base, []) + [ID]
            results |= actedWith  # Add all actors that base has acted with to results
        if len(results) <= 0:
            return None
        alreadySearched |= searchBase
        searchBase = results


def getPath(data, startingActors, endingActors):
    raise NotImplementedError("Implement me!")


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
    #print(name(19974))  # Q2.2.3

    print(ID("Blaze Kelly Coyle"))
    print(ID("Robert Maximilliano"))
    print(ID("Peter Brouwer"))
    print(ID("Toi Svane Stepp"))
    print(ID("Iva Ilakovac"))

    with open('resources/tiny.pickle', 'rb') as f:
        tiny = pickle.load(f)

    with open('resources/small.pickle', 'rb') as f:
        small = pickle.load(f)

    with open('resources/large.pickle', 'rb') as f:
        large = pickle.load(f)

    tinyTransform = transform_data(tiny)
    for ID in tinyTransform[0]:
        print()
        print(name(tinyTransform[0][ID].ID))
        print(tinyTransform[0][ID].ID)
        print(tinyTransform[0][ID].baconPath)


