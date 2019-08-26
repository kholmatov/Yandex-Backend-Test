# from app import db
# db.create_all()
import datetime
import re

def checkDate(date_string):
    try:
        match = re.fullmatch(r'\d\d\.\d\d\.\d{4}', date_string)
        if match:
            bDate = datetime.datetime.strptime(date_string, '%d.%m.%Y').date()
            nDate = datetime.datetime.utcnow().date()
            if bDate < nDate:
                return bDate
            else:
                return False
        else:
            return False
    except:
        return False

print("YES" if checkDate('31.02.2019') else "NO")