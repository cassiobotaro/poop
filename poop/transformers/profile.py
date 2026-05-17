from poop.types.profile import CProfile, Profile, PStats, SortKey, Stats

NAMESPACE: dict[str, object] = {
    "cProfile": CProfile,
    "profile": CProfile,  # `profile` is the pure-Python flavour; alias here
    "Profile": Profile,
    "pstats": PStats,
    "Stats": Stats,
    "SortKey": SortKey,
}
