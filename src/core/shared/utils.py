import datetime


def date_to_string(date: datetime.date) -> str:
    if date is not None:
        return str(date)

def datetime_to_string(date: datetime.datetime) -> str:
    if date is not None:
        return str(date)
    
def string_to_date(string: str) -> datetime.date:
    try:
        date = datetime.datetime.strptime(string, '%Y-%m-%d').date()
        return date
    except Exception as error:
        return None