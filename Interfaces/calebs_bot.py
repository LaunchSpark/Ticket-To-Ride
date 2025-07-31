from typing import List, Optional, Dict
from Interfaces.abstract_interface import Interface
import random
import heapq
from collections import Counter

from context.Map import MapGraph
from context.Map import Route
from context.decks import DestinationTicket

class CalebsBot(Interface):
    """Baseline bot that makes random choices.

    Helpful functions and attributes
    -------------------------------
    ``self.player`` is assigned by the game engine and exposes many helpers for
    making decisions. Some commonly used ones are listed below.

    ``self.player.get_affordable_routes()`` -> ``List[tuple[Route, int]]``
        Returns the routes you can currently afford and the locomotives required.
        Example::

            options = self.player.get_affordable_routes()
            if options:
                route, loco_needed = options[0]

    ``self.player.get_tickets()`` -> ``List[DestinationTicket]``
        Your destination tickets. Each ticket has ``city1``, ``city2``,
        ``value`` and ``is_completed`` attributes.
        Example::

            incomplete = [t for t in self.player.get_tickets() if not t.is_completed]

    ``self.player.get_hand()`` -> ``Counter[str]``
        Current train cards in hand, keyed by color letter.
        Example::

            red_cards = self.player.get_hand().get('R', 0)

    ``self.player.trains_remaining``
        How many trains you still have available.
        Example::

            if self.player.trains_remaining <= 2:
                # game will end soon
                pass

    ``self.player.context`` -> :class:`PlayerContext`
        Snapshot of public game state each turn. Useful fields include:

        - ``face_up_cards``: visible train cards in the market.
          Example::

              first = self.player.context.face_up_cards[0]

        - ``map``: :class:`MapGraph` representing the board. You can inspect
          routes via ``self.player.context.map.get_available_routes()`` or
          ``get_claimed_routes(player_id)``.

        - ``opponents``: list of ``OpponentInfo`` with each opponent's exposed
          cards, remaining trains, score and ticket count.
          Example::

              for opp in self.player.context.opponents:
                  print(opp.player_id, opp.score)

        - ``turn_number``: current turn index.
        - ``score``: your current score so far.
    """
    is_endgame: bool = False # TODO: implement endgame detection
    risk_appetite: float = 1.0
    # used to determine whether to
    # 1 = Draw
    # 2 = Claim
    # 3 = draw a destination ticket
    def choose_turn_action(self) -> int:
        """Decide which action to take this turn."""
        # if there is a route in the wishlist we can afford, claim it (make sure not to spend reserved colors for grays)
        claimable = self.player.get_affordable_routes()
        city_goals: set[str] = set()
        for ticket in [t for t in self.player.get_tickets() if not t.is_completed]:
            city_goals.add(ticket.city1)
            city_goals.add(ticket.city2)
        path_results = self.path_finder(city_goals.pop(), [city for city in city_goals])
        if path_results:
            wishlist_routes, wishlist_colors = path_results
        else:
            raise ValueError("No valid path found to complete destination tickets.")
        hand = self.player.get_hand()
        for route, loco_needed in claimable:
            if route in wishlist_routes:
            # If not a gray route, claim it
                if route.color != "X":
                    return 2
                # For gray routes, check if we can pay with a non-wishlist color or with a wishlist color without dipping below wishlist need
                eligible_colors = [color for color, count in hand.items() if count >= route.length]
                for color in eligible_colors:
                    # If we can pay with a non-wishlist color or with wishlist color and still have enough left for wishlist
                    if color not in wishlist_colors or (type(wishlist_colors) == Counter and (hand[color] - route.length >= wishlist_colors.get(color))): # type:ignore
                        # if we can pay without locomotives or if we are in the endgame
                        if loco_needed == 0 or self.is_endgame == True:
                            return 2

        # if we are too close to the end of the game to draw another destination ticket, do cost calculation to decide which routes to go for
        # if any destination tickets are incomplete, draw train cards. Otherwise, draw new destination tickets.
        for ticket in self.player.get_tickets():
            if not ticket.is_completed or self.is_endgame:
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

        # First, pick wishlist colors from the face-up cards
        for color in sorted_colors:
            if len(draw_choices) == 2:
                return draw_choices
            if color in face_up:
                for market_color, index in face_up:
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
        """Select a route and number of locomotives to spend."""
        # Find the most expensive route from target_routes that is also claimable
        target_routes = self.get_target_routes()
        if not claimable_routes or not target_routes:
            return claimable_routes[random.randrange(0, len(claimable_routes))]

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
        if filtered:
            filtered.sort(
                key=lambda x: (
                    x[1],                # fewer locomotives
                    x[0].color == "X",   # False (colored) before True (gray)
                    -x[0].length         # longer first
                )
            )
        return filtered[0]

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
    def select_ticket_offer(self, offer) -> List[DestinationTicket]:
        """Choose which destination tickets to keep.

        Takes as many as possible without the cost exceeding what the player can spend before the end of the game,
        maximizing expected value.
        """
        hand = self.player.get_hand()
        options = []

        # calculate value and train car cost for each ticket and combination of tickets
        # single tickets
        for ticket in offer:
            cost, expected_value = self.calculate_tickets_value([ticket])
            options.append(([ticket], cost, expected_value))

        # two tickets
        for ticket in [t1 for t1 in offer]:
            for ticket2 in [t2 for t2 in offer if t2 != ticket and [ticket, t2] not in [o[0] for o in options] and [t2, ticket] not in [o[0] for o in options]]:
                cost, expected_value = self.calculate_tickets_value([ticket, ticket2])
                options.append(([ticket, ticket2], cost, expected_value))

        # all three tickets
        value_calc = self.calculate_tickets_value(offer)
        options.append((offer, value_calc[0], value_calc[1]))

        # Sort by expected value descending
        options.sort(key=lambda x: x[2], reverse=True)

        # Choose the option that maximizes expected value without exceeding train cost
        for tickets, cost, _ in options:
            if cost < self.player.trains_remaining: # TODO: factor in turns remaining estimate
                return tickets
        
        # Always keep at least one ticket (game rule)
        return [o for o in options if len(o[0]) == 1][0][0][0] # Returns the first sigle ticket option as a default


    #######################
    #       helpers       #
    #######################

    def calculate_tickets_value(self, tickets: List[DestinationTicket]) -> tuple[int, float]:
        """
        Estimate the cost (in train cards) to complete the given list of destination tickets.
        Uses the shortest available path that completes all tickets.
        Already claimed routes are treated as zero-cost (free to traverse) if claimed by self,
        but routes claimed by other players are unnavigable.
        Returns None if no path exists to complete all tickets, otherwise returns a tuple 
        (total cost in train cars, expected value of the tickets).
        """
        cities = set()
        for ticket in tickets:
            cities.add(ticket.city1)
            cities.add(ticket.city2)
        path_results = self.path_finder(cities.pop(), [c for c in cities])
        routes, wishlist = path_results if path_results else ([], {'colors': Counter(), 'gray': []})
        
        train_car_total = 0
        for route in routes:
            train_car_total += route.length
        if train_car_total == 0:
            return (0, 0)  # No routes to traverse
        expected_value = sum(ticket.value for ticket in tickets) / train_car_total # TODO: factor in longest path
        return (train_car_total, expected_value)

    def get_target_routes(self) -> List[Route]:
        target_routes = []
        return target_routes

    def path_finder( # TODO: prefer longest path in case of ties
        self,
        start_point: str,
        destinations: List[str]
    ) -> 'tuple[List[Route], Dict[str, Counter | List]] | None':
        """
        Find a set of routes that connects start_point to all destinations,
        minimizing the sum of route lengths (A* search).
        Routes claimed by self are treated as zero-cost, routes claimed by others are ignored.
        Returns a tuple (list of Route objects, wishlist dict), or (0, 0) if not all destinations are reachable.
        The wishlist dict has keys 'colors' (Counter) and 'gray' (list of lengths).
        """
        graph = self.player.context.map  # MapGraph instance representing the game board
        my_id = self.player.player_id    # The current player's ID

        def get_color_multiplier(route: Route) -> float: # TODO: factor in the fact that locomotives exist
            """
            Calculate a cost multiplier for the route's length based on how many 
            of the required color cards are in the unknown pile or in hand, 
            to prefer routes with a higher chance of drawing the needed cards.
            Gray routes are the most flexible, so they get a lower multiplier.
            """
            accessible_cards = Counter[str]()
            for color in ["W", "B", "U", "G", "Y", "O", "R", "P"]:
                in_hand = self.player.get_hand().get(route.color, 0)
                known_cards = 0
                for opponent in self.player.context.opponents:
                    known_cards += opponent.exposed_hand.get(route.color, 0)
                unknown_cards = 12 - known_cards
                accessible_count = in_hand + unknown_cards
                accessible_cards.update({color: accessible_count})
            if route.color == "X":
                # gray routes are flexible, so they are treated as whichever color is most accessible
                return min(accessible_cards.values(), default=1.0) / 12.0
            else:
                # For colored routes, use the specific color's count
                return accessible_cards.get(route.color, 1.0) / 12.0

        # Heuristic function for A* (estimates cost to reach all remaining destinations)
        def heuristic(current: str, remaining: set[str]) -> float:
            # Use Dijkstra's algorithm to estimate the shortest path from current to each remaining destination,
            # then sum the costs. If a destination is unreachable, treat its cost as a large number.
            def dijkstra(start: str, end: str) -> float:
                heap = [(0.0, start)]
                visited = set()
                while heap:
                    cost, city = heapq.heappop(heap)
                    if city == end:
                        return cost
                    if city in visited:
                        continue
                    visited.add(city)
                    for route in graph._adj.get(city, []):
                        neighbor = route.other_city(city)
                        if neighbor in visited:
                            continue
                        # Ignore routes claimed by other players
                        if route.claimed_by is not None and route.claimed_by != my_id:
                            continue
                        # If claimed by self, cost is 0; else, cost is route.length
                        route_cost = 0 if route.claimed_by == my_id else route.length * get_color_multiplier(route)
                        heapq.heappush(heap, (cost + route_cost, neighbor))
                return 999999  # Large number if unreachable
            return sum(dijkstra(current, dest) for dest in remaining)

        # Each state in the search is a tuple:
        # (estimated_total_cost, cost_so_far, current_city, remaining_destinations, path_so_far, visited_cities)
        initial_remaining = set(destinations)
        if start_point in initial_remaining:
            initial_remaining.remove(start_point)  # Don't count the start if it's a destination

        # Each state: (est_total, cost_so_far, current, remaining, path, visited_cities, wishlist)
        heap = [
            (
                heuristic(start_point, initial_remaining),
                0.0,
                start_point,
                frozenset(initial_remaining),
                [],
                set([start_point]),
                {'colors': Counter(), 'gray': []}
            )
        ]
        visited_states = {}  # Memoization: (current_city, remaining_destinations) -> lowest cost found

        while heap:
            # Pop the state with the lowest estimated total cost
            est_total, cost_so_far, current, remaining, path, visited_cities, wishlist = heapq.heappop(heap)
            # Memoization key includes both city, remaining, and a tuple of sorted color counts and gray lengths
            state_key = (
                current,
                remaining,
                tuple(sorted(wishlist['colors'].items())),
                tuple(sorted(wishlist['gray']))
            )
            if state_key in visited_states and visited_states[state_key] <= cost_so_far:
                continue
            visited_states[state_key] = cost_so_far

            # If all destinations have been visited, return the path
            if not remaining:
                return path, wishlist

            # Explore all routes from the current city
            for route in graph._adj.get(current, []):
                # Ignore routes claimed by other players
                if route.claimed_by is not None and route.claimed_by != my_id:
                    continue
                neighbor = route.other_city(current)
                if neighbor in visited_cities:
                    continue  # Avoid cycles

                # If the route is already claimed by us, it's free; otherwise, use its length as cost
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

                # Prune if any color exceeds 12
                test_wishlist = new_wishlist['colors']
                for g in sorted(new_wishlist['gray'], reverse=True):
                    test_color = min(test_wishlist, key = test_wishlist.get, default=None)
                    test_wishlist[test_color] += g
                # If any color exceeds 12, skip this route
                if new_wishlist['colors'] and max(test_wishlist.values(), default=0) > 12:
                    continue

                # Remove neighbor from remaining destinations if it's one of them
                new_remaining = set(remaining)
                if neighbor in new_remaining:
                    new_remaining.remove(neighbor)

                # Push the new state onto the heap
                heapq.heappush(
                    heap,
                    (
                        cost_so_far + route_cost + heuristic(neighbor, new_remaining),
                        float(cost_so_far + route_cost),
                        neighbor,
                        frozenset(new_remaining),
                        path + [route],
                        visited_cities | {neighbor},
                        new_wishlist
                    )
                )
        # If the heap is empty and we haven't returned, not all destinations are reachable
        return None

    def estimate_turns_until_end(self) -> int:
        """
        Estimate the minimum number of turns before any player runs out of trains,
        taking into account trains_remaining and color breakdowns of each player's hand,
        and using risk_appetite to interpolate between pessimistic and optimistic assumptions
        about unknown cards in opponents' hands.
        """
        import math

        all_routes = self.player.context.map.get_available_routes()
        if not all_routes:
            return 1  # Game will end immediately if no routes left

        min_turns = float('inf')

        # Handle self (Player)
        trains = getattr(self.player, 'trains_remaining', 0)
        hand = self.player.get_hand()
        cards_in_hand = sum(hand.values())

        # For self, you know your hand exactly
        claimable_routes = [
            r for r in all_routes
            if r.length <= trains and r.claimed_by is None and (
                (r.color == "X" and any(hand.get(color, 0) + hand.get('L', 0) >= r.length for color in hand))
                or (r.color != "X" and hand.get(r.color, 0) + hand.get('L', 0) >= r.length)
            )
        ]
        if claimable_routes:
            max_len = max(r.length for r in claimable_routes)
            turns_to_claim = math.ceil(trains / max_len)
            min_turns = min(min_turns, turns_to_claim)
        else:
            min_route_len = min((r.length for r in all_routes if r.length <= trains and r.claimed_by is None), default=1)
            needed_cards = min_route_len
            cards_needed = max(0, needed_cards - cards_in_hand)
            draw_turns = math.ceil(cards_needed / 2) + 1
            min_turns = min(min_turns, draw_turns)

        # Handle opponents (OpponentInfo)
        for opp in self.player.context.opponents:
            trains = getattr(opp, 'remaining_trains', 0)
            hand = getattr(opp, 'exposed_hand', Counter())
            known_cards = sum(hand.values())
            total_cards = getattr(opp, 'num_cards_in_hand', known_cards)
            unknown_cards = max(0, total_cards - known_cards)

            # Risk interpolation: 0 = risk-averse (worst case), 1 = risk-seeking (best case)
            risk = getattr(self, 'risk_appetite', 0.5)
            risk = max(0.0, min(1.0, risk))  # Clamp to [0,1]

            # For each route, estimate if player can claim it
            claimable_routes = []
            for route in all_routes:
                if route.length > trains or route.claimed_by is not None:
                    continue
                if route.color == "X":
                    # For gray, can they pay with any color?
                    can_claim = any(
                        hand.get(color, 0) + hand.get('L', 0) +
                        math.floor(unknown_cards * risk) >= route.length
                        for color in hand
                    )
                else:
                    # Assume unknown cards are distributed to help/hinder as per risk
                    color_cards = hand.get(route.color, 0)
                    wilds = hand.get('L', 0)
                    # Pessimistic: all unknowns are the needed color; Optimistic: none are
                    extra = math.floor(unknown_cards * risk)
                    can_claim = (color_cards + wilds + extra) >= route.length
                if can_claim:
                    claimable_routes.append(route)

            if claimable_routes:
                max_len = max(r.length for r in claimable_routes)
                turns_to_claim = math.ceil(trains / max_len)
                min_turns = min(min_turns, turns_to_claim)
            else:
                # If can't claim, estimate how many turns to draw enough cards
                min_route_len = min((r.length for r in all_routes if r.length <= trains and r.claimed_by is None), default=1)
                needed_cards = min_route_len
                cards_needed = max(0, needed_cards - known_cards)
                draw_turns = math.ceil(cards_needed / 2) + 1
                min_turns = min(min_turns, draw_turns)

        return max(1, int(min_turns))