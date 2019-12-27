from bs4 import BeautifulSoup
from os import listdir
from os.path import join, isfile
from pytimeparse.timeparse import timeparse
import csv

class TimelineRecord:
    def __init__(self):
        self.drivingDistance = 0
        self.drivingTime = 0
        self.walkingDistance = 0
        self.walkingTime = 0
        self.places = []

    def __str__(self):
        return "Driving Distance: {0}\tDriving Time: {1}\tWalking Distance: {2}\tWalking Time: {3}\nPlaces: {4}".format(
            self.drivingDistance,
            self.drivingTime,
            self.walkingDistance,
            self.walkingTime,
            self.places
        )

class TimelineHTMLParser:
    def __init__(self, filename):
        self.fileName = filename
        self.record = TimelineRecord()
        self.soup = None

    def _parseActivity(self, activity):
        divs = self.soup.find_all('div', attrs={'data-activity':activity})
        if not divs:
            return (0, 0)
        div = divs[0]
        if not div or not div.string or not div.next_sibling.next_sibling or not div.next_sibling.next_sibling.string:
            return (0, 0)
        distance = div.string[:-3] # strip " mi" from the end
        time = timeparse(div.next_sibling.next_sibling.string)/60 #convert string to minutes
        return (distance, time)

    def _parseDriving(self):
        self.record.drivingDistance, self.record.drivingTime = self.parseActivity('29')

    def _parseWalking(self):
        self.record.walkingDistance, self.record.walkingTime = self.parseActivity('2')

    def _parsePlaceVisits(self):
        divs = self.soup.find_all('div', attrs={'class':'place-visit-title', 'jsan':'7.place-visit-title'})
        self.record.places = list(map(lambda x: x.string, divs))

    def parse(self):
        with open(self.fileName, 'r+') as f:
            html = f.read()
        self.soup = BeautifulSoup(html, 'html.parser')
        self._parseDriving()
        self._parseWalking()
        self._parsePlaceVisits()
        return self.record

class TimelineDirParser:
    def __init__(self, dirname):
        self.dirName = dirname
    
    def parse(self):
        files = listdir(self.dirName)
        records = {}
        for f in files:
            filename = join(self.dirName, f)
            if isfile(filename) and not f.startswith('.'):
                print("Filename: {}".format(filename))
                records[f] = TimelineHTMLParser(filename).parse()
        return records

    def parseSingle(self, date_str):
        return {date_str: TimelineHTMLParser(join(self.dirName, date_str)).parse()}

class TimelineRecorder:
    def __init__(self, records, daily_commute_output, daily_places_output):
        self.dailyCommuteOutput = daily_commute_output
        self.dailyPlacesOutput = daily_places_output
        self.records = records

    def record(self):
        self._recordCommutes()
        self._recordPlaceVisits()

    def _recordCommutes(self):
        with open(self.dailyCommuteOutput, 'w', newline='') as commute_file:
            fieldnames = [
                'Date',
                'Driving Distance',
                'Driving Time',
                'Walking Distance',
                'Walking Time',
                'Number of places'
            ]
            commute_writer = csv.DictWriter(commute_file, fieldnames=fieldnames)
            commute_writer.writeheader()
            for i in self.records:
                rec = self.records[i]
                commute_writer.writerow({
                    'Date': i,
                    'Driving Distance': rec.drivingDistance,
                    'Driving Time': rec.drivingTime,
                    'Walking Distance': rec.walkingDistance,
                    'Walking Time': rec.walkingTime,
                    'Number of places': len(rec.places)
                })
    def _recordPlaceVisits(self):
        with open(self.dailyPlacesOutput, 'w', newline='') as places_file:
            fieldnames = [
                'Date',
                'Place'
            ]
            places_writer = csv.DictWriter(places_file, fieldnames=fieldnames)
            places_writer.writeheader()
            for i in self.records:
                rec = self.records[i]
                for place in rec.places:
                    places_writer.writerow({
                        'Date': i,
                        'Place': place
                    })

if __name__ == "__main__":
    parser = TimelineDirParser('/Users/harshdeep/Downloads/Timeline/html/')
    records = parser.parse()
    recorder = TimelineRecorder(records, '/Users/harshdeep/Downloads/Timeline/commute.csv', '/Users/harshdeep/Downloads/Timeline/places.csv')
    recorder.record()