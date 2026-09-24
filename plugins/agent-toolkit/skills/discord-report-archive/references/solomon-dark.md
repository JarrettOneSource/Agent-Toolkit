# Solomon Dark report archive

Use these existing bindings when the request concerns Solomon's Games reports.
They are defaults for this project; an explicit request takes precedence.

| Resource | Location or ID |
| --- | --- |
| Primary archive | `/home/user/solomon-darker-bug-reports` |
| Windows mirror through WSL | `/mnt/c/Users/User/Documents/Solomon Darker Bug Reports` |
| Windows Explorer path | `C:\Users\User\Documents\Solomon Darker Bug Reports` |
| Guild | Solomon's Games — `725764837015158856` |
| Parent channel | `#darker-beta` — `1537302929420197918` |
| Report thread | Solomon Darker - Web Bug Reports — `1542255501855825960` |
| Thread link | https://discord.com/channels/725764837015158856/1542255501855825960 |
| Soggy's author ID | `229486970047430656` |
| Existing account ID | `600774060439371807` |
| Archive date convention | `America/New_York`; retain source UTC timestamps |

Read the archive index/status for the prior collection boundary and existing
work. The first collection started September 21, 2026; that is history, not a
fixed cutoff for future requests. Resolve the requested reporters and dates
from the current task. Check the live source/account before refreshing Discord
data or applying reactions.

The existing folder layout is the contract for updates. A useful grouping
example is
[`09-coffin-spawn-lag-spike/report.txt`](/home/user/solomon-darker-bug-reports/2026-09-21/09-coffin-spawn-lag-spike/report.txt):
the original report/video and a later `~Save File` message belong to one report,
with both message IDs retained. Both are completion-reaction targets. A general
positive playtest comment retained as context is not another unresolved report.

The Windows mirror is part of this archive's delivery. Keep original report
text, media and save ZIPs intact while adding new groups or evidence. Use fresh
files beneath `_source/` for later snapshots so collection history survives.

For requested Solomon Dark implementation, provide the chosen report directory
to [`solomon-dark-native-parity-re`](../../solomon-dark-native-parity-re/SKILL.md).
That skill owns native recovery, implementation, Mac acceptance and publication.
Evidence intake itself does not start a worker queue or authorize a push.
