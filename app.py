import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

import pandas as pd
import streamlit as st

# --- 1. DATA MODELS ---


@dataclass
class Team:
    id: str
    name: str
    fifa_ranking: int
    flag: str = "🏳️"

    @property
    def display_name(self) -> str:
        return f"{self.flag} {self.name}"


@dataclass
class Match:
    id: str
    home_team: Optional[Team] = None
    away_team: Optional[Team] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    home_penalties: Optional[int] = None
    away_penalties: Optional[int] = None
    is_played: bool = False
    group_id: str = ""
    winner_id: Optional[str] = None
    label: str = ""


@dataclass
class Group:
    id: str
    name: str
    teams: List[Team]


# --- 2. OFFICIAL DATA SEEDING ---

GROUPS_CONFIG: Dict[str, List[Tuple[str, str, int, str]]] = {
    "A": [
        ("MEX", "Mexico", 15, "🇲🇽"),
        ("RSA", "South Africa", 59, "🇿🇦"),
        ("KOR", "South Korea", 22, "🇰🇷"),
        ("CZE", "Czech Republic", 47, "🇨🇿"),
    ],
    "B": [
        ("CAN", "Canada", 38, "🇨🇦"),
        ("BIH", "Bosnia and Herzegovina", 75, "🇧🇦"),
        ("QAT", "Qatar", 35, "🇶🇦"),
        ("SUI", "Switzerland", 15, "🇨🇭"),
    ],
    "C": [
        ("BRA", "Brazil", 5, "🇧🇷"),
        ("MAR", "Morocco", 14, "🇲🇦"),
        ("HAI", "Haiti", 85, "🇭🇹"),
        ("SCO", "Scotland", 51, "🏴󠁧󠁢󠁳󠁣󠁴󠁿"),
    ],
    "D": [
        ("USA", "United States", 11, "🇺🇸"),
        ("PAR", "Paraguay", 56, "🇵🇾"),
        ("AUS", "Australia", 24, "🇦🇺"),
        ("TUR", "Turkey", 26, "🇹🇷"),
    ],
    "E": [
        ("GER", "Germany", 13, "🇩🇪"),
        ("CUW", "Curaçao", 90, "🇨🇼"),
        ("CIV", "Ivory Coast", 38, "🇨🇮"),
        ("ECU", "Ecuador", 30, "🇪🇨"),
    ],
    "F": [
        ("NED", "Netherlands", 7, "🇳🇱"),
        ("JPN", "Japan", 18, "🇯🇵"),
        ("SWE", "Sweden", 28, "🇸🇪"),
        ("TUN", "Tunisia", 41, "🇹🇳"),
    ],
    "G": [
        ("BEL", "Belgium", 10, "🇧🇪"),
        ("EGY", "Egypt", 36, "🇪🇬"),
        ("IRN", "Iran", 20, "🇮🇷"),
        ("NZL", "New Zealand", 91, "🇳🇿"),
    ],
    "H": [
        ("ESP", "Spain", 3, "🇪🇸"),
        ("CPV", "Cape Verde", 65, "🇨🇻"),
        ("KSA", "Saudi Arabia", 56, "🇸🇦"),
        ("URU", "Uruguay", 11, "🇺🇾"),
    ],
    "I": [
        ("FRA", "France", 2, "🇫🇷"),
        ("SEN", "Senegal", 17, "🇸🇳"),
        ("IRQ", "Iraq", 58, "🇮🇶"),
        ("NOR", "Norway", 47, "🇳🇴"),
    ],
    "J": [
        ("ARG", "Argentina", 1, "🇦🇷"),
        ("ALG", "Algeria", 44, "🇩🇿"),
        ("AUT", "Austria", 22, "🇦🇹"),
        ("JOR", "Jordan", 70, "🇯🇴"),
    ],
    "K": [
        ("POR", "Portugal", 6, "🇵🇹"),
        ("COD", "DR Congo", 60, "🇨🇩"),
        ("UZB", "Uzbekistan", 64, "🇺🇿"),
        ("COL", "Colombia", 12, "🇨🇴"),
    ],
    "L": [
        ("ENG", "England", 4, "🏴󠁧󠁢󠁥󠁮󠁧󠁿"),
        ("CRO", "Croatia", 10, "🇭🇷"),
        ("GHA", "Ghana", 64, "🇬🇭"),
        ("PAN", "Panama", 43, "🇵🇦"),
    ],
}

