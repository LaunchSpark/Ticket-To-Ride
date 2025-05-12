from __future__ import annotations

"""Ticket‑to‑Ride **Game** module – interactive CLI + gameplay loop.

This file provides a *minimal but functional* front‑end to experiment with the
core mechanics while Strategy AI and scoring are still under construction.
"""

from typing import List, Optional, Dict, Any, Set, Tuple
import random
from collections import Counter

from Strategy import UnknownPoolSnapshot, PlayerSnapshot, GameSnapshot  # type: ignore
from Deck import TrainCardDeck
from Map import MapGraph
from Player import Player
from ticket_deck import TicketDeck, load_default_tickets, _key  # type: ignore
from display.live_heatmap_renderer import LiveHeatmapRenderer

# ---------------------------------------------------------------------------
# Helper – classify claimed edges
# ---------------------------------------------------------------------------

def _claimed_route_sets(board: MapGraph, me: str) -> Tuple[Set[Tuple[str, str]], Set[Tuple[str, str]]]:
    my, enemy = set(), set()
    for r in board.routes:
        if r.is_claimed():
            key = tuple(sorted((r.city_a, r.city_b)))
            (my if r.claimed_by == me else enemy).add(key)
    return my, enemy

# ---------------------------------------------------------------------------
# Snapshot utilities
# ---------------------------------------------------------------------------

def _make_unknown_pool(active: Player, face_up: list[str], discard: Counter[str], players: List[Player], full: Counter[str]) -> UnknownPoolSnapshot:
    known = Counter(face_up) + discard + Counter(active.hand_counts())
    for p in players:
        if p is not active:
            known.update(p.get_exposed())
    unseen = full - known
    return UnknownPoolSnapshot(counts=unseen, total=sum(unseen.values()))


def _build_snapshot(game: "Game", active: Player, idx: int) -> GameSnapshot:
    hidden = game.deck.hidden_counts()
    market = Counter(game.deck.face_up())
    discard = Counter(game.deck.discard_pile)
    full = hidden + market + discard

    pool = _make_unknown_pool(active, game.deck.face_up(), discard, game.players, full)

    players_ss: Dict[str, PlayerSnapshot] = {
        p.player_id: PlayerSnapshot(
            player_id=p.player_id,
            hand=p.hand_counts(),
            exposed=p.get_exposed(),
            tickets=list(p.tickets),
        )
        for p in game.players
    }

    return GameSnapshot(
        board=game.map,
        deck_face_up=game.deck.face_up(),
        deck_discard=discard,
        unknown_pool=pool,
        players=players_ss,
        turn_index=idx,
    )

# ---------------------------------------------------------------------------
# Game class
# ---------------------------------------------------------------------------

