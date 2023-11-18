def eclat(db, minsup):
    def generate_frequent_itemsets(P, minsup, F):
        for i, p_i in enumerate(P):
            Xa, t_Xa = p_i
            if not isinstance(Xa, list):
                Xa = [Xa]
            F.append((Xa, len(t_Xa)))
            Pa = []
            for j in range(i + 1, len(P)):
                Xb, t_Xb = P[j]
                if not isinstance(Xb, list):
                    Xb = [Xb]
                if j > i:
                    Xab = list(set(Xa).union(set(Xb)))
                    Xab.sort()
                    t_Xab = t_Xa.intersection(t_Xb)
                    if len(t_Xab) >= minsup:
                        Pa.append((Xab, t_Xab))
            if len(Pa) != 0:
                generate_frequent_itemsets(Pa, minsup, F)

    P = {}
    for i in range(len(db)):
        for item in db[i]:
            if item in P:
                P[item].add(i)
            else:
                P[item] = {i}
    P = list(P.items())
    
    condition = lambda x: len(x[1]) >= minsup
    P = [item for item in P if condition(item)]

    P = sorted(P, key=lambda x: x[0])
    F = []
    
    generate_frequent_itemsets(P, minsup, F)

    return [(F[i][0], F[i][1]) for i in range(len(F))]

def getStrongRulesFromFrequentSets(fsets, minconf):
    strong_rules = []
    fsets_sets = [item[0] for item in fsets]
    fsets_supp = [item[1] for item in fsets]
    for i, frequentSet in enumerate(fsets_sets):
        if len(frequentSet) >= 2:
            A = getSubsets(set=frequentSet)
            while len(A) != 0:
                X = A[-1]
                A.remove(X)
                index_x = fsets_sets.index(X)
                c = fsets_supp[i] / fsets_supp[index_x]
                if c >= minconf:
                    #Y is the complement of X in the set frequentSet
                    Y = list(frequentSet)
                    for item in X:
                        Y.remove(item)

                    lift_denominator = fsets_supp[fsets_sets.index(X)]
                    lift = c / lift_denominator
                    strong_rules.append((X, Y, fsets_supp[i], c, lift))
                else:
                    if len(X) >= 2:
                        W_sets = getSubsets(X)
                        for W in W_sets:
                            if W in A:
                                A.remove(W)

    return strong_rules

def getSubsets(set):
    subsets = []
    x = len(set)
    for i in range(1 << x):
       subsets.append([set[j] for j in range(x) if (i & (1 << j))])

    subsets.pop(-1)
    subsets.pop(0)

    return subsets

def getStrongRulesForDatabase(db, minsup, minconf):
    fsets = eclat(db, minsup)
    strong_rules = getStrongRulesFromFrequentSets(fsets, minconf)
    return strong_rules

class Recommender:
    """
        This is the class to make recommendations.
        The class must not require any mandatory arguments for initialization.
    """
    def __init__(self):
        self.rules = {}
        self.prices = {}


    def train(self, prices, database) -> None:
        """
            allows the recommender to learn which items exist, which prices they have, and which items have been purchased together in the past
            :param prices: a list of prices in USD for the items (the item ids are from 0 to the length of this list - 1)
            :param database: a list of lists of item ids that have been purchased together. Every entry corresponds to one transaction
            :return: the object should return itself here (this is actually important!)
        """
        
        rules_db = getStrongRulesForDatabase(db=database, minsup=0.005*len(database), minconf=0.1)
        premises, conclusions, sup, conf, lift = [], [], [], [], []

        for rule in rules_db:
            premises.append(tuple(rule[0]))
            conclusions.append(tuple(rule[1]))
            sup.append(rule[2])
            conf.append(rule[3])
            lift.append(rule[4])
        
        temp_rules = list(zip(premises,conclusions))
        for i, rule in enumerate(temp_rules):
            self.rules[rule] = (sup[i], conf[i], lift[i])

        for i, price in enumerate(prices):
            self.prices[i] = price

        return self

    def get_recommendations(self, cart:list, max_recommendations:int) -> list:
        """
            makes a recommendation to a specific user
            
            :param cart: a list with the items in the cart
            :param max_recommendations: maximum number of items that may be recommended
            :return: list of at most `max_recommendations` items to be recommended
        """

        rules = list(self.rules.keys())
        premises, conclussions = [],[]
        for rule in rules:
            premises.append(list(rule[0]))
            conclussions.append(list(rule[1]))

        #Gets only the conclusions in which the cart is a subset or equal to the premise
        possible_recommendations = []
        for i, premise in enumerate(premises):
            if (all(x in cart for x in premise)):
                possible_recommendations.append((conclussions[i], self.rules[(tuple(premise), tuple(conclussions[i]))][2]))
        possible_recommendations = sorted(possible_recommendations, key=lambda x:x[1])

        #Gets the (at least) 10 best items according to our evaluation and sorts them by price
        best_recommendations = []
        best_recommendations_prices = []

        print(possible_recommendations[-20:])

        for i in range(len(possible_recommendations)):
            if len(best_recommendations) >= 10:
                break
            
            #Add the items in the best rule
            for item in possible_recommendations[-1][0]:
                if item not in best_recommendations:
                    best_recommendations.append(item)
                    best_recommendations_prices.append(self.prices[item])
                possible_recommendations[-1][0].remove(item)
                
            possible_recommendations.pop(-1)
        
        best_recommendations = [x for _, x in sorted(zip(best_recommendations_prices, best_recommendations), key=lambda pair: pair[0])]

        recommendations = []
        i=0
        while i < max_recommendations:
            if len(best_recommendations) == 0:
                break

            if best_recommendations[-1] not in recommendations:
                recommendations.append(best_recommendations.pop(-1))
                i = i + 1
            else:
                best_recommendations.pop(-1)

        if len(recommendations) > 0:
            return recommendations
        else:
            return[0]