# Eligible third-place group pools for the 8 group winners playing a 3rd-place team in R32
THIRD_PLACE_POOLS: Dict[str, List[str]] = {
    "1E": ["A", "B", "C", "D", "F"],
    "1I": ["C", "D", "F", "G", "H"],
    "1A": ["C", "E", "F", "H", "I"],
    "1L": ["E", "H", "I", "J", "K"],
    "1D": ["B", "E", "F", "I", "J"],
    "1G": ["A", "E", "H", "I", "J"],
    "1B": ["E", "F", "G", "I", "J"],
    "1K": ["D", "E", "I", "J", "L"],
}


def seed_data() -> Tuple[Dict[str, Team], Dict[str, Group], Dict[str, Match]]:
    teams_dict: Dict[str, Team] = {}
    groups: Dict[str, Group] = {}
    matches: Dict[str, Match] = {}
    for gid, t_data in GROUPS_CONFIG.items():
        group_teams = [Team(tid, name, rank, flag) for tid, name, rank, flag in t_data]
        for t in group_teams:
            teams_dict[t.id] = t
        groups[gid] = Group(gid, f"Group {gid}", group_teams)
        for i in range(len(group_teams)):
            for j in range(i + 1, len(group_teams)):
                t1, t2 = group_teams[i], group_teams[j]
                m_id = f"{gid}_{t1.id}_{t2.id}"
                matches[m_id] = Match(m_id, t1, t2, group_id=gid, label=f"Group {gid}")
    return teams_dict, groups, matches


# --- 3. STATE MANAGEMENT ---


def init_state() -> None:
    if "initialized" not in st.session_state:
        teams, groups, matches = seed_data()
        st.session_state.teams = teams
        st.session_state.groups = groups
        st.session_state.matches = matches
        st.session_state.knockout = {
            "R32": [Match(f"R32_{i}", label=f"R32 Match {i + 1}") for i in range(16)],
            "R16": [Match(f"R16_{i}", label=f"R16 Match {i + 1}") for i in range(8)],
            "QF": [Match(f"QF_{i}", label=f"Quarter-final {i + 1}") for i in range(4)],
            "SF": [Match(f"SF_{i}", label=f"Semi-final {i + 1}") for i in range(2)],
            "TP": [Match("TP_0", label="Third Place Playoff")],
            "F": [Match("F_0", label="World Cup Final")],
        }
        st.session_state.initialized = True


def set_match_state(
    m: Match,
    home_score: Optional[int],
    away_score: Optional[int],
    is_played: bool,
    home_pen: Optional[int] = None,
    away_pen: Optional[int] = None,
    winner_id: Optional[str] = None,
) -> None:
    """Updates both the Match object and its corresponding session_state keys."""
    m.home_score = home_score
    m.away_score = away_score
    m.home_penalties = home_pen
    m.away_penalties = away_pen
    m.is_played = is_played
    m.winner_id = winner_id

    st.session_state[f"score_h_{m.id}"] = int(home_score) if home_score is not None else 0
    st.session_state[f"score_a_{m.id}"] = int(away_score) if away_score is not None else 0
    st.session_state[f"pen_h_{m.id}"] = int(home_pen) if home_pen is not None else 0
    st.session_state[f"pen_a_{m.id}"] = int(away_pen) if away_pen is not None else 0
    st.session_state[f"played_{m.id}"] = is_played
    st.session_state[f"winner_{m.id}"] = winner_id


def clear_match_state(m: Match) -> None:
    """Resets a match and its associated session state keys."""
    m.is_played = False
    m.home_score = None
    m.away_score = None
    m.home_penalties = None
    m.away_penalties = None
    m.winner_id = None
    for key_prefix in ["score_h_", "score_a_", "pen_h_", "pen_a_", "played_", "winner_", "ui_pen_h_", "ui_pen_a_"]:
        st.session_state.pop(f"{key_prefix}{m.id}", None)


