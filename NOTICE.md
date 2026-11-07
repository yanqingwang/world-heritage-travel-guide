# Data sources, attribution and redistribution

This repository combines data from several sources. The code is MIT-licensed;
the data keeps the terms of its upstream providers. This project is not
affiliated with UNESCO, the Ministry of Culture and Tourism of China,
Wikipedia/Wikimedia, OpenStreetMap, OurAirports or OpenFlights.

## UNESCO World Heritage Centre

- Source: <https://whc.unesco.org/en/list/> (XML editions in English, Chinese,
  French, Spanish, Russian and Arabic).
- Short site names and descriptions are quoted for identification and travel
  guidance. Text and official site images remain © UNESCO. Each record links to
  the corresponding UNESCO page. Do not strip the UNESCO attribution when
  reusing these fields.
- Official site images are hot-linked thumbnails, not bundled assets.

## Ministry of Culture and Tourism of China (文化和旅游部)

- Source: <https://lyfw.mct.gov.cn/site/special/home> (5A scenic-area list).
- Names, addresses, introductions, coordinates, official websites and booking
  links are public government information, reproduced with source links.
- Chinese introductions are the official source text. English introductions
  are Wikipedia text where available, otherwise machine translation (labelled
  in `intro_en_source`).

## Wikipedia and Wikidata

- Wikipedia text: CC BY-SA 4.0. Each record links to the relevant article and
  every derivative introduction keeps its source marker.
- Wikidata: CC0 1.0. Used for identifiers, coordinates, labels, sitelinks and
  Commons image references.
- Wikimedia Commons images: individual licences (CC BY, CC BY-SA, public
  domain, etc.). The licence and author are stored per image in `images[]` and
  displayed in the site and Markdown entries.

## OpenStreetMap

- Source: <https://www.openstreetmap.org/> via the Overpass API.
- © OpenStreetMap contributors. Data is available under the Open Database
  License (ODbL) 1.0: <https://opendatacommons.org/licenses/odbl/>.
- Derived hotel/station/ferry extracts in `data/*.json` are attribution-required
  ODbL data. Keep the OpenStreetMap credit if you redistribute them.

## OurAirports (fallback: OpenFlights)

- Source: <https://ourairports.com/data/> (`data/raw/airports.json`).
- OurAirports data is public domain. Only airports with `scheduled_service=yes`
  and an IATA code are kept, so defunct airports are excluded from the
  nearest-airport result. Coordinates are used only to compute great-circle
  distances.
- The older OpenFlights snapshot (`data/raw/airports.dat`, ODbL) is kept as an
  offline fallback.

## Visa requirements table

- Source: English Wikipedia, "Visa requirements for Chinese citizens"
  (<https://en.wikipedia.org/wiki/Visa_requirements_for_Chinese_citizens>),
  CC BY-SA 4.0.
- The table is a secondary source. Visa rules change frequently; the record
  keeps the retrieval date and links to the source. Always verify with the
  Chinese Ministry of Foreign Affairs / destination government before travel.

## Takedown / corrections

If you are a rights holder and believe an image or text excerpt should not be
included, open an issue with the record ID and source URL. Fields can be
removed or replaced with a link to the original.
