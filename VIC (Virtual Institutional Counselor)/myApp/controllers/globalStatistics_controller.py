import logging
from myApp.models.globalStatistics_model import (
    get_top_meetings_by_sections,
    get_total_sections_per_year,
    get_top_classes_most_prerequisites,
    get_top_classes_least_offered
)

class GlobalStatisticsController:
    def __init__(self, db_url):
        self.db_url = db_url

    def top_meetings_with_most_sections(self):
        """Get top 5 meetings with the most sections."""
        try:
            meetings = get_top_meetings_by_sections(self.db_url)
            if not meetings:
                raise ValueError("No meetings found with associated sections.")
            return meetings
        except Exception as e:
            logging.error(f"Error in top_meetings_with_most_sections: {e}")
            raise e

    def total_sections_per_year(self):
        """Get total number of sections per year."""
        try:
            logging.info("Starting total_sections_per_year request")
            sections_per_year = get_total_sections_per_year(self.db_url)
            logging.info(f"Retrieved sections per year: {sections_per_year}")
            return sections_per_year
        except Exception as e:
            logging.error(f"Error in total_sections_per_year: {e}")
            raise e

    def top_classes_most_prerequisites(self):
        """Get top 3 classes that appear the most as prerequisites."""
        try:
            classes = get_top_classes_most_prerequisites(self.db_url)
            if not classes:
                raise ValueError("No classes found as prerequisites.")
            return classes
        except Exception as e:
            logging.error(f"Error in top_classes_most_prerequisites: {e}")
            raise e

    def top_classes_least_offered(self):
        """Get top 3 classes that were offered the least."""
        try:
            classes = get_top_classes_least_offered(self.db_url)
            if not classes:
                raise ValueError("No classes found that were offered the least.")
            return classes
        except Exception as e:
            logging.error(f"Error in top_classes_least_offered: {e}")
            raise e