def sync_state() -> None:
    """Synchronizes Match objects with widget values in st.session_state."""
    # Sync Group Stage
    for m_id, match in st.session_state.matches.items():
        is_played = bool(st.session_state.get(f"played_{m_id}", False))
        match.is_played = is_played
        if is_played:
            h = st.session_state.get(f"score_h_{m_id}")
            a = st.session_state.get(f"score_a_{m_id}")
            match.home_score = int(h) if h is not None else 0
            match.away_score = int(a) if a is not None else 0
            match.winner_id = (
                match.home_team.id
                if match.home_score > match.away_score
                else (match.away_team.id if match.away_score > match.home_score else None)
            )
        else:
            match.home_score = None
            match.away_score = None
            match.winner_id = None

    # Sync Knockout Stage
    for matches in st.session_state.knockout.values():
        for m in matches:
            if not m.home_team or not m.away_team:
                if m.is_played or m.winner_id is not None:
                    clear_match_state(m)
                continue

            is_played = bool(st.session_state.get(f"played_{m.id}", False))
            if not is_played:
                m.is_played = False
                m.home_score = None
                m.away_score = None
                m.home_penalties = None
                m.away_penalties = None
                m.winner_id = None
                continue

            h_raw = st.session_state.get(f"score_h_{m.id}")
            a_raw = st.session_state.get(f"score_a_{m.id}")
            h = int(h_raw) if h_raw is not None else 0
            a = int(a_raw) if a_raw is not None else 0
            m.home_score = h
            m.away_score = a

            if h > a:
                m.home_penalties = None
                m.away_penalties = None
                m.winner_id = m.home_team.id
                m.is_played = True
                st.session_state[f"winner_{m.id}"] = m.winner_id
            elif a > h:
                m.home_penalties = None
                m.away_penalties = None
                m.winner_id = m.away_team.id
                m.is_played = True
                st.session_state[f"winner_{m.id}"] = m.winner_id
            else:
                ph_raw = st.session_state.get(f"pen_h_{m.id}")
                pa_raw = st.session_state.get(f"pen_a_{m.id}")
                ph = int(ph_raw) if ph_raw is not None else 0
                pa = int(pa_raw) if pa_raw is not None else 0
                if ph != pa:
                    m.home_penalties = ph
                    m.away_penalties = pa
                    m.winner_id = m.home_team.id if ph > pa else m.away_team.id
                    m.is_played = True
                    st.session_state[f"winner_{m.id}"] = m.winner_id
                else:
                    # A regulation draw in knockouts requires non-equal penalty scores
                    m.home_penalties = ph
                    m.away_penalties = pa
                    m.is_played = False
                    m.winner_id = None
                    st.session_state[f"played_{m.id}"] = False
                    st.session_state[f"winner_{m.id}"] = None


# --- 4. ENGINE, STANDINGS & CASCADE RESET ---


def calculate_standings(group: Group, matches: Dict[str, Match]) -> pd.DataFrame:
    stats = {
        t.id: {
            "id": t.id,
            "Team": t.display_name,
            "P": 0,
            "W": 0,
            "D": 0,
            "L": 0,
            "GF": 0,
            "GA": 0,
            "GD": 0,
            "Pts": 0,
            "_rank": t.fifa_ranking,
        }
        for t in group.teams
    }

    group_matches = [
        m
        for m in matches.values()
        if m.group_id == group.id and m.is_played and m.home_score is not None and m.away_score is not None
    ]

    for match in group_matches:
        h, a = match.home_team.id, match.away_team.id
        hs, ascore = int(match.home_score), int(match.away_score)
        stats[h]["P"] += 1
        stats[a]["P"] += 1
        stats[h]["GF"] += hs
        stats[h]["GA"] += ascore
        stats[a]["GF"] += ascore
        stats[a]["GA"] += hs
        if hs > ascore:
            stats[h]["W"] += 1
            stats[h]["Pts"] += 3
            stats[a]["L"] += 1
        elif hs < ascore:
            stats[a]["W"] += 1
            stats[a]["Pts"] += 3
            stats[h]["L"] += 1
        else:
            stats[h]["D"] += 1
            stats[a]["D"] += 1
            stats[h]["Pts"] += 1
            stats[a]["Pts"] += 1

    for s in stats.values():
        s["GD"] = s["GF"] - s["GA"]

    # Compute head-to-head tie-breaker metrics among teams with identical (Pts, GD, GF)
    by_primary: Dict[Tuple[int, int, int], List[str]] = {}
    for tid, s in stats.items():
        key = (s["Pts"], s["GD"], s["GF"])
        by_primary.setdefault(key, []).append(tid)

    for s in stats.values():
        s["_h2h_pts"] = 0
        s["_h2h_gd"] = 0
        s["_h2h_gf"] = 0

    for tied_ids in by_primary.values():
        if len(tied_ids) > 1:
            tied_set = set(tied_ids)
            for match in group_matches:
                h, a = match.home_team.id, match.away_team.id
                if h in tied_set and a in tied_set:
                    hs, ascore = int(match.home_score), int(match.away_score)
                    stats[h]["_h2h_gf"] += hs
                    stats[a]["_h2h_gf"] += ascore
                    stats[h]["_h2h_gd"] += hs - ascore
                    stats[a]["_h2h_gd"] += ascore - hs
                    if hs > ascore:
                        stats[h]["_h2h_pts"] += 3
                    elif hs < ascore:
                        stats[a]["_h2h_pts"] += 3
                    else:
                        stats[h]["_h2h_pts"] += 1
                        stats[a]["_h2h_pts"] += 1

    df = pd.DataFrame(list(stats.values())).sort_values(
        by=["Pts", "GD", "GF", "_h2h_pts", "_h2h_gd", "_h2h_gf", "_rank"],
        ascending=[False, False, False, False, False, False, True],
    )
    df = df.drop(columns=["_rank", "_h2h_pts", "_h2h_gd", "_h2h_gf"]).reset_index(drop=True)
    df.insert(0, "Pos", [1, 2, 3, 4])
    return df


