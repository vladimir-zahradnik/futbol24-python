## Futbol24 API documentation

Beware that this is unofficial documentation as API for this service is not public. It may be incomplete.

https://api.futbol24.gluak.com/start
https://api.futbol24.gluak.com/renew
http://api.futbol24.gluak.com/competitions
http://api.futbol24.gluak.com/league/$ID$/tables

http://api.futbol24.gluak.com/countries
http://api.futbol24.gluak.com/countries?filter=tables

http://img.futbol24.gluak.com/country/
http://api.futbol24.gluak.com/country/$ID$/teams
http://api.futbol24.gluak.com/country/$ID$/leagues/?filter=tables

http://api.futbol24.gluak.com/matches/get
http://api.futbol24.gluak.com/matches/update
http://api.futbol24.gluak.com/matches/update/${ID}
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



Address:
http://api.futbol24.gluak.com/

AUTH DETAILS:
F24_APP_VERSION: 1.9.1
XUSER_LANGUAGE: slk
User-Agent: Futbol24 1.9.1/26 (innotek GmbH/VirtualBox; OS 23; 1024x720@160; slk)
F24_DEVICE_ID: androidTab
Accept-Encoding: gzip


Minimalny request:
curl --compressed --verbose -H "Accept-Encoding: gzip" --cookie "F24-CC=sk" http://api.futbol24.gluak.com/countries

curl --compressed --verbose -A "Futbol24 1.9.1/26 (innotek GmbH/VirtualBox; OS 23; 1024x720@160; slk)" -H "Content-Type: application/json" -H "F24_APP_VERSION: 1.9.1" -H "XUSER_LANGUAGE: slk" -H "F24_DEVICE_ID: androidTab" -H "Connection: Keep-Alive" -H "Accept-Encoding: gzip" --cookie "F24-CC=sk" http://api.futbol24.gluak.com/countries