## Futbol24 API documentation

Beware that this is unofficial documentation as API for this service is not public. It may be incomplete.

Endpoint address:
[api.futbol24.gluak.com](http://api.futbol24.gluak.com)

# New API
## Implemented
GET /v2/countries
GET /v2/competitions
GET /v2/teams
GET /v2/team/{team_id}/matches
GET /v2/matches/day

## Not implemented
GET /v2/start?platform=android ; Authentication, returns auth token
GET /v2/match/1823730?fields=actions:predictions:statistics
GET /v2/matches/update/1538219619
GET /v2/competition/{competition_id}/fixtures
GET /v2/competition/{competition_id}/notifications/set
GET /v2/competition/{competition_id}/standings
GET /v2/match/{match_id}/actions
GET /v2/match/{match_id}?fields=actions:predictions:statistics
GET /v2/match/{match_id}/notifications/set
GET /v2/match/{match_id}/odds/{publisher}?type=details
GET /v2/match/{match_id}/predictions
GET /v2/match/{match_id}/predictions/add
GET /v2/match/{match_id}/statistics
GET /v2/match/{match_id}/updates
GET /v2/matches/day/{dd}
GET /v2/matches/odds/{publisher}
GET /v2/matches/update/{update}
GET /v2/notifications/push/attach
GET /v2/notifications/push/detach
GET /v2/team/{team_id}/notifications/set

# Old API

https://api.futbol24.gluak.com/start
https://api.futbol24.gluak.com/renew
http://api.futbol24.gluak.com/competitions
http://api.futbol24.gluak.com/league/$ID$/tables

http://api.futbol24.gluak.com/matches/get
http://api.futbol24.gluak.com/matches/team/$ID$
http://api.futbol24.gluak.com/matches/team/$ID$/away
http://api.futbol24.gluak.com/matches/team/$ID$/home
http://api.futbol24.gluak.com/matches/day/$DAY$/?&offset=$OFFSET$
http://api.futbol24.gluak.com/matches/ad/$PROVIDER_ID$/update ; provider_id je cislo, napr. 4

http://api.futbol24.gluak.com/match/$ID$/details

http://api.futbol24.gluak.com/teams/search?q=$SEARCH$
http://api.futbol24.gluak.com/teams/get
http://img.futbol24.gluak.com/team/

http://api.futbol24.gluak.com/odds/$PROVIDER_ID$/match/$MATCH_ID$ ; provider_id je cislo, napr. 4

http://api.futbol24.gluak.com/account/team/$ID$/push
http://api.futbol24.gluak.com/account/team/$ID$/favorite
http://api.futbol24.gluak.com/account/team/$ID$/matches
http://api.futbol24.gluak.com/account/match/$ID$/
http://api.futbol24.gluak.com/account/match/$ID$/push
http://api.futbol24.gluak.com/account/match/$ID$/advice
http://api.futbol24.gluak.com/account/push/register/
http://api.futbol24.gluak.com/account/push/register/GCM-
http://api.futbol24.gluak.com/account/push/type/matches