class Game:
    def __init__(self, *, seed: Optional[int] = None):
        self.rng = random.Random(seed)
        self.map = MapGraph()
        self.deck = TrainCardDeck(seed=seed)
        self.ticket_deck = TicketDeck(load_default_tickets(), rng=self.rng)
        self.players: List[Player] = []
        self.turn_index: int = 0
        self.heatmap: Optional[LiveHeatmapRenderer] = None
        self.follow_id: Optional[str] = None

    # ---------------- player helpers ----------------
    def add_player(self, name: str) -> None:
        if any(p.player_id == name for p in self.players):
            raise ValueError("Duplicate player name")
        self.players.append(Player(name))

    # ---------------- setup -------------------------
    def _deal_initial_cards(self):
        for p in self.players:
            p.add_cards([self.deck.draw_face_down() for _ in range(4)])

    def _offer_tickets(self):
        for p in self.players:
            owned = {_key(t) for pl in self.players for t in pl.tickets}
            offers = self.ticket_deck.deal_unique(owned, 3)
            print(f"\n{p.player_id}, choose at least 2 destination tickets:")
            for i, t in enumerate(offers, 1):
                print(f"  {i}) {t.city_a} → {t.city_b} ({t.value} pts)")
            while True:
                raw = input("Keep which? (comma‑separated indices) → ")
                try:
                    idxs = [int(x) for x in raw.split(',') if x.strip()]
                except ValueError:
                    idxs = []
                if len([i for i in idxs if 1 <= i <= 3]) >= 2:
                    break
                print(" ➜ Need at least two valid indices 1‑3.")
            keep = set(idxs)
            for i in keep:
                p.add_ticket(offers[i-1])
            self.ticket_deck.return_tickets([offers[i-1] for i in {1,2,3}-keep])

    def setup(self):
        if len(self.players) < 2:
            raise RuntimeError("Add at least two players first")
        self._deal_initial_cards()
        self._offer_tickets()
        print("\nSetup complete!\n")

    # --------------- turn primitives ---------------
    def current_player(self) -> Player:
        return self.players[self.turn_index % len(self.players)]

    def next_turn(self):
        self.turn_index += 1

    def _draw_phase(self, player: Player):
        for _ in range(2):
            try:
                c = self.deck.draw_face_down()
            except RuntimeError:
                break
            player.add_cards([c])

    def _claim_phase(self, player: Player):
        pass  # TODO integrate strategy

    # ---------------- gameplay loop ----------------
    def play(self, *, max_turns: int = 20):
        cap = self.turn_index + max_turns
        if self.heatmap and self.follow_id is None and self.players:
            self.follow_id = self.players[0].player_id
        while self.turn_index < cap:
            pl = self.current_player()
            self._draw_phase(pl)
            pl.allocate_for_desired_routes(self.map)
            self._claim_phase(pl)
            if self.heatmap and pl.player_id == self.follow_id:
                mine, enemy = _claimed_route_sets(self.map, self.follow_id)
                self.heatmap.update_from_player(pl, enemy_claims=enemy, my_claims=mine)
            self.next_turn()

    # --------------------- CLI ---------------------
    def cli(self):
        print("Ticket‑to‑Ride CLI. Type 'help' for commands.")
        while True:
            try:
                line = input("\n> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nExiting."); break
            if not line:
                continue
            toks = line.split()
            cmd = toks[0]
            # help
            if cmd == "help":
                print(
                    "Commands:\n"
                    "  add <name>                       – add player\n"
                    "  follow <name>                    – follow player\n"
                    "  render <map> <cp.json> [alpha]   – create heat‑map renderer\n"
                    "  setup                            – initial deal\n"
                    "  play [turns]                     – run loop (default 20)\n"
                    "  hand                             – show hands counts\n"
                    "  snapshot                         – print snapshot\n"
                    "  quit                             – exit\n"
                )
            # add
            elif cmd == "add" and len(toks) == 2:
                try:
                    self.add_player(toks[1]); print("Added.")
                except ValueError as e:
                    print(e)
            # follow
            elif cmd == "follow" and len(toks) == 2:
                if toks[1] in {p.player_id for p in self.players}:
                    self.follow_id = toks[1]; print(f"Now following {toks[1]}.")
                else:
                    print("Unknown player.")
            # render
            elif cmd == "render" and 3 <= len(toks) <= 4:
                img, cp = toks[1], toks[2]
                alpha = float(toks[3]) if len(toks) == 4 else 0.6
                try:
                    self.heatmap = LiveHeatmapRenderer(img, control_points_path=cp, background_alpha=alpha)
                    print("Renderer created.")
                except Exception as e:
                    print(f"Renderer error: {e}")
            # setup
            elif cmd == "setup":
                try:
                    self.setup()
                except RuntimeError as e:
                    print(e)
            # play
            elif cmd == "play":
                turns = int(toks[1]) if len(toks) == 2 else 20
                self.play(max_turns=turns)
            # hand
            elif cmd == "hand":
                for p in self.players:
                    print(p.player_id, p.hand_counts())
            # snapshot
            elif cmd == "snapshot":
                snap = _build_snapshot(self, self.current_player(), self.turn_index)
                print(snap)
            # quit
            elif cmd == "quit":
                break
            else:
                print("Unknown command.")
