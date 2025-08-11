from math import comb, floor, ceil
from itertools import count
from scipy.stats import nhypergeom
from typing import List, Optional, Dict
from Interfaces.abstract_interface import Interface
import random
import heapq
from collections import Counter
import csv

from context.Map import MapGraph
from context.Map import Route
from context.decks import DestinationTicket
from context.player_context import PlayerContext, OpponentInfo

class CalebsBot(Interface):
    risk_appetite: float
    endgame_threshold: int

    def __init__(self):
        super().__init__()
        self.precompute_data = self.read_routes_from_csv("shortest_paths_precompute.csv")

    def set_player(self, player):
        """Provide the Player instance that this interface controls."""
        self.player = player
        self.risk_appetite = float(self.player.name.split(sep = "_")[-1])
        self.endgame_threshold: int = ceil(3 + 2 * self.risk_appetite)

    # used to determine whether to
    # 1 = Draw
    # 2 = Claim
    # 3 = draw a destination ticket
    def choose_turn_action(self) -> int:
        """Decide which action to take this turn."""
        # if there is a route in the wishlist we can afford, claim it (make sure not to spend reserved colors for grays)
        claimable = self.player.get_affordable_routes()
        if claimable:
            claimable.sort(
                key = lambda x: (
                    x[1],
                    -x[0].length,
                    x[0].color != 'X'
                )
            )
            city_goals: set[str] = set()
            for ticket in [t for t in self.player.get_tickets() if not t.is_completed]:
                city_goals.add(ticket.city1)
                city_goals.add(ticket.city2)
            path_results = self.path_finder(city_goals.pop(), [city for city in city_goals]) if city_goals else None
            if path_results:
                wishlist_routes, wishlist_colors = path_results
            else:
                wishlist_routes = None
                wishlist_colors = None
            hand = self.player.get_hand()
            for route, loco_needed in claimable:
                if not wishlist_routes:
                    if route.color != 'X':
                        return 2
                    eligible_colors = [color for color, count in hand.items() if count >= route.length - loco_needed]
                    if eligible_colors:
                        return 2
                elif route in wishlist_routes:
                # If not a gray route, claim it
                    if route.color != "X":
                        return 2
                    # For gray routes, check if we can pay with a non-wishlist color or with a wishlist color without dipping below wishlist need
                    eligible_colors = [color for color, count in hand.items() if count >= route.length]
                    for color in eligible_colors:
                        # If we can pay with a non-wishlist color or with wishlist color and still have enough left for wishlist
                        if color not in wishlist_colors or (type(wishlist_colors) == Counter and (hand[color] - route.length >= wishlist_colors.get(color))): # type:ignore
                            # if we can pay without locomotives or if we are in the endgame
                            if loco_needed == 0 or self.estimate_turns_until_end(bypass = True) < (3 * self.endgame_threshold):
                                return 2

        # if we are too close to the end of the game to draw another destination ticket, do cost calculation to decide which routes to go for
        # if any destination tickets are incomplete, draw train cards. Otherwise, draw new destination tickets.
        for ticket in self.player.get_tickets():
            if not ticket.is_completed or self.estimate_turns_until_end(bypass = True) < (3 * self.endgame_threshold):
                return 1
        return 3

    ##############################################################################################
    # now that you`ve decided what action to take on your turn, decide how to handle each action #
    ##############################################################################################

    # choose what cards to draw
    def choose_draw_train_action(self) -> List[int]:
        """Choose which face-up index to draw or ``-1`` for the deck."""

        # Get wishlist colors (most needed for target routes)
        city_goals: set[str] = set()
        for ticket in [t for t in self.player.get_tickets() if not t.is_completed]:
            city_goals.add(ticket.city1)
            city_goals.add(ticket.city2)
        path_results = self.path_finder(city_goals.pop(), [city for city in city_goals])
        if path_results:
            wishlist_routes, wishlist_colors = path_results
        else:
            raise ValueError("No valid path found to complete destination tickets.")
        color_counts = wishlist_colors['colors']
        sorted_colors = [color for color, _ in color_counts.most_common()] # type: ignore
        face_up = self.player.context.face_up_cards
        draw_choices = []
        hand = self.player.get_hand()

        def check_infinite_mulligan_risk(draw_choices) -> tuple[float, int|None]:
            """
            Exact hypergeometric probability that the market has at least 3 non-L's after n_turns.

            Returns:
                (risk, safe_locomotive_index)
            """
            # Find locomotive indices
            locomotive_indices = [i for i, card in enumerate(face_up) if card == 'L']
            accessible_cards = self.get_card_accessibility()

            # Current market non-L count
            market_non_l_start = len(face_up) - len(locomotive_indices)

            # Deck composition
            deck_size = accessible_cards.total()
            deck_l = accessible_cards.get('L', 0)
            deck_non_l = accessible_cards.total() - deck_l

            # Total number of replacements
            num_turns = 3
            replacements_per_turn = 2
            draws = min(num_turns * replacements_per_turn, deck_size)

            # Hypergeometric probability sum
            prob_safe = 0.0
            for k in range(0, draws + 1):
                # k = number of non-L's drawn from deck into market
                final_non_l = market_non_l_start + k - (draws - k)  # gains minus losses
                if final_non_l >= 3:
                    ways_choose_nonl = comb(deck_non_l, k)
                    ways_choose_l = comb(deck_l, draws - k)
                    total_ways = comb(deck_size, draws)
                    prob_safe += (ways_choose_nonl * ways_choose_l) / total_ways

            # Pick a safe locomotive index if one exists
            return 1 - prob_safe, locomotive_indices[0] if locomotive_indices else None
        
        # First, pick wishlist colors from the face-up cards
        for color in sorted_colors:
            if len(draw_choices) == 2:
                # risk, safe_choice = check_infinite_mulligan_risk(draw_choices)
                # return [safe_choice] if safe_choice and risk > 0.8 else draw_choices
                return draw_choices
            if color in face_up:
                for index, market_color in enumerate(face_up):
                    if market_color == color and hand[color] < color_counts[color]:
                        # If we have less than wishlist, pick this color
                        draw_choices.append(index)
                    else:
                        # If we have enough of this color, move on to the next color
                        continue

        # If less than 2 choices, pick most common hand colors not in wishlist but in face-up
        if len(draw_choices) < 2:
            wishlist_set = set(sorted_colors)
            for color, _ in hand.most_common():
                if len(draw_choices) == 2:
                    return draw_choices
                if color not in wishlist_set and color in face_up:
                    draw_choices.append(face_up.index(color))

        # If still no choices and there are locomotives face-up, pick one
        # TODO: weigh locomotives more heavily if close to a large route, and less if there are few colors we don't have
        if not draw_choices and 'L' in face_up:
            return [face_up.index('L')]

        # If the draw hasn't filled up, fill up with -1 (deck) until two cards are chosen
        while len(draw_choices) < 2:
            draw_choices.append(-1)

        return draw_choices

    # choose what routes to claim -------------------------------------------------------------------#
    # claimable_routes is a list of tuples( Route , number of locomotives needed to claim)           #
    # return a tuple (route, number of locomotives you wish to spend)                                #
    # so to buy a route that costs 2 of a color using 1 locomotive you could return tuple(route, 1)  #
    # error handling is done on the back end --------------------------------------------------------#
    def choose_route_to_claim(self, claimable_routes: 'List[tuple[Route,int]]') -> 'tuple[Route,int]':
        """Select a route and number of locomotives to spend. Returns a tuple (route, number of locomotives).
        Returns None if there are no affordable target routes or if there are no claimable routes."""
        # Find the most expensive route from target_routes that is also claimable
        city_goals: set[str] = set()
        claimable_routes.sort(
            key = lambda x: (
                x[1],                # fewer locomotives
                x[0].color == "X",   # False (colored) before True (gray)
                -x[0].length         # longer first
            )
        )
        for ticket in [t for t in self.player.get_tickets() if not t.is_completed]:
            city_goals.add(ticket.city1)
            city_goals.add(ticket.city2)
        path_results = self.path_finder(city_goals.pop(), [city for city in city_goals])
        if path_results:
            target_routes = path_results[0]
        else:
            raise ValueError("No valid path found to complete destination tickets.")
        
        if not target_routes:
            return claimable_routes[0]

        # TODO: limit locomotive use based on risk appetite?
        # Build a set for fast lookup
        target_set = set(target_routes)
        # Sort claimable_routes by:
            # 1. Is in target_routes
            # 2. Fewer locomotives needed
            # 3. Not gray (prefer colored)
            # 4. Route length (descending)
        filtered = [
            (route, locos)
            for route, locos in claimable_routes
            if route in target_set
        ]
        return filtered[0] if filtered else claimable_routes[0]

    # choose what color to spend on a gray route (will spend most common color on input of None or on invalid color input)
    def choose_color_to_spend(self, route: Route, color_options: List[str]) -> "str | None":
        """Pick a color to spend on gray routes."""
        hand = self.player.get_hand()
        city_goals: set[str] = set()
        for ticket in [t for t in self.player.get_tickets() if not t.is_completed]:
            city_goals.add(ticket.city1)
            city_goals.add(ticket.city2)
        path_results = self.path_finder(city_goals.pop(), [city for city in city_goals])
        if path_results:
            wishlist = path_results[1]["colors"]
        else:
            raise ValueError("No valid path found to complete destination tickets.")
        # Allow colors in wishlist only if enough remain after spending for this route
        eligible_colors = []
        for color, count in hand.items():
            if color in color_options and count >= route.length:
                needed = wishlist.get(color, 0) # type:ignore
                # If this color is in wishlist and we can still afford it after spending
                if color not in wishlist or (count - route.length) >= needed:
                    eligible_colors.append((color, count))
        if eligible_colors:
            # Return the least common eligible color
            return min(eligible_colors, key=lambda x: x[1])[0]
        # Fallback: return None, which will by default pick the most common eligible color
        return None

    # choose which destination tickets to keep
    def select_ticket_offer(self, offer) -> List[DestinationTicket]: #TODO: implement special logic for first turn (check if len(player.get_tickets()) == 0)
        """Choose which destination tickets to keep.

        Takes as many as possible without the cost exceeding what the player can spend before the end of the game,
        maximizing expected value.
        """
        hand = self.player.get_hand()
        options = []
        min_kept = 1 if self.player.get_tickets() else 2

        # calculate value and train car cost for each ticket and combination of tickets
        # single tickets (only calculate if keeping one ticket is an option)
        if min_kept == 1:
            for ticket in offer:
                cost, expected_value, routes, wishlist = self.calculate_tickets_value([ticket])
                if cost < self.player.trains_remaining:
                    options.append(([ticket], cost, expected_value, routes, wishlist))

        # two tickets
        for ticket in [t1 for t1 in offer]:
            for ticket2 in [t2 for t2 in offer if t2 != ticket and [ticket, t2] not in [o[0] for o in options] and [t2, ticket] not in [o[0] for o in options]]:
                cost, expected_value, routes, wishlist = self.calculate_tickets_value([ticket, ticket2])
                if cost < self.player.trains_remaining:
                    options.append(([ticket, ticket2], cost, expected_value, routes, wishlist))

        # all three tickets
        cost, expected_value, routes, wishlist = self.calculate_tickets_value(offer)
        if cost < self.player.trains_remaining:
            options.append((offer, cost, expected_value, routes, wishlist))

        # if none of the options are affordable with how many trains remain, choose the one with the lowest value to minimize score loss
        if not options:
            return [min(offer, key = lambda x: x.value)]

        # Sort by expected value descending
        options.sort(key=lambda x: x[2], reverse=True)

        def estimate_turn_cost(routes, wishlist) -> int: # TODO: revisit this
            """
            Estimate how many turns a given list of routes will take to fully claim and return the estimate as an int
            """
            turn_count = len(routes)
            # Estimate how many turns it would take to draw all needed cards
            wishlist_colors = wishlist['colors']
            wishlist_gray = sorted(wishlist['gray'], reverse = True)
            hand_copy = hand.copy()
            for color, count in wishlist_colors.items():
                if color in hand_copy:
                    hand_copy[color] -= count
                else:
                    hand_copy[color] = -count

            # Get accessible cards
            accessible_cards = self.get_card_accessibility()
            
            # Loop through wishlist colors and take stock of how many we can fill from accessible colors
            for color, count in [item for item in wishlist_colors.items() if wishlist_colors[item[1]] < 0]:
                adjust_value = min(accessible_cards.get(color, 0), -count)
                if color in accessible_cards:
                    accessible_cards[color] -= adjust_value
                wishlist_colors[color] = count + adjust_value

                # Calculate expected turn cost
                turn_count += ceil(float(adjust_value) * (1.0 + self.risk_appetite)) # Assumes different rates of relevant card draw depending on risk appetite (1 per turn at 0 and 2 per turn at 1)
                        
            # If we still have negative counts, check if we can fill them with locomotives
            for color, count in [item for item in wishlist_colors.items() if wishlist_colors[item[1]] < 0]:
                adjust_value = min(hand_copy.get('L', 0), -count)
                if 'L' in hand_copy:
                    hand_copy['L'] -= adjust_value
                wishlist_colors[color] = count + adjust_value
            
            # If we still have negative counts, check if there are enough accessible locomotives to fill them
            for color, count in [item for item in wishlist_colors.items() if wishlist_colors[item[1]] < 0]:
                adjust_value = min(accessible_cards["L"], -count)
                accessible_cards["L"] -= adjust_value
                wishlist_colors[color] = count + adjust_value

                # Map risk tolerance to confidence level, requiring an 80% confidence level at risk appetite 0 and a 99% confidence level at risk appetite 100
                confidence = 0.99 - 0.19 * self.risk_appetite

                # Calculate total unknown cards
                total_unknowns = sum((o.num_cards_in_hand - o.exposed_hand.total()) for o in self.player.context.opponents) + len(self.player.context.train_deck)

                # Negative hypergeometric in scipy: nhypergeom(M, K, r)
                dist = nhypergeom(M=total_unknowns, K=accessible_cards["L"], r=adjust_value)

                # Use percent point function (inverse CDF) to get the quantile
                min_draws = ceil(dist.ppf(confidence))
                turn_count += min_draws
                accessible_cards["L"] -= adjust_value

            # TODO (STRETCH): instead of this, find a way to allow for the fact that cards will become accessible as they are paid (and maybe even prioritize paying those colors to get them back sooner)
            for color, count in [item for item in wishlist_colors.items() if wishlist_colors[item[1]] < 0]:
                return 99999

            # Assuming color needs are filled, fill gray route needs from remaining accessible cards if possible, using remaining locomotives to supplement where possible/necessary
            for gray_cost in wishlist_gray:
                color = min([color for color, count in accessible_cards.items() if count >= gray_cost], key = lambda x: accessible_cards[x], default = None)
                if color:
                    wishlist_gray.remove(gray_cost)
                    accessible_cards[color] -= gray_cost
                # TODO (STRETCH): instead of this, find a way to allow for the fact that cards will become accessible as they are paid (and maybe even prioritize paying those colors to get them back sooner)
                else: 
                    return 99999

            # Add the number of routes to the previous turn count estimate (assuming one route per turn) and return 
            return turn_count

        # Choose the option that maximizes expected value without exceeding train cost
        train_counts = [self.player.trains_remaining] + [o.remaining_trains for o in self.player.context.opponents]
        turns_until_end = self.estimate_turns_until_end(bypass = True)
        option_info = []
        for tickets, cost, value, routes, wishlist in [o for o in options if o[3]]:
            turns_left = turns_until_end - estimate_turn_cost(routes, wishlist)
            option_info.append((tickets, turns_left, value / turns_until_end))
        # Sort options in descending order of estimated turn cost
        sorted_options: List[tuple[List[DestinationTicket], int, int]] = sorted(option_info, key = lambda x: (x[2], x[1]), reverse = True)
        if sorted_options[0][1] > 0:
            return sorted_options[0][0]
        
        # If no options are expected to be complete before the game ends, choose the option that is closest to resolving before the game ends
        return min([o for o in sorted_options if len(o[0]) == min_kept], key = lambda x: x[1])[0]


    #######################
    #       helpers       #
    #######################

    def parse_route_str(self, route_str: str) -> list[tuple[str, str, int, str]]:
        routes = []
        if route_str:
            for part in route_str.split("|"):
                city_pair, length, color = part.split(":")
                city1, city2 = city_pair.split("-")
                routes.append(Route(city1, city2, int(length), color))
        return routes

    def read_routes_from_csv(self, filename="shortest_paths.csv") -> dict[str, dict[str, tuple[list[tuple[str, str, int, str]], int]]]:
        data = {}
        with open(filename, mode="r", newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                start = row["start_city"]
                end = row["end_city"]
                route_str = row["route_str"]
                length = int(row["length"])

                route_list = self.parse_route_str(route_str)

                if start not in data:
                    data[start] = {}
                data[start][end] = (route_list, length)
        return data

    def calculate_tickets_value(self, tickets: List[DestinationTicket]) -> tuple[int, float, List[Route], Dict[str, Counter | List]]:
        """
        Estimate the cost (in train cards) to complete the given list of destination tickets.
        Uses the shortest available path that completes all tickets.
        Already claimed routes are treated as zero-cost (free to traverse) if claimed by self,
        but routes claimed by other players are unnavigable.
        Returns None if no path exists to complete all tickets, otherwise returns a tuple
        (total cost in train cars, expected value of the tickets, route wishlist, color wishlist).
        Color wishlist structure is {'colors': Counter[str], 'gray': List[int]}.
        """
        cities = set()
        for ticket in tickets:
            cities.add(ticket.city1)
            cities.add(ticket.city2)
        path_results = self.path_finder(cities.pop(), [c for c in cities])
        routes, wishlist = path_results if (path_results and path_results[0]) else ([], {'colors': Counter(), 'gray': []})
        
        train_car_total = 0
        if not routes:
            return (0, 0, routes, wishlist) # No routes to traverse
        for route in routes:
            train_car_total += route.length
        expected_value = sum(ticket.value for ticket in tickets) / train_car_total # TODO: factor in longest path
        return (train_car_total, expected_value, routes, wishlist)

    def get_card_accessibility(self) -> Counter[str]: # TODO: factor in market
        """
        Calculate the accessibility of each train card color based on the current hand and face-up cards.
        Returns a dictionary with colors as keys and the number of that color in the unknown as the value.
        The score is based on how many of that color are in hand, in opponents' exposed hands, and in the unknown pile.
        """
        accessible_cards = Counter[str]()
        face_up = self.player.context.face_up_cards
        for color in ["W", "B", "U", "G", "Y", "O", "R", "P"]:
            in_hand = self.player.get_hand().get(color, 0)
            known_cards = 0
            for opponent in self.player.context.opponents:
                known_cards += opponent.exposed_hand.get(color, 0)
            unknown_cards = 12 - known_cards
            accessible_count = in_hand + unknown_cards - len([c for c in face_up if c == color])
            accessible_cards.update({color: accessible_count})
        known_cards = 0
        for opponent in self.player.context.opponents:
            known_cards += opponent.exposed_hand.get("L", 0)
        accessible_cards.update({"L": self.player.get_hand().get("L", 0) + 14 - known_cards - len([c for c in face_up if c == 'L'])})
        return accessible_cards
    

    def path_finder(
        self,
        start_point: str,
        destinations: List[str]
    ) -> 'tuple[List[Route], dict[str, Counter | List]] | None':
        graph = self.player.context.map
        my_id = self.player.player_id

        def get_color_multiplier(route: Route) -> float:
            accessible_cards = self.get_card_accessibility()
            if route.color == "X":
                # gray routes are flexible, so they are treated as whichever color is most accessible
                return min(accessible_cards.values(), default=1.0) / 12.0
            else:
                # For colored routes, use the specific color's count
                return accessible_cards.get(route.color, 1.0) / 12.0

        # Heuristic function for A* (estimates cost to reach all remaining destinations)
        def heuristic(current: str, remaining: set[str]) -> int:
            return sum([self.precompute_data[current][r][1] for r in remaining])

        def wishlist_signature(wishlist: dict) -> tuple:
            color_bucket = tuple(sorted((color, (count // 2) * 2) for color, count in wishlist['colors'].items()))
            gray_bucket = tuple(sorted((length // 2) * 2 for length in wishlist['gray']))
            return (color_bucket, gray_bucket)

        initial_remaining = set(destinations)
        if start_point in initial_remaining:
            initial_remaining.remove(start_point)

        # Each state: (est_total, tie-breaker, cost_so_far, current, remaining, path, visited_cities, wishlist)
        heap = [
            (
                float(heuristic(start_point, initial_remaining)),  # priority
                0,  # tie-breaker: prefer longer path (negated later)
                0.0,
                start_point,
                frozenset(initial_remaining),
                [],
                set([start_point]),
                {'colors': Counter(), 'gray': []}
            )
        ]
        visited_states = {}
        counter = count()

        while heap:
            # Pop the state with the lowest estimated total cost
            _, _, cost_so_far, current, remaining, path, visited_cities, wishlist = heapq.heappop(heap)

            state_key = (
                current,
                remaining,
                path[-1]
            ) if path else (
                current,
                remaining
            )
            if state_key in visited_states and visited_states[state_key] <= cost_so_far:
                continue
            visited_states[state_key] = cost_so_far

            # If all destinations have been visited, return the path
            if not remaining:
                return [p for p in path if p.claimed_by != self.player.player_id], wishlist

            # Explore all routes from the current city
            for route in graph._adj.get(current, []):
                if route.claimed_by is not None and route.claimed_by != my_id:
                    continue

                neighbor = route.other_city(current)
                if neighbor in visited_cities:
                    continue

                route_cost = 0 if route.claimed_by == my_id else route.length * get_color_multiplier(route)

                new_wishlist = {
                    'colors': wishlist['colors'].copy(),
                    'gray': list(wishlist['gray'])
                }

                if route.claimed_by != my_id:
                    if route.color == "X":
                        new_wishlist['gray'].append(route.length)
                    else:
                        new_wishlist['colors'][route.color] += route.length

                # # Gray simulation for pruning (in-place temp solution, written by AI. Testing to see how well the bot does without it)
                # test_wishlist = new_wishlist['colors'].copy()
                # for g in sorted(new_wishlist['gray'], reverse=True):
                #     least_needed = min(test_wishlist, key=test_wishlist.get, default=None)
                #     if least_needed is not None:
                #         test_wishlist[least_needed] += g

                # if test_wishlist and max(test_wishlist.values(), default=0) > 12:
                #     continue

                new_remaining = set(remaining)
                if neighbor in new_remaining:
                    new_remaining.remove(neighbor)

                heapq.heappush(
                    heap,
                    (
                        cost_so_far + route_cost + heuristic(neighbor, new_remaining),
                        next(counter), # tiebreaker
                        float(cost_so_far + route_cost),
                        neighbor,
                        frozenset(new_remaining),
                        path + [route],
                        visited_cities | {neighbor},
                        new_wishlist
                    )
                )

        return None  # No valid path found

    def estimate_turns_until_end(self, bypass: bool = False) -> int:
        """
        If the endgame threshold has been reached, estimate the minimum number of turns
        before any player runs out of trains, assuming that the player with the least
        number of trains tries to spend their remaining trains as quickly as possible.
        """

        # a player is an endgame threat if the difference between their train count and their hand size is less than the endgame threshold
        endgame_threats = [(o, o.remaining_trains) for o in self.player.context.opponents if o.remaining_trains - o.num_cards_in_hand < self.endgame_threshold]

        if not endgame_threats:
            return 50
        
        # for testing purposes. TODO: remove along with associated parameter once this is the only bottleneck
        if bypass:
            return min([t - o.num_cards_in_hand for o, t in endgame_threats])

        min_turns = float('inf')

        # check each opponent who is within reach of endgame to see how many turns it would take them to run out if they wanted to
        for opponent, trains in endgame_threats:
            hand = Counter(getattr(opponent, 'exposed_hand', Counter()))
            market = self.player.context.face_up_cards.copy()
            known_cards = sum(hand.values())
            # unknown_cards is the difference between the total number of cards in the opponent's hand (num_cards_in_hand) and the exposed cards (known_cards)
            unknown_cards = getattr(opponent, 'num_cards_in_hand', known_cards) - known_cards

            all_routes = self.player.context.map.get_available_routes()

            accessible_cards = self.get_card_accessibility()
            accessible_colors = accessible_cards.copy()
            accessible_locomotives = accessible_colors.pop('L')

            #################
            # CARDS IN HAND #
            #################

            # If they don't have enough cards in their hand to end the game, check the market first for known cards in colors they already have
            if hand.total() <= trains - 2:
                market_goodies = [card for card in market if card in hand.keys() and card != 'L']
                min_turns += ceil(float(len(market_goodies)) / 2.0)

            # For now, just subtract the locomotive count from the train count
            trains -= hand.pop('L', 0)

            # function to update claimable route lists TODO: eventually implement a way to make sure routes don't get double-claimed
            def update_claimable():
                optimistic = [r for r in claimable_optimistic if (r.color != 'X' and r.length < min(trains, hand.get(r.color, 0) + unknown_cards)) or r.length < min(trains, max(hand.values()) + unknown_cards)]
                pessimistic = [r for r in optimistic if (r.color != 'X' and r.length < min(trains, hand.get(r.color, 0))) or r.length < min(trains, max(hand.values()))]
                return optimistic, pessimistic
            
            # get all the routes that are at least optimistically claimable (assuming the correct cards are in the unknowns), and then a second card that only factors in known cards
            claimable_optimistic = sorted([r for r in all_routes if (r.color != 'X' and r.length < min(trains, hand.get(r.color, 0) + unknown_cards)) or r.length < min(trains, max(hand.values()) + unknown_cards)], key = lambda x: (x.length, x.color == 'X'), reverse = True)
            claimable_pessimistic = [r for r in claimable_optimistic if (r.color != 'X' and r.length < min(trains, hand.get(r.color, 0))) or r.length < min(trains, max(hand.values()))]

            # create a copy of hand so we have the original for later, along with a list of expenditures so that we can more easily check for opportunities to lump unknowns in later
            spent = []
            hand_copy = hand.copy()

            # figure out how long it would take to play out all the colors in hand
            for route in claimable_pessimistic:
                # if there aren't enough of the color left to claim the shortest elegible route, end the loop
                if (trains - 2 - sum([n for _, n in spent])) >= claimable_pessimistic[-1].length:
                    break
                # if the game hasn't ended yet
                elif (trains - 2 - sum([n for _, n in spent])) <= route.length:
                    color = route.color if route.color != 'X' else accessible_colors.most_common(1)[0][0]
                    hand_copy[color] -= route.length
                    spent.append((color, route.length))
                    min_turns += 1
                    claimable_optimistic, claimable_pessimistic = update_claimable()
            
            ############
            # UNKNOWNS #
            ############

            # first, if there are still not enough cards in hand to end the game, draw until there are (add unknowns)
            if hand.total() + unknown_cards <= trains - 2:
                unknown_cards = trains - hand.total() - 2
                min_turns += (trains - 2 - hand.total() - unknown_cards) / 2

            # create a dictionary that maps each gray route to the chance it will be needed 
            reserved_grays: Dict[Route,float] = {}

            # check the probability that unknown cards of each color we are spending will not be able to be lumped in
            for _ in range(0, len(spent)):
                color, count = spent.pop(0)
                fail_prob, progress = 0.0, float(count)
                count_cases = range(1, min(unknown_cards, accessible_colors[color]))
                for k in count_cases:
                    claimable_by_color = [r for r in claimable_optimistic if r.length == count + k and r.color == color]
                    claimable_grays = [r for r in claimable_optimistic if r.length == count + k and r.color == 'X']

                    # find the probability that k will be drawn
                    this_prob: float = float(comb(accessible_cards[color], k) * comb(sum(accessible_cards.values()) - accessible_cards[color], unknown_cards - k)) / float(comb(sum(accessible_cards.values()), unknown_cards))
                    progress += (k) + this_prob

                    # if they only have gray routes of length k, reserve one with strength prob
                    if claimable_grays and not claimable_by_color:
                        for route in claimable_grays:
                            # if the route is not reserved yet, the chance that we will need it is equal to the probability of drawing k of the given color
                            if route not in reserved_grays.keys():
                                reserved_grays.update({route: this_prob})
                                break
                            # if the route is already reserved, add the chance that the other reserving routes don't need it and this one does to the reservation weight
                            #   and change the probability for future cycles of the loop to be equal to the chance that we have k of the color and couldn't get this one
                            else:
                                # normally I wouldn't use a dual assignment like this for readability's sake but each calculation takes both original values
                                reserved_grays[route], this_prob = reserved_grays[route] + (1- reserved_grays[route]) * this_prob, reserved_grays[route] * this_prob  

                    # if they do not have any routes of length k that the color can claim and this is the last expenditure of this color, add the probability to the running total of ones that will require an extra turn
                    elif not claimable_by_color and color not in [c for c, _ in spent]:
                        fail_prob += this_prob

                # For now I will assume that the versatility offered by grays and the locomotives will mean that the opponent will only need 
                #   1 extra turn to spend the unknown cards of the given color enough of the time that it can safely be taken as guaranteed TODO: revise this assumption in light of logic change 
                min_turns += fail_prob
                
                # if 
                if progress + 2 > trains and count < trains:
                    return floor(min_turns)
                elif progress < trains:
                    trains -= progress
                claimable_optimistic, claimable_pessimistic = update_claimable()

            # TODO: check on the probability of not being able to claim a route in the case where I draw and still can't afford to play out the hand if necessary (due to the sizes of numbers we're dealing with it may not be necessary)
            # route_turn_costs: Dict[Route, float] = {}
            
            # for each remaining route in claimable_routes, figure out the probability of being able to claim it,
            # for route in claimable_optimistic:
            #     color = route.color if route.color != 'X' else None
            #     # the probability of being able to claim any given route is equal to the
            #     prob = float(comb(accessible_cards[color], route.cost) * comb(sum(accessible_cards.values()) - accessible_cards[color], unknown_cards - k)) / float(comb(sum(accessible_cards.values()), unknown_cards))
        
        return floor(min_turns)