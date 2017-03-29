import csv

import requests
from lxml import html


class MarvelParser:
    """
        allComicsURL = the initial URL of the character/comics to parse through

        yearToStart  = the year from which to select comic series from.
                        Select only series that start after yearToStart.
    """

    def __init__(self,
                 year_to_start=0,
                 all_comics_url='http://marvel.wikia.com/wiki/Spider-Man_Comic_Books'):
        """
            Construct parser that grabs all comics found at all_comics_url that start on or after year_to_start.

            If all_comics_url isn't passed it will parse Spider-Man comics
            If year_to_start isn't passed it will use 0 as default
        """
        self.year_to_start = year_to_start
        self.all_comics_url = all_comics_url
        self.base_url = self.all_comics_url[:self.all_comics_url.rfind("/wiki/")]
        self.characters = []
        self.issues = []

    def csv_save(self, data):
        print("not done yet")
        # if len(data) == 4:
        #    with open("character.csv", 'w') as resultFile:
        #        wr = csv.writer(resultFile, dialect='excel')
        #        wr.writerows(data)
        # elif len(data) == 5:
        #    with open("issue.csv", 'w') as resultFile:
        #        wr = csv.writer(resultFile, dialect='excel')
        #        wr.writerows(data)")

    def data_save(self, data):
        if len(data) == 4:
            self.characters.append(data)
        elif len(data) == 5:
            self.issues.append(data)

    # issueName, issueNum, seriesName, releaseDate, issueID, seriesID, imageURL
    def save_issue_data(self, issue_url):
        """
            Write an issues data as a csv file
    
            format:
            issue_name,issue_num,series_name,release_date,image
        """
        print(issue_url)
        page = requests.get(issue_url)
        tree = html.fromstring(page.content)

        # Issue Name
        issue_name = tree.xpath(
            '//*[@id="mw-content-text"]/table[1]/tr[1]/td/div/table/tr[1]/th/div/b/a/text()')
        if len(issue_name) > 1:
            issue_name = issue_name[0].strip() + ' & ' + issue_name[1].strip()
        elif len(issue_name) == 1:
            issue_name = issue_name[0]
        elif len(issue_name) == 0:
            issue_name = ""

        # Series Name
        series_name = tree.xpath(
            '//*[@id="mw-content-text"]/table[1]/tr[1]/td/div/div[2]/div[1]/a/text()')
        if len(series_name) == 0:
            series_name = \
                tree.xpath(
                    '//*[@id="mw-content-text"]/table[2]/tr[1]/td/div/div[2]/div[1]/a/text()')[
                    0].strip()
        else:
            series_name = series_name[0].strip()
        series_name = series_name.replace('  ', ' ')

        # Image URL
        image_url = tree.xpath(
            '//*[@id="templateimage"]/div/div/a/img/@src')[0]
        image_url = image_url[:image_url.find('.jpg') + 4].strip()

        # Issue Number
        issue_num = tree.xpath(
            '//*[@id="mw-content-text"]/table[1]/tr[1]/td/div/div[2]/div[1]/text()')
        if len(issue_num) == 0:
            issue_num = tree.xpath(
                '//*[@id="mw-content-text"]/table[2]/tr[1]/td/div/div[2]/div[1]/text()')
        issue_num = issue_num[0].strip()
        issue_num = issue_num[issue_num.find('#') + 1:].strip()

        # Release Date
        release_date_xpaths = [
            '//*[@id="mw-content-text"]/table[1]/tr[1]/td/div/div[2]/div[2]/a/text()',
            '//*[@id="mw-content-text"]/table[1]/tr[1]/td/div/div[2]/div[2]/div[4]/a/text()',
            '//*[@id="mw-content-text"]/table[1]/tr[1]/td/div/div[2]/div[2]/div[4]/text()',
            '//*[@id="mw-content-text"]/table[2]/tr[1]/td/div/div[2]/div[2]/div[4]/a/text()']
        release_date = [tree.xpath(currentXpath) for currentXpath in release_date_xpaths if
                        tree.xpath(currentXpath)]
        if len(release_date[0]) > 1:
            release_date = release_date[0][0] + ', ' + release_date[0][1]
        else:
            release_date = release_date[0][0]
        issue_data = [issue_name.replace('\"', ''),
                      issue_num.replace('\"', ''),
                      series_name.replace('\"', ''),
                      release_date,
                      image_url]
        self.data_save(issue_data)
        print(issue_data)

    def save_character_data(self, character_url, index, issueID):
        url = self.base_url + character_url
        page = requests.get(url)
        tree = html.fromstring(page.content)
        # Character Name
        character_name = str(tree.xpath(
            '//*[@id="WikiaPageHeader"]/div/div[1]/h1/text()')[0])
        end = character_name.rfind(' (Earth')
        if end < 0:
            character_name = character_name[:]
        else:
            character_name = character_name[:end]
        # Type of Character
        type_of_char = ""
        if index == 0:
            type_of_char = "Protagonist"
        elif index == 1:
            type_of_char = "Supporting"
        elif index == 2:
            type_of_char = "Antagonist"
        # Earth ID
        earth_id = tree.xpath(
            '//*[@id="mw-content-text"]/div[1]//' +
            'h3[contains(text(),"Universe")]/following-sibling::*/a/text()')
        if (len(earth_id) > 0):
            earth_id = str(earth_id[0])
        else:
            eid_ind = character_url.find('(Earth-')
            if eid_ind >= 0:
                earth_id = character_url[eid_ind + 1:-1]
            else:
                earth_id = ''
        character_data = [character_name, type_of_char, earth_id, str(issueID)]
        # print(character_data[0] + " : " + character_url)
        # print(character_data)
        self.data_save(character_data)
        print(character_data)

    # list of character url
    def parse_characters_data(self, list_of_characters, index, issueID):
        [self.save_character_data(character_url, index, issueID) for character_url in
         list_of_characters]

    # write to character.csv
    # charName, typeOfChar, earthID, issueID, charID
    def parse_characters_url(self, issueID, issue_url):
        """
            Write a character data as a csv file
            example:
    
            charName, typeOfChar, earthID, issueID, charID
        """
        # For each parameter,
        #    save it in the proper column
        print(issue_url)
        page = requests.get(issue_url)
        tree = html.fromstring(page.content)

        featured_character_url = tree.xpath(
            '//div[@id="mw-content-text"]/h2[@id="AppearingHeader1"]/following::' +
            'p[b[contains(text(), "Featured Characters")]]/following::ul[1]/li//' +
            'a[not(contains(@class, "image"))]/@href')
        supporting_character_url = tree.xpath(
            '//div[@id="mw-content-text"]/h2[@id="AppearingHeader1"]/following::' +
            'p[b[contains(text(), "Supporting Characters")]]/following::' +
            'ul[1]//li//a[not(contains(@title, "Appearance"))]/@href')
        antagonist_character_url = tree.xpath(
            '//div[@id="mw-content-text"]/h2[@id="AppearingHeader1"]/following::' +
            'p[b[contains(text(), "Antagonists")]]/following::' +
            'ul[1]//a[not(contains(@title, "Appearance"))]/@href')
        # Make a list of all character url's and create a set of them to remove reoccurences
        # if there are two stories in an issue
        all_types_of_characters = [list(set(url_list)) for url_list in
                                   [featured_character_url, supporting_character_url,
                                    antagonist_character_url]]
        #                         (list_of_url  index)     [list_of_url, list_of_url, list_of_url]
        [self.parse_characters_data(characters, char_type, issueID) for char_type, characters in
         enumerate(all_types_of_characters) if len(characters) > 0]

    def parse_series_data(self):
        """
            Grabs a comic series's data and calls another function to write the data to an excel spreadsheet
        """
        # Go to a series URL
        # For every issue in the series,
        #   click it and parse all data of that issue
        #   save it as a list
        #   pass all data in that issues page to save_series_data funtcion
        valid_series_urls = self.grab_series_url()
        for series_url in valid_series_urls:
            page = requests.get(series_url)
            tree = html.fromstring(page.content)
            home_url = 'http://marvel.wikia.com'
            issue_url_endings = tree.xpath(
                '//*[contains(@id,"gallery")]/div[*]/div[*]/div/b/a/@href')
            issue_urls = [home_url + issue for issue in issue_url_endings]
            # [self.save_issue_data(issue_url) for issue_url in issue_urls]
            [self.parse_characters_url(issueID, issue_url) for issueID, issue_url in
             enumerate(issue_urls, 1)]

    def parse(self):
        self.parse_series_data()

    def grab_series_url(self):
        """
            Returns a list of URLs (list of comic book series) to look in and grab data from.
    
            Grabs the series that start after this MarvelParsers yearToStart year.
        """
        # For every comic visible at the given link
        #   look for series that start on or after year_to_start
        #   add that series URL to the list
        # return that valid_series_urls
        page = requests.get(self.all_comics_url)
        tree = html.fromstring(page.content)

        series_start_dates = tree.xpath(
            '//*[@id="gallery-0"]/div[*]/div[2]/center/i/a[1]/text()')
        series_start_dates = list(map(int, series_start_dates))
        series_urls = tree.xpath(
            '//*[@id="gallery-0"]/div[*]/div[*]/center[i/a[1]/@href]/b/a/@href')
        valid_series_urls = [self.base_url + comic for index, comic in enumerate(series_urls)
                             if series_start_dates[index] >= self.year_to_start]
        return valid_series_urls


# =====================================================================================================================
#   Executable
# =====================================================================================================================

if __name__ == "__main__":
    spiderman = MarvelParser(2014)
    print("All+:\n")
    spiderman.parse()
