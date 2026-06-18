from __future__ import annotations

import os as _os

# mutmut v3 vs src-layout compatibility shim.
#
# Problem 1 — stats collection:
#   The trampoline in mutants/src/ calls record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
#   where orig.__module__ is 'src.chat.xxx' (because pythonpath=["."] means the module is
#   imported as src.chat.xxx). mutmut's assertion blocks names starting with 'src.'.
#   Fix: strip 'src.' before recording so hit names match the stored mutant names
#   (e.g. 'chat.domain.entities.xǁConversationǁset_title').
#
# Problem 2 — mutant execution:
#   In the child after os.fork(), MUTANT_UNDER_TEST is set to the bare mutant name
#   (e.g. 'chat.domain.entities.xǁ…__mutmut_1') without 'src.' prefix.
#   The trampoline builds prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
#   which IS 'src.chat.domain.entities.xǁ…__mutmut_'. startswith() fails → original
#   code always runs → every mutant survives.
#   Fix: prepend 'src.' to MUTANT_UNDER_TEST so the trampoline prefix check succeeds.

_mutant_under_test = _os.environ.get("MUTANT_UNDER_TEST", "")
if "__mutmut_" in _mutant_under_test and not _mutant_under_test.startswith("src."):
    _os.environ["MUTANT_UNDER_TEST"] = "src." + _mutant_under_test

try:
    import mutmut.__main__ as _mm

    _orig_record = _mm.record_trampoline_hit

    def _record_without_src_prefix(name: str) -> None:
        _orig_record(name.removeprefix("src."))

    _mm.record_trampoline_hit = _record_without_src_prefix
except (ImportError, AttributeError):
    pass
