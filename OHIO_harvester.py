# -*- coding: utf-8 -*-
import requests
from lxml import html
import csv

class OHIO_Parser:
    """Parser / harvester for OHIO results on volunteermatch.org"""
    search_URL = "https://www.volunteermatch.org/search/orgs.jsp?l=Ohio&k=&submitsearch=Search"
    MAIN_SITE_URL = "https://www.volunteermatch.org"
    paginated_searching_url = "https://www.volunteermatch.org/search/orgsch.jsp?aff=&r=region&l=Ohio%2C+USA&o=update&s="
    organization_link_xpath = "//div[@id='maininfo']//div[@class='searchitem']//h3//a/@href"

    def __init__(self):
        self.results_hrefs_list = []
        self.no_of_sites = 419

    def get_result_hrefs_from_single_site(self, url, set_current_site=True):
        """Harvests single paginated websites for urls (hrefs in a tags)"""
        single_website = requests.get(url)
        tree = html.fromstring(single_website.content)
        try:
            if set_current_site: #Prints current site when harvesting (method not needed at that stage)
                print(self.get_current_page_url(tree))
            hrefs_list = tree.xpath(OHIO_Parser.organization_link_xpath)
            return hrefs_list
        except Exception as e:
            print("Something went wrong when harvesting urls from site %s, error: %s" % (url, e))

    def get_result_hrefs_from_ALL_sites(self, check_last_site=False):
        """Iterates over all paginated sites in the specified in init range"""
        for site_no in range(self.no_of_sites):
            url = OHIO_Parser.paginated_searching_url + str(site_no) + "1" # We have to add "1" to url for exact site number
            results_hrefs = self.get_result_hrefs_from_single_site(url) or []
            self.results_hrefs_list.extend(results_hrefs)

            if check_last_site:
                if len(results_hrefs) < 10:
                    break
        print(self.results_hrefs_list)

    def _get_full_url(self, url_postfix):
        """Adds prefix to result url"""
        return self.MAIN_SITE_URL + url_postfix

    def _verify_website_url(self, url):
        """Checks if the website of organizations is right (dummy for now, only checking simple statement)"""
        if "add_admin" in url:
            return ""
        elif isinstance(url,list) and "add_admin" not in url:
            return url[0]
        return ""

    def get_data_from_single_result(self, url): # TODOs: add error handling (when website is not available etc)
        """Harvests single record, fixes url (adds prefix)
        returns tuple with (organization_name, mission_statement, website_url)"""
        full_url = self._get_full_url(url)
        print(full_url)
        tree = html.fromstring(requests.get(full_url).content)
        organization_name = tree.xpath("//li[@class='list_box_name']//span[@class='rwd_display']/text()")[0].encode('utf-8')
        mission_statement = tree.xpath("//span[@id='short_mission']/text()")[0].encode('utf-8')
        website_url = tree.xpath("//div[@class='more_info_col2 left']//section//p//a/@href") or ""
        return (organization_name,mission_statement,self._verify_website_url(website_url))

    def full_websites_data_generator(self):
        """Generator based on harvested previously single record urls"""
        for site in self.results_hrefs_list:
            yield self.get_data_from_single_result(site)

    def CSV_writer(self):
        with open('OHIO_RESULTS3.csv', mode="w") as csv_OHIO_file:
            results_writer = csv.writer(csv_OHIO_file, delimiter='|', quotechar="'", quoting=csv.QUOTE_MINIMAL)
            for elem in self.full_websites_data_generator():
                print(elem)
                results_writer.writerow(elem)

    def get_number_of_sites(self, tree):        # draft
        """We should get number of elements as str (later we have to divide by no of elements per site to get number
            of sites)"""
        return tree.xpath("//p[@class='descriptor left']/text()").split("or",1)[1].strip() # We should get number of elements as str (la

    def get_current_page_url(self, tree):       # draft
        """Method gather information about current page (we can use that for traverse on available websites"""
        return tree.xpath("//div[@class='pagination']//span//text()")

if __name__ == "__main__":
    PARSER = OHIO_Parser()
    PARSER.get_result_hrefs_from_ALL_sites()
    PARSER.CSV_writer()
