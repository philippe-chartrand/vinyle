"""
dates in mpd are too discrete for searching and listing and are often years only.
So we merge dates as years
"""

def group_dates_by_year(items):
    dates = {item['date'][0:4] for item in items}
    return [{'date': date} for date in sorted(dates)]