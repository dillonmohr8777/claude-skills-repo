# Shared core

`alignhcm_core.py` is the single source of truth for the document engine used by
every Align document skill. It is **vendored** into each skill at
`scripts/_core/alignhcm_core.py` rather than imported, because a Claude skill is
uploaded and installed standalone and cannot depend on a sibling.

Vendoring without discipline rots. So each skill's self-test hashes its copy
against `CORE_SHA256` below and fails if they have drifted. To change the core:

1. Edit `_alignhcm-core/alignhcm_core.py`
2. Run `python3 _alignhcm-core/sync_core.py`
3. Run each skill's `scripts/selftest.py`

Never edit a vendored copy directly.