def get_third_place_standings(
    groups: Dict[str, Group], matches: Dict[str, Match], teams: Dict[str, Team]
) -> pd.DataFrame:
    """Computes the ranking table of all 12 third-placed teams."""
    rows = []
    for gid, g in groups.items():
        df = calculate_standings(g, matches)
        row = df.iloc[2]
        t = teams[row["id"]]
        rows.append(
            {
                "Group": gid,
                "id": t.id,
                "Team": t.display_name,
                "P": int(row["P"]),
                "W": int(row["W"]),
                "D": int(row["D"]),
                "L": int(row["L"]),
                "GF": int(row["GF"]),
                "GA": int(row["GA"]),
                "GD": int(row["GD"]),
                "Pts": int(row["Pts"]),
                "_rank": t.fifa_ranking,
            }
        )
    thirds_df = pd.DataFrame(rows).sort_values(
        by=["Pts", "GD", "GF", "W", "_rank"],
        ascending=[False, False, False, False, True],
    )
    thirds_df = thirds_df.drop(columns=["_rank"]).reset_index(drop=True)
    thirds_df.insert(0, "Rank", list(range(1, len(thirds_df) + 1)))
    thirds_df["Status"] = ["✅ Qualified" if i < 8 else "❌ Eliminated" for i in range(len(thirds_df))]
    return thirds_df


def assign_best_thirds(
    best_thirds: List[Dict],
) -> Dict[str, Team]:
    """
    Assigns the 8 advancing third-placed teams to their official R32 group-winner opponents
    using backtracking so every slot receives an eligible group from THIRD_PLACE_POOLS.
    """
    slots = list(THIRD_PLACE_POOLS.keys())
    by_group: Dict[str, Team] = {item["group"]: item["team"] for item in best_thirds}
    ordered_groups = [item["group"] for item in best_thirds]
    avail_set = set(ordered_groups)

    def backtrack(idx: int, used: Set[str]) -> Optional[Dict[str, str]]:
        if idx == len(slots):
            return {}
        slot = slots[idx]
        # Prefer in best-third ranking order among eligible groups for this slot
        candidates = [g for g in ordered_groups if g in THIRD_PLACE_POOLS[slot] and g not in used]
        for g in candidates:
            used.add(g)
            res = backtrack(idx + 1, used)
            if res is not None:
                res[slot] = g
                return res
            used.remove(g)
        return None

    solution = backtrack(0, set())
    if solution is not None:
        return {slot: by_group[g] for slot, g in solution.items()}

    # Fallback (unreachable for any 8 of 12 groups, kept for defensive completeness)
    used_fallback: Set[str] = set()
    assigned: Dict[str, Team] = {}
    for slot in slots:
        owner_group = slot[1:]
        for g in ordered_groups:
            if g not in used_fallback and g != owner_group and g in avail_set:
                used_fallback.add(g)
                assigned[slot] = by_group[g]
                break
    return assigned


def _reset_all_knockouts() -> None:
    for matches in st.session_state.knockout.values():
        for m in matches:
            if m.home_team is not None or m.away_team is not None or m.is_played:
                clear_match_state(m)
                m.home_team = None
                m.away_team = None


def _get_match_loser(m: Match) -> Optional[Team]:
    if not m.is_played or not m.winner_id or not m.home_team or not m.away_team:
        return None
    return m.away_team if m.winner_id == m.home_team.id else m.home_team


