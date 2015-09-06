import datetime

def calculate_start_end_date(start_year=2008, start_month = 2):

    # From the beginning of a month
    start_date = datetime.date(start_year, start_month, 1)
    end_year, end_month = start_year, start_month + 1
        
    if end_month > 12:
        end_year += 1
        end_month = 1
        
    end_date = datetime.date(end_year, end_month, 1) - datetime.timedelta(days=1)
    return start_date, end_date
