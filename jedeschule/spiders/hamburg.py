import xml.etree.ElementTree as ET

from scrapy import Item

from jedeschule.spiders.school_spider import SchoolSpider
from jedeschule.items import School


class HamburgSpider(SchoolSpider):
    name = "hamburg"

    start_urls = [
        "https://geodienste.hamburg.de/HH_WFS_Schulen?SERVICE=WFS&VERSION=1.1.0&REQUEST=GetFeature&typename=de.hh.up:nicht_staatliche_schulen,de.hh.up:staatliche_schulen&srsname=EPSG:4326"
    ]


    def parse(self, response):
        namespaces = {
            "gml": "http://www.opengis.net/gml",
        }

        elem = ET.fromstring(response.body)

        for member in elem:
            data_elem = {}
            for attr in member[0]:
                if attr.tag == "{https://registry.gdi-de.org/id/de.hh.up}the_geom":
                    # This nested entry contains the coordinates that we would like to expand
                    lon, lat = attr.findtext(
                        "gml:Point/gml:pos", namespaces=namespaces
                    ).split(" ")
                    data_elem["lat"] = lat
                    data_elem["lon"] = lon
                    continue
                # strip the namespace before returning
                data_elem[attr.tag.split("}", 1)[1]] = attr.text
            yield data_elem

    @staticmethod
    def normalize(item: Item) -> School:
        city_parts = item.get("adresse_ort").split()
        zip_code, city = city_parts[0], city_parts[1:]
        return School(
            name=item.get("schulname"),
            id="HH-{}".format(item.get("schul_id")),
            address=item.get("adresse_strasse_hausnr"),
            address2="",
            zip=zip_code,
            city=" ".join(city),
            website=item.get("schul_homepage"),
            email=item.get("schul_email"),
            school_type=item.get("schulform"),
            fax=item.get("fax"),
            phone=item.get("schul_telefonnr"),
            director=item.get("name_schulleiter"),
            latitude=item.get("lat"),
            longitude=item.get("lon"),
        )