def update_bracket() -> None:
    all_groups_played = all(m.is_played for m in st.session_state.matches.values())
    if not all_groups_played:
        _reset_all_knockouts()
        return

    all_standings = {
        gid: calculate_standings(g, st.session_state.matches) for gid, g in st.session_state.groups.items()
    }
    winners = {gid: st.session_state.teams[df.iloc[0]["id"]] for gid, df in all_standings.items()}
    runners_up = {gid: st.session_state.teams[df.iloc[1]["id"]] for gid, df in all_standings.items()}

    thirds_df = get_third_place_standings(
        st.session_state.groups, st.session_state.matches, st.session_state.teams
    )
    best_thirds = [
        {"group": row["Group"], "team": st.session_state.teams[row["id"]]}
        for _, row in thirds_df.iloc[:8].iterrows()
    ]
    third_opponents = assign_best_thirds(best_thirds)

    # Official 2026 World Cup R32 Bracket Order (paired sequentially into R16 -> QF -> SF -> Final)
    r32_mappings: List[Tuple[Optional[Team], Optional[Team]]] = [
        # Pathway 1 (Top-Left)
        (winners["E"], third_opponents.get("1E")),  # M74
        (winners["I"], third_opponents.get("1I")),  # M77
        (runners_up["A"], runners_up["B"]),         # M73
        (winners["F"], runners_up["C"]),            # M75
        # Pathway 2 (Bottom-Left)
        (runners_up["K"], runners_up["L"]),         # M83
        (winners["H"], runners_up["J"]),            # M84
        (winners["D"], third_opponents.get("1D")),  # M81
        (winners["G"], third_opponents.get("1G")),  # M82
        # Pathway 3 (Top-Right)
        (winners["C"], runners_up["F"]),            # M76
        (runners_up["E"], runners_up["I"]),         # M78
        (winners["A"], third_opponents.get("1A")),  # M79
        (winners["L"], third_opponents.get("1L")),  # M80
        # Pathway 4 (Bottom-Right)
        (winners["J"], runners_up["H"]),            # M86
        (runners_up["D"], runners_up["G"]),         # M88
        (winners["B"], third_opponents.get("1B")),  # M85
        (winners["K"], third_opponents.get("1K")),  # M87
    ]

    r32 = st.session_state.knockout["R32"]
    for i, (h, a) in enumerate(r32_mappings):
        if r32[i].home_team != h or r32[i].away_team != a:
            clear_match_state(r32[i])
            r32[i].home_team, r32[i].away_team = h, a

    # Cascading propagation across knockout rounds
    def propagate(prev_round: List[Match], curr_round: List[Match]) -> None:
        for i in range(len(curr_round)):
            m1, m2 = prev_round[i * 2], prev_round[i * 2 + 1]
            h = st.session_state.teams.get(m1.winner_id) if (m1.is_played and m1.winner_id) else None
            a = st.session_state.teams.get(m2.winner_id) if (m2.is_played and m2.winner_id) else None
            if curr_round[i].home_team != h or curr_round[i].away_team != a:
                clear_match_state(curr_round[i])
                curr_round[i].home_team, curr_round[i].away_team = h, a

    propagate(r32, st.session_state.knockout["R16"])
    propagate(st.session_state.knockout["R16"], st.session_state.knockout["QF"])
    propagate(st.session_state.knockout["QF"], st.session_state.knockout["SF"])

    sf = st.session_state.knockout["SF"]
    wf_h = st.session_state.teams.get(sf[0].winner_id) if (sf[0].is_played and sf[0].winner_id) else None
    wf_a = st.session_state.teams.get(sf[1].winner_id) if (sf[1].is_played and sf[1].winner_id) else None
    final_match = st.session_state.knockout["F"][0]
    if final_match.home_team != wf_h or final_match.away_team != wf_a:
        clear_match_state(final_match)
        final_match.home_team, final_match.away_team = wf_h, wf_a

    ltp_h = _get_match_loser(sf[0])
    ltp_a = _get_match_loser(sf[1])
    tp_match = st.session_state.knockout["TP"][0]
    if tp_match.home_team != ltp_h or tp_match.away_team != ltp_a:
        clear_match_state(tp_match)
        tp_match.home_team, tp_match.away_team = ltp_h, ltp_a


# --- 5. SIMULATION ENGINE ---


def simulate_match_logic(match: Match) -> Tuple[int, int]:
    diff = match.away_team.fifa_ranking - match.home_team.fifa_ranking
    goal_range = [0, 1, 2, 3, 4, 5]

    def w(adj: int) -> List[float]:
        if adj > 20:
            return [2, 5, 10, 8, 4, 1]
        elif adj > 5:
            return [5, 10, 8, 4, 2, 1]
        elif adj < -20:
            return [15, 5, 1, 0.5, 0.1, 0]
        return [10, 8, 5, 2, 1, 0.5]

    return (
        random.choices(goal_range, weights=w(diff))[0],
        random.choices(goal_range, weights=w(-diff))[0],
    )


def simulate_group_match(m: Match) -> None:
    if not m.home_team or not m.away_team:
        return
    h, a = simulate_match_logic(m)
    winner_id = m.home_team.id if h > a else (m.away_team.id if a > h else None)
    set_match_state(m, h, a, True, None, None, winner_id)


def simulate_knockout(m: Match) -> None:
    if not m.home_team or not m.away_team:
        return
    h, a = simulate_match_logic(m)
    if h == a:
        hp = random.randint(3, 5)
        ap = random.randint(2, 5)
        while hp == ap:
            ap = random.randint(2, 5)
        winner_id = m.home_team.id if hp > ap else m.away_team.id
        set_match_state(m, h, a, True, hp, ap, winner_id)
    else:
        winner_id = m.home_team.id if h > a else m.away_team.id
        set_match_state(m, h, a, True, None, None, winner_id)


def run_full_sim() -> None:
    _reset_all_knockouts()
    for m in st.session_state.matches.values():
        simulate_group_match(m)
    sync_state()
    update_bracket()
    for r in ["R32", "R16", "QF", "SF", "TP", "F"]:
        for m in st.session_state.knockout[r]:
            simulate_knockout(m)
        sync_state()
        update_bracket()


def run_remaining_sim() -> None:
    for m in st.session_state.matches.values():
        if not m.is_played:
            simulate_group_match(m)
    sync_state()
    update_bracket()
    for r in ["R32", "R16", "QF", "SF", "TP", "F"]:
        for m in st.session_state.knockout[r]:
            if m.home_team and m.away_team and not m.is_played:
                simulate_knockout(m)
        sync_state()
        update_bracket()


def run_group_stage_sim(only_remaining: bool = False) -> None:
    if not only_remaining:
        _reset_all_knockouts()
    for m in st.session_state.matches.values():
        if not only_remaining or not m.is_played:
            simulate_group_match(m)
    sync_state()
    update_bracket()


def reset_tournament_cb() -> None:
    for k in list(st.session_state.keys()):
        del st.session_state[k]


def confirm_match_cb(m: Match, is_ko: bool) -> None:
    t1, t2 = m.home_team, m.away_team
    if not t1 or not t2:
        return
    h = int(st.session_state.get(f"score_h_{m.id}", 0) or 0)
    a = int(st.session_state.get(f"score_a_{m.id}", 0) or 0)
    is_draw = h == a
    ph = int(st.session_state.get(f"pen_h_{m.id}", 0) or 0)
    pa = int(st.session_state.get(f"pen_a_{m.id}", 0) or 0)

    if is_ko and is_draw and ph == pa:
        st.session_state[f"err_{m.id}"] = "Penalties cannot end in a draw!"
        return

    st.session_state.pop(f"err_{m.id}", None)
    if is_ko:
        if h > a:
            win_id = t1.id
        elif a > h:
            win_id = t2.id
        else:
            win_id = t1.id if ph > pa else t2.id
        set_match_state(
            m,
            h,
            a,
            True,
            ph if is_draw else None,
            pa if is_draw else None,
            win_id,
        )
    else:
        win_id = t1.id if h > a else (t2.id if a > h else None)
        set_match_state(m, h, a, True, None, None, win_id)
    sync_state()
    update_bracket()


def sim_single_match_cb(m: Match, is_ko: bool) -> None:
    st.session_state.pop(f"err_{m.id}", None)
    if is_ko:
        simulate_knockout(m)
    else:
        simulate_group_match(m)
    sync_state()
    update_bracket()


def reset_single_match_cb(m: Match) -> None:
    st.session_state.pop(f"err_{m.id}", None)
    clear_match_state(m)
    sync_state()
    update_bracket()


def sim_group_cb(gid: str) -> None:
    for m in st.session_state.matches.values():
        if m.group_id == gid:
            simulate_group_match(m)
    sync_state()
    update_bracket()


def reset_group_cb(gid: str) -> None:
    for m in st.session_state.matches.values():
        if m.group_id == gid:
            clear_match_state(m)
    sync_state()
    update_bracket()


def sim_round_cb(rounds_to_sim: List[str]) -> None:
    for rk in rounds_to_sim:
        for m in st.session_state.knockout[rk]:
            if m.home_team and m.away_team and not m.is_played:
                simulate_knockout(m)
    sync_state()
    update_bracket()


# --- 6. UI COMPONENTS ---


