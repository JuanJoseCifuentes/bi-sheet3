import numpy as np
from scipy.optimize import minimize

#GET FREQUENT ITEMSETS
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


#METRICS
def getConfidence(sup_xy, sup_x):
    return sup_xy / sup_x

def getLift(conf, sup_y, len_database):
    rsup_y = sup_y / len_database
    lift = conf / rsup_y
    return lift

def getLeverage(sup_xy, sup_x, sup_y, len_database):
    rsup_xy = sup_xy / len_database
    rsup_x = sup_x / len_database
    rsup_y = sup_y / len_database

    leverage = rsup_xy - (rsup_x * rsup_y)
    return leverage

def getJaccard(sup_xy, sup_x, sup_y):
    jaccard_denominator = sup_x + sup_y - sup_xy
    jaccard = sup_xy / jaccard_denominator
    return jaccard

def getConviction(conf, sup_y, len_database):
    rsup_y = sup_y / len_database
    conviction_denominator = 1 - conf
    conviction = (1 - rsup_y) / conviction_denominator
    return conviction

def getOddsRatio(sup_xy, sup_x, sup_y, len_database):
    sup_nox_y = sup_y - sup_xy
    sup_x_noy = sup_x - sup_xy
    sup_nox_noy = len_database - sup_xy - sup_nox_y - sup_x_noy

    odds_denominator = sup_x_noy * sup_nox_y
    odds = (sup_xy * sup_nox_noy) / odds_denominator
    return odds


#GET RULES
def getStrongRulesFromFrequentSets(fsets, minconf, len_database):
    strong_rules = []
    fsets_sets = [item[0] for item in fsets]
    fsets_supp = [item[1] for item in fsets]
    for i, frequentSet in enumerate(fsets_sets):
        if len(frequentSet) >= 2:
            A = getSubsets(set=frequentSet)
            while len(A) != 0:
                X = A[-1]
                A.remove(X)

                sup_xy = fsets_supp[i]
                
                index_x = fsets_sets.index(X)
                sup_x = fsets_supp[index_x]

                conf = getConfidence(sup_xy, sup_x)
                if conf >= minconf:
                    #Y is the complement of X in the set frequentSet
                    Y = list(frequentSet)
                    for item in X:
                        Y.remove(item)

                    sup_y = fsets_supp[fsets_sets.index(Y)]

                    lift = getLift(conf, sup_y, len_database)
                    lev = getLeverage(sup_xy, sup_x, sup_y, len_database)
                    jacc = getJaccard(sup_xy, sup_x, sup_y)
                    conv = getConviction(conf, sup_y, len_database)
                    odds = getOddsRatio(sup_xy, sup_x, sup_y, len_database)

                    strong_rules.append((X, Y, (conf, lift, lev, jacc, conv, odds)))
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


#GROUP IT ALL TOGETHER
def getStrongRulesForDatabase(db, minsup, minconf):
    fsets = eclat(db, minsup)

    len_data = len(db)

    strong_rules = getStrongRulesFromFrequentSets(fsets, minconf, len_data)
    return strong_rules


#PROMEDIO PONDERADO
def calculate_weighted_score(conf, lift, lev, jacc, conv, odds, weights):
    total_score = np.average([conf, lift, lev, jacc, conv, odds,], weights=weights, axis=0)
    return total_score

#RECOMMENDER
class Recommender:
    """
        This is the class to make recommendations.
        The class must not require any mandatory arguments for initialization.
    """
    def __init__(self):
        self.rules = {}
        self.prices = {}
        self.weights = [3,3.5,3.5,4,6,8]


    def train(self, prices, database) -> None:
        """
            allows the recommender to learn which items exist, which prices they have, and which items have been purchased together in the past
            :param prices: a list of prices in USD for the items (the item ids are from 0 to the length of this list - 1)
            :param database: a list of lists of item ids that have been purchased together. Every entry corresponds to one transaction
            :return: the object should return itself here (this is actually important!)
        """
        
        rules_db = getStrongRulesForDatabase(db=database, minsup=0.002*len(database), minconf=0.1)
        premises, conclusions, metrics = [], [], []

        for rule in rules_db:
            premises.append(tuple(rule[0]))
            conclusions.append(tuple(rule[1]))
            metrics.append(rule[2])

        normalized_metrics = []
        grouped_metrics = ()
        for i in range(len(metrics[0])):
            metric = [x[i] for x in metrics]
            grouped_metrics = grouped_metrics + (metric,)
            min_metric = min(metric)
            max_metric = max(metric)
                
            normalized_metric = []
            for meassure in metric:
                normalized_meassure = (meassure - min_metric) / (max_metric - min_metric)
                normalized_metric.append(normalized_meassure)
            normalized_metrics.append(normalized_metric)

        metrics = list(zip(*normalized_metrics))

        temp_rules = list(zip(premises,conclusions))
        for i, rule in enumerate(temp_rules):
            self.rules[rule] = metrics[i]

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
                rule = (tuple(premise), tuple(conclussions[i]))
                metrics = self.rules[rule]
                
                total_score = calculate_weighted_score(metrics[0], metrics[1], metrics[2],metrics[3],metrics[4],metrics[5],self.weights)

                possible_recommendations.append((conclussions[i], total_score))
        possible_recommendations = sorted(possible_recommendations, key=lambda x:x[1])

        #Gets 0.4 of the total best items according to our evaluation and sorts them by price
        best_recommendations = []
        best_recommendations_prices = []

        for i in range(len(possible_recommendations)):
            if len(best_recommendations) >= max_recommendations + 0.4 * len(self.prices):
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