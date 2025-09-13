import sys
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QTextEdit, QComboBox, QCheckBox, QGroupBox,
                             QProgressBar, QTabWidget, QMessageBox, QFrame)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
import json
import os


class JobSearchThread(QThread):
    """Worker thread for job searching to prevent UI freezing"""
    update_progress = pyqtSignal(int, str)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, search_params):
        super().__init__()
        self.search_params = search_params
        self.results = []

    def run(self):
        try:
            # Initialize browser
            options = webdriver.ChromeOptions()
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument("--start-maximized")

            # Uncomment the line below if you want to run in headless mode
            # options.add_argument("--headless")

            driver = webdriver.Chrome(options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            self.update_progress.emit(10, "Starting LinkedIn search...")
            results = self.search_linkedin(driver)
            self.results.extend(results)

            driver.quit()
            self.update_progress.emit(100, "Search completed!")
            self.finished.emit(self.results)

        except Exception as e:
            self.error.emit(str(e))

    def search_linkedin(self, driver):
        """Search jobs on LinkedIn based on parameters"""
        results = []
        try:
            # Construct LinkedIn search URL
            keywords = self.search_params['keywords'].replace(' ', '%20')
            location = self.search_params.get('location', '').replace(' ', '%20')

            # Build the search URL with parameters
            url = f"https://www.linkedin.com/jobs/search/?keywords={keywords}"
            if location:
                url += f"&location={location}"

            # Add experience level filter if specified
            experience_map = {
                "Internship": "1",
                "Entry level": "2",
                "Associate": "3",
                "Mid-Senior level": "4",
                "Director": "5",
                "Executive": "6"
            }

            exp_level = self.search_params.get('experience_level')
            if exp_level and exp_level != "Any" and exp_level in experience_map:
                url += f"&f_E={experience_map[exp_level]}"

            # Add remote filter if specified
            if self.search_params.get('remote_only', False):
                url += "&f_WT=2"

            # Navigate to the constructed URL
            self.update_progress.emit(20, "Loading LinkedIn jobs page...")
            driver.get(url)
            time.sleep(3)

            # Scroll to load more jobs
            self.update_progress.emit(40, "Loading more job listings...")
            scroll_pause_time = 2
            screen_height = driver.execute_script("return window.innerHeight")
            scrolls = 5  # Number of times to scroll

            for i in range(scrolls):
                driver.execute_script(f"window.scrollBy(0, {screen_height});")
                time.sleep(scroll_pause_time)
                self.update_progress.emit(40 + int((i / scrolls) * 40), f"Loading jobs... ({i + 1}/{scrolls})")

            # Extract job listings
            self.update_progress.emit(80, "Extracting job information...")
            job_listings = driver.find_elements(By.CSS_SELECTOR, "div.job-search-card")

            for job in job_listings[:20]:  # Limit to 20 results
                try:
                    title = job.find_element(By.CSS_SELECTOR, "h3.base-search-card__title").text
                    company = job.find_element(By.CSS_SELECTOR, "h4.base-search-card__subtitle").text
                    location = job.find_element(By.CSS_SELECTOR, "span.job-search-card__location").text
                    link = job.find_element(By.CSS_SELECTOR, "a.base-card__full-link").get_attribute("href")

                    # Try to get posting date if available
                    try:
                        posted_date = job.find_element(By.CSS_SELECTOR, "time").get_attribute("datetime")
                    except NoSuchElementException:
                        posted_date = "Not specified"

                    results.append({
                        'title': title,
                        'company': company,
                        'location': location,
                        'link': link,
                        'posted_date': posted_date,
                        'source': 'LinkedIn'
                    })
                except NoSuchElementException:
                    continue

        except Exception as e:
            self.error.emit(f"LinkedIn search error: {str(e)}")

        return results


class JobSearchApp(QMainWindow):
    """Main application window for job search tool"""

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.search_thread = None

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("LinkedIn Job Search Tool")
        self.setGeometry(100, 100, 900, 700)

        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Create tabs
        tabs = QTabWidget()
        search_tab = QWidget()
        results_tab = QWidget()

        tabs.addTab(search_tab, "Search")
        tabs.addTab(results_tab, "Results")

        # Setup tabs
        self.setup_search_tab(search_tab)
        self.setup_results_tab(results_tab)

        main_layout.addWidget(tabs)

        # Status bar
        self.status_bar = self.statusBar()

    def setup_search_tab(self, tab):
        """Setup the search tab with input fields"""
        layout = QVBoxLayout(tab)

        # Search parameters group
        search_group = QGroupBox("LinkedIn Search Parameters")
        search_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        search_layout = QVBoxLayout(search_group)

        # Keywords
        keywords_layout = QHBoxLayout()
        keywords_layout.addWidget(QLabel("Job Title/Keywords:"))
        self.keywords_input = QLineEdit()
        self.keywords_input.setPlaceholderText("e.g., Python Developer, Data Scientist")
        keywords_layout.addWidget(self.keywords_input)
        search_layout.addLayout(keywords_layout)

        # Location
        location_layout = QHBoxLayout()
        location_layout.addWidget(QLabel("Location:"))
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("e.g., New York, Remote, India")
        location_layout.addWidget(self.location_input)
        search_layout.addLayout(location_layout)

        # Experience level
        experience_layout = QHBoxLayout()
        experience_layout.addWidget(QLabel("Experience Level:"))
        self.experience_combo = QComboBox()
        self.experience_combo.addItems(
            ["Any", "Internship", "Entry level", "Associate", "Mid-Senior level", "Director", "Executive"])
        experience_layout.addWidget(self.experience_combo)
        search_layout.addLayout(experience_layout)

        # Remote only option
        self.remote_check = QCheckBox("Remote jobs only")
        search_layout.addWidget(self.remote_check)

        layout.addWidget(search_group)

        # Search button
        self.search_button = QPushButton("Search LinkedIn Jobs")
        self.search_button.setStyleSheet(
            "QPushButton { background-color: #0077B5; color: white; font-weight: bold; padding: 10px; }")
        self.search_button.clicked.connect(self.start_search)
        layout.addWidget(self.search_button)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("Ready to search LinkedIn jobs")
        layout.addWidget(self.status_label)

        layout.addStretch()

    def setup_results_tab(self, tab):
        """Setup the results tab"""
        layout = QVBoxLayout(tab)

        # Results display
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        layout.addWidget(self.results_text)

        # Export buttons
        button_layout = QHBoxLayout()
        self.export_txt_button = QPushButton("Export as TXT")
        self.export_txt_button.clicked.connect(self.export_txt)
        self.export_json_button = QPushButton("Export as JSON")
        self.export_json_button.clicked.connect(self.export_json)

        button_layout.addWidget(self.export_txt_button)
        button_layout.addWidget(self.export_json_button)
        button_layout.addStretch()

        layout.addLayout(button_layout)

    def start_search(self):
        """Start the job search process"""
        # Get search parameters
        search_params = {
            'keywords': self.keywords_input.text(),
            'location': self.location_input.text(),
            'experience_level': self.experience_combo.currentText(),
            'remote_only': self.remote_check.isChecked()
        }

        if not search_params['keywords']:
            QMessageBox.warning(self, "Warning", "Please enter at least one keyword to search for.")
            return

        # Disable search button during search
        self.search_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_label.setText("Starting LinkedIn search...")

        # Create and start search thread
        self.search_thread = JobSearchThread(search_params)
        self.search_thread.update_progress.connect(self.update_progress)
        self.search_thread.finished.connect(self.search_finished)
        self.search_thread.error.connect(self.search_error)
        self.search_thread.start()

    def update_progress(self, value, message):
        """Update progress bar and status"""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)

    def search_finished(self, results):
        """Handle search completion"""
        self.search_button.setEnabled(True)
        self.status_label.setText(f"Search completed! Found {len(results)} jobs on LinkedIn.")

        # Display results
        self.display_results(results)

        # Store results for export
        self.current_results = results

    def search_error(self, error_message):
        """Handle search errors"""
        self.search_button.setEnabled(True)
        self.status_label.setText("Error occurred during search")
        QMessageBox.critical(self, "Error", f"An error occurred: {error_message}")

    def display_results(self, results):
        """Display search results in the results tab"""
        if not results:
            self.results_text.setHtml("""
                <div style="text-align: center; padding: 50px;">
                    <h2>No jobs found matching your criteria.</h2>
                    <p>Try broadening your search terms or removing some filters.</p>
                </div>
            """)
            return

        html = """
        <div style="font-family: Arial, sans-serif;">
            <h2 style="color: #0077B5;">LinkedIn Job Search Results</h2>
            <p>Found {} jobs matching your criteria:</p>
        """.format(len(results))

        for i, result in enumerate(results, 1):
            # Format the date if available
            date_info = ""
            if result['posted_date'] != "Not specified":
                try:
                    date_obj = datetime.fromisoformat(result['posted_date'].replace('Z', '+00:00'))
                    date_info = f"<br><strong>Posted:</strong> {date_obj.strftime('%Y-%m-%d')}"
                except:
                    date_info = f"<br><strong>Posted:</strong> {result['posted_date']}"

            html += f"""
            <div style="border: 1px solid #ddd; padding: 15px; margin-bottom: 15px; border-radius: 5px; background-color: #f9f9f9;">
                <h3 style="margin-top: 0; color: #0077B5;">{i}. {result['title']}</h3>
                <p><strong>Company:</strong> {result['company']}</p>
                <p><strong>Location:</strong> {result['location']}</p>
                {date_info}
                <p><a href="{result['link']}" style="color: #0077B5; text-decoration: none;">View on LinkedIn →</a></p>
            </div>
            """

        html += "</div>"
        self.results_text.setHtml(html)

    def export_txt(self):
        """Export results to a text file"""
        if not hasattr(self, 'current_results') or not self.current_results:
            QMessageBox.warning(self, "Warning", "No results to export.")
            return

        try:
            filename = f"linkedin_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("LinkedIn Job Search Results\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Search conducted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Keywords: {self.keywords_input.text()}\n")
                f.write(f"Location: {self.location_input.text()}\n")
                f.write(f"Experience Level: {self.experience_combo.currentText()}\n")
                f.write(f"Remote Only: {'Yes' if self.remote_check.isChecked() else 'No'}\n")
                f.write("=" * 50 + "\n\n")

                for i, result in enumerate(self.current_results, 1):
                    f.write(f"{i}. {result['title']}\n")
                    f.write(f"   Company: {result['company']}\n")
                    f.write(f"   Location: {result['location']}\n")
                    f.write(f"   Posted: {result['posted_date']}\n")
                    f.write(f"   Link: {result['link']}\n")
                    f.write("-" * 50 + "\n")

            QMessageBox.information(self, "Success", f"Results exported to {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export: {str(e)}")

    def export_json(self):
        """Export results to a JSON file"""
        if not hasattr(self, 'current_results') or not self.current_results:
            QMessageBox.warning(self, "Warning", "No results to export.")
            return

        try:
            filename = f"linkedin_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            export_data = {
                "search_parameters": {
                    "keywords": self.keywords_input.text(),
                    "location": self.location_input.text(),
                    "experience_level": self.experience_combo.currentText(),
                    "remote_only": self.remote_check.isChecked(),
                    "search_date": datetime.now().isoformat()
                },
                "results": self.current_results
            }

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            QMessageBox.information(self, "Success", f"Results exported to {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export: {str(e)}")


def main():
    """Main function to run the application"""
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle('Fusion')

    # Create and show main window
    window = JobSearchApp()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()