def render_match(m: Match, is_ko: bool = False) -> None:
    with st.container(border=True):
        if m.label and is_ko:
            st.caption(m.label)
        c1, c2, c3, c4 = st.columns([5, 2, 2, 5])
        t1, t2 = m.home_team, m.away_team
        with c1:
            t1_label = (
                f"{t1.display_name} <span style='color:gray;font-size:0.8em;'>(#{t1.fifa_ranking})</span>"
                if t1
                else "TBD"
            )
            st.markdown(f"<div style='font-weight: bold; padding-top: 6px;'>{t1_label}</div>", unsafe_allow_html=True)
        with c2:
            h = st.number_input(
                "H",
                min_value=0,
                max_value=15,
                step=1,
                key=f"score_h_{m.id}",
                label_visibility="collapsed",
                disabled=(t1 is None or t2 is None),
            )
        with c3:
            a = st.number_input(
                "A",
                min_value=0,
                max_value=15,
                step=1,
                key=f"score_a_{m.id}",
                label_visibility="collapsed",
                disabled=(t1 is None or t2 is None),
            )
        with c4:
            t2_label = (
                f"<span style='color:gray;font-size:0.8em;'>(#{t2.fifa_ranking})</span> {t2.display_name}"
                if t2
                else "TBD"
            )
            st.markdown(
                f"<div style='font-weight: bold; text-align: right; padding-top: 6px;'>{t2_label}</div>",
                unsafe_allow_html=True,
            )

        if t1 and t2:
            is_draw = h == a
            ph, pa = 0, 0
            if is_ko and is_draw:
                st.caption("⚽ Regulation Draw — Enter Penalty Shootout Score:")
                cp1, cp2 = st.columns(2)
                with cp1:
                    ph = st.number_input(
                        "Home Penalties",
                        min_value=0,
                        max_value=25,
                        step=1,
                        key=f"pen_h_{m.id}",
                        label_visibility="collapsed",
                    )
                with cp2:
                    pa = st.number_input(
                        "Away Penalties",
                        min_value=0,
                        max_value=25,
                        step=1,
                        key=f"pen_a_{m.id}",
                        label_visibility="collapsed",
                    )

            err_msg = st.session_state.pop(f"err_{m.id}", None)
            if err_msg:
                st.error(err_msg)

            if m.is_played:
                status_col, reset_col = st.columns([4, 1])
                with status_col:
                    if is_ko:
                        if h > a:
                            winner = t1
                        elif a > h:
                            winner = t2
                        else:
                            winner = t1 if ph > pa else t2
                        pen_txt = f" ({ph}) : ({pa}) " if h == a else " : "
                        st.markdown(
                            f"<div style='color: #00c853; font-size: 0.9rem; padding-top: 4px;'>"
                            f"✅ <b>{h}{pen_txt}{a}</b> — {winner.display_name} advances</div>",
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            f"<div style='color: #00c853; font-size: 0.9rem; padding-top: 4px;'>"
                            f"✅ Match Completed (<b>{h} : {a}</b>)</div>",
                            unsafe_allow_html=True,
                        )
                with reset_col:
                    st.button(
                        "↺",
                        key=f"rst_{m.id}",
                        help="Reset match",
                        width="stretch",
                        on_click=reset_single_match_cb,
                        args=(m,),
                    )
            else:
                b_col1, b_col2 = st.columns([3, 1])
                with b_col1:
                    st.button(
                        "Confirm",
                        key=f"btn_{m.id}",
                        width="stretch",
                        on_click=confirm_match_cb,
                        args=(m, is_ko),
                    )
                with b_col2:
                    st.button(
                        "🎲",
                        key=f"sim_{m.id}",
                        help="Simulate this match",
                        width="stretch",
                        on_click=sim_single_match_cb,
                        args=(m, is_ko),
                    )


