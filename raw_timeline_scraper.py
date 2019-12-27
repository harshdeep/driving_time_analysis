import webbrowser
import pyautogui
import pyperclip
import time
from datetime import date
from datetime import timedelta
import os

class RawTimelineScraper:
    # Adjust these constants according to your setup
    base_url = 'https://www.google.com/maps/timeline?hl=en&authuser=0&ei=KFH9XZznC9Lt-gSTorbACg%3A29&ved=1t%3A17706&pb=!1m2!1m1!1s'
    map_rect_on_screen = (534, 134, 1004, 738)
    click_coordinates_on_screen_to_select_all_source = (874, 184)

    def __init__(self, start_date, num_days, base_dir):
        self.startDate = start_date
        self.numDays = num_days
        self.baseDir = base_dir

    def scrape(self):
        self._createDirectories()
        for n in range(self.numDays):
            date = self.startDate + timedelta(n)
            self._scrapeDate(date.strftime("%Y-%m-%d"))

    def _createDirectoryIfAbsent(self, dir):
        if not os.path.exists(dir):
            os.makedirs(dir)

    def _createDirectories(self):
        self._createDirectoryIfAbsent(self.baseDir)
        self._createDirectoryIfAbsent(os.path.join(self.baseDir, 'images'))
        self._createDirectoryIfAbsent(os.path.join(self.baseDir, 'html'))

    def rerun(self):
        for n in range(self.numDays):
            date = self.startDate + timedelta(n)
            self._scrapeDateIfDataAbsent(date.strftime("%Y-%m-%d"))

    def _scrapeDate(self, date_str):
        print('Scraping ' + date_str)
        webbrowser.open_new_tab(RawTimelineScraper.base_url + date_str)
        time.sleep(10)
        self._takeMapScreenshot(self._screenshotFilename(date_str))
        self._saveSource(self._sourceFilename(date_str))

    def _screenshotFilename(self, date_str):
        return self.baseDir + '/images/' + date_str + '.png'

    def _sourceFilename(self, date_str):
        return self.baseDir + '/html/' + date_str

    def _scrapeDateIfDataAbsent(self, date_str):
        if not self._isDataPresent(date_str):
            self._scrapeDate(date_str)

    def _isDataPresent(self, date_str):
        screenshot_filename = self._screenshotFilename(date_str)
        source_filename = self._sourceFilename(date_str)
        return (os.path.exists(screenshot_filename) and (os.path.getsize(screenshot_filename) > 72000) and os.path.exists(source_filename) and (os.path.getsize(source_filename) > 100000))

    def _takeMapScreenshot(self, filename):
        pyautogui.screenshot(imageFilename=filename, region=RawTimelineScraper.map_rect_on_screen)

    def _saveSource(self, filename):
        pyautogui.hotkey('command', 'shift', 'C')
        time.sleep(5)
        pyautogui.click(RawTimelineScraper.click_coordinates_on_screen_to_select_all_source[0], RawTimelineScraper.click_coordinates_on_screen_to_select_all_source[1])
        time.sleep(2)
        self._copyIntoClipboard()
        time.sleep(2)
        s = pyperclip.paste()
        with open(filename, 'w') as f:
            f.write(s)

    def _copyIntoClipboard(self):
        pyautogui.keyDown('command')
        time.sleep(0.5)
        pyautogui.keyDown('c')
        time.sleep(2)
        pyautogui.keyUp('c')
        pyautogui.keyUp('command')

if __name__ == "__main__":
    print('Starting in a few seconds. Bring Chrome to the front')
    time.sleep(5)
    print('Starting now')
    scraper = RawTimelineScraper(date(2019, 12, 22), 1, '/Users/harshdeep/Downloads/Timeline2')
    scraper.scrape()