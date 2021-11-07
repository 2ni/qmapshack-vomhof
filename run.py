"""
list of all hof: http https://hofsuche.vomhof.ch/api/de/farms|json_pp>vomhof.json
detail of 1 hof: http https://hofsuche.vomhof.ch/api/de/farm/421 |ppj > vomhof-421.json

process to gpx which then can be used in qmapshack as overlay
"""

import gpxpy
import gpxpy.gpx
import json
import requests
import argparse
import sys  # noqa: F401
import os
import re
from datetime import datetime as dt


class Vomhof:

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
        }
        self.datadir = "data"
        self.api = "https://www.hofsuche.vomhof.ch/api/de"
        self.farmurl = "https://hofsuche.vomhof.ch/de/farm"

    @staticmethod
    def print(msg):
        print("\033[38;2;248;248;200m{}\033[0m {}".format(dt.now().strftime("%Y-%m-%d %H:%M:%S"), msg))

    def run(self):
        parser = argparse.ArgumentParser(description="Vomhof Poi generator for qmapshack", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument("--readcache", action="store_true", help="reads data from file")
        parser.add_argument("--writecache", action="store_true", help="writes data to files")
        parser.add_argument("--pretty", action="store_true", help="writes data to files prettyprinted")
        parser.add_argument("--id", type=int, help="only process given farm")
        self.args = parser.parse_args()

        if (self.args.writecache or self.args.readcache) and not os.path.isdir(self.datadir):
            os.mkdir(self.datadir)

        self.xml()

    def get_farm(self, id=None):
        """
        get base data of all farms if id not given else
        get detail data of given farm
        """
        id = str(id) if id else ""
        fn_data = "farm-{}.json".format(id) if id else "farms.json"
        fn_cache = os.path.join(self.datadir, fn_data)
        if (self.args.readcache):
            self.print("reading {} from cache".format(fn_data))
            try:
                with open(fn_cache, "r") as cache:
                    return json.loads(cache.read())
            except IOError:
                self.print("could not read {}. Forcing download".format(fn_data))

        url = os.path.join(self.api, *["farm", id] if id else ["farms"])
        self.print("downloading {} from {}".format(fn_data, url))
        with requests.get(url, headers=self.headers) as response:
            data = response.json()
            if self.args.writecache:
                with open(fn_cache, "w") as cache:
                    cache.write(json.dumps(data, indent=2) if self.args.pretty else json.dumps(data))

            return data

    def farm_to_gpx(self, farm):
        """ farm given as json"""
        waypoint = gpxpy.gpx.GPXWaypoint()
        waypoint.latitude = farm["location"]["lat"]
        waypoint.longitude = farm["location"]["lon"]
        waypoint.name = farm["farmname"]
        waypoint.symbol = "Pin, Red"
        bio = False
        demeter = False
        labels = []
        for label in farm["productionlabels"]:
            labels.append(label["name"])
            if re.search("demeter", label["name"], re.IGNORECASE):
                demeter = True
            elif re.search("bio", label["name"], re.IGNORECASE):
                bio = True

        if demeter:
            waypoint.symbol = "Pin, Green"
        elif bio:
            waypoint.symbol = "Pin, Blue"

        offers = []
        for offer in farm["vomhof"]["offers"]:
            if offer["product"] and offer["product"]["name"]:
                offers.append(offer["product"]["name"])

        paymentmethods = []
        for method in farm["vomhof"]["paymentmethod"]:
            paymentmethods.append(method["name"])

        waypoint.description = "<p>{street}, {zip} {city}</p><p>{labels}</p><p>{offers}</p><p>{shop}</p><p>{paymentmethods}</p><p><a href=\"{url}\">Vomhof</a>&nbsp;|&nbsp;<a href=\"{website}\">Website</a></p>".format(
            street=farm["street"],
            zip=farm["zip"],
            city=farm["city"],
            shop="<div>{}</div".format(farm["vomhof"]["shopdescription"].replace("\n", "</div><div>")),
            offers=",&nbsp;".join(offers),
            labels=",&nbsp;".join(labels),
            paymentmethods=",&nbsp;".join(paymentmethods),
            website=farm["website"],
            url=os.path.join(self.farmurl, farm["id"])
        )
        return waypoint

    def xml(self):
        gpx = gpxpy.gpx.GPX()
        gpx.name = "vomhof"

        farms = self.get_farm()
        total = 1 if self.args.id else farms["aggregations"]["mapLocations"]["doc_count"]
        self.print("generating xml from {} entries".format(total))
        processed = 0
        for data in farms["aggregations"]["mapLocations"]["buckets"]:
            id = data["_id"]
            if (self.args.id and str(self.args.id) != id):
                continue

            self.print("processing farm {} ({}/{})".format(id, processed, total))
            processed += 1
            farm = self.get_farm(id)
            waypoint = self.farm_to_gpx(farm)
            gpx.waypoints.append(waypoint)

        fn_gpx = "vomhof.gpx"
        self.print("writing to {}".format(fn_gpx))
        with open(os.path.join(".", fn_gpx), "w") as fn:
            fn.write(gpx.to_xml())


if __name__ == "__main__":

    vomhof = Vomhof()
    vomhof.print("Hello.")
    vomhof.run()