def main() -> None:
    st.set_page_config(page_title="2026 World Cup Simulator", page_icon="🏆", layout="wide")
    init_state()
    sync_state()
    update_bracket()

    st.title("🏆 2026 FIFA World Cup Simulator")

    total_group_matches = len(st.session_state.matches)
    played_group_matches = sum(1 for m in st.session_state.matches.values() if m.is_played)
    all_ko_matches = [m for r in ["R32", "R16", "QF", "SF", "TP", "F"] for m in st.session_state.knockout[r]]
    played_ko_matches = sum(1 for m in all_ko_matches if m.is_played)

    with st.sidebar:
        st.header("⚙️ Tournament Controls")
        st.button(
            "🎲 Simulate All (Reset & Run)",
            width="stretch",
            type="primary",
            on_click=run_full_sim,
        )
        st.button(
            "🤖 Auto-Simulate Remaining",
            width="stretch",
            on_click=run_remaining_sim,
        )
        st.button(
            "⚽ Simulate Group Stage Only",
            width="stretch",
            on_click=run_group_stage_sim,
            args=(False,),
        )
        st.button(
            "🔄 Reset Tournament",
            width="stretch",
            on_click=reset_tournament_cb,
        )

        st.divider()
        st.subheader("📊 Progress")
        st.progress(
            played_group_matches / total_group_matches,
            text=f"Group Stage: {played_group_matches} / {total_group_matches} matches",
        )
        st.progress(
            played_ko_matches / len(all_ko_matches),
            text=f"Knockout Stage: {played_ko_matches} / {len(all_ko_matches)} matches",
        )

    tab_labels = [f"Group {gid}" for gid in st.session_state.groups.keys()] + ["📊 3rd Place Table"]
    g_tabs = st.tabs(tab_labels)

    for i, (gid, group) in enumerate(st.session_state.groups.items()):
        with g_tabs[i]:
            c_t, c_m = st.columns([1.1, 1])
            with c_t:
                st.subheader(f"{group.name} Standings")
                standings_df = calculate_standings(group, st.session_state.matches).drop(columns=["id"])
                st.dataframe(standings_df, hide_index=True, width="stretch")

                gc1, gc2 = st.columns(2)
                with gc1:
                    st.button(
                        f"🎲 Simulate Group {gid}",
                        key=f"sim_grp_{gid}",
                        width="stretch",
                        on_click=sim_group_cb,
                        args=(gid,),
                    )
                with gc2:
                    st.button(
                        f"↺ Reset Group {gid}",
                        key=f"rst_grp_{gid}",
                        width="stretch",
                        on_click=reset_group_cb,
                        args=(gid,),
                    )

            with c_m:
                st.subheader("Fixtures")
                for m in st.session_state.matches.values():
                    if m.group_id == gid:
                        render_match(m, is_ko=False)

    with g_tabs[-1]:
        st.subheader("Ranking of Third-Placed Teams (Top 8 Advance to R32)")
        thirds_df = get_third_place_standings(
            st.session_state.groups, st.session_state.matches, st.session_state.teams
        ).drop(columns=["id"])
        st.dataframe(thirds_df, hide_index=True, width="stretch")

    if played_group_matches == total_group_matches:
        st.divider()
        st.header("🏁 Knockout Stage")
        k_tabs = st.tabs(["Round of 32", "Round of 16", "Quarter-finals", "Semi-finals", "Finals"])
        round_keys = ["R32", "R16", "QF", "SF", "F"]
        for i, r in enumerate(round_keys):
            with k_tabs[i]:
                rc1, rc2 = st.columns([3, 1])
                with rc2:
                    rounds_to_sim = ["TP", "F"] if r == "F" else [r]
                    can_sim_round = any(
                        m.home_team and m.away_team and not m.is_played
                        for rk in rounds_to_sim
                        for m in st.session_state.knockout[rk]
                    )
                    if can_sim_round:
                        st.button(
                            "🎲 Simulate Round",
                            key=f"sim_rnd_{r}",
                            width="stretch",
                            on_click=sim_round_cb,
                            args=(rounds_to_sim,),
                        )

                cols = st.columns(2)
                for idx, m in enumerate(st.session_state.knockout[r]):
                    with cols[idx % 2]:
                        render_match(m, is_ko=True)

                if r == "F":
                    st.write("---")
                    st.subheader("🥉 Third Place Playoff")
                    c_tp = st.columns(2)
                    with c_tp[0]:
                        render_match(st.session_state.knockout["TP"][0], is_ko=True)

                    f = st.session_state.knockout["F"][0]
                    if f.is_played and f.winner_id:
                        champion = st.session_state.teams[f.winner_id]
                        runner_up = _get_match_loser(f)
                        tp_match = st.session_state.knockout["TP"][0]
                        third_place = (
                            st.session_state.teams[tp_match.winner_id]
                            if (tp_match.is_played and tp_match.winner_id)
                            else None
                        )
                        podium_html = (
                            f"<div style='background: linear-gradient(135deg, #ffd700 0%, #ffb300 100%); "
                            f"padding: 24px; border-radius: 12px; margin-top: 16px; text-align: center; color: #111;'>"
                            f"<h1 style='margin: 0; color: #111;'>👑 WORLD CHAMPION: {champion.display_name} 🏆</h1>"
                        )
                        if runner_up:
                            podium_html += f"<p style='font-size: 1.1rem; margin: 8px 0 0 0;'>🥈 Runner-up: <b>{runner_up.display_name}</b>"
                            if third_place:
                                podium_html += f" &nbsp;|&nbsp; 🥉 Third Place: <b>{third_place.display_name}</b>"
                            podium_html += "</p>"
                        podium_html += "</div>"
                        st.markdown(podium_html, unsafe_allow_html=True)
    else:
        st.info(
            f"⚽ Complete the Group Stage ({played_group_matches}/{total_group_matches} matches played) to unlock the Knockout Stage."
        )


if __name__ == "__main__":
    main()
