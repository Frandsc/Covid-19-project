import dataset
import pandas as pd
from os import listdir, path
from sqlalchemy import types


DBNAME = 'postgres'
DBUSERNAME = 'postgres'
DBPASSWORD = 'work01'

# making sure correct types are used for arguable columns
must_type = {
    'time_series_covid_19_recovered.csv': {
        'Province/State': types.STRINGTYPE
    },
    'time_series_covid_19_confirmed.csv': {
        'Province/State': types.STRINGTYPE
    },
    'time_series_covid_19_deaths.csv': {
        'Province/State': types.STRINGTYPE
    },
    'COVID19_open_line_list.csv': {
        'notes_for_discussion': types.STRINGTYPE,
        'location': types.STRINGTYPE,
        'additional_information': types.STRINGTYPE,
        'symptoms': types.STRINGTYPE,
        'outcome': types.STRINGTYPE,
        'date_death_or_discharge': types.STRINGTYPE,
        'reported_market_exposure': types.STRINGTYPE,
        'chronic_disease': types.STRINGTYPE,
        'data_moderator_initials': types.STRINGTYPE,
        'sequence_available': types.STRINGTYPE
    },
    'COVID19_line_list_data.csv': {
        'symptom': types.STRINGTYPE,
    },
    'time_series_covid_19_confirmed_US.csv': {
        'Admin2': types.STRINGTYPE,
    },
    'time_series_covid_19_deaths_US.csv': {
        'Admin2': types.STRINGTYPE,
    }
}


if __name__ == '__main__':
    # connecting to the database
    db = dataset.connect(f'postgresql://{DBUSERNAME}:{DBPASSWORD}@localhost:5432/{DBNAME}')
    # going through all csv files in dataset folder
    for fname in listdir('dataset'):
        if fname[-4:] == '.csv':
            # some verbosity
            print(f'Processing {fname}...', end=' ')
            # reading file
            df = pd.read_csv(path.join('dataset', fname))
            # converting it to list of dicts
            rows = list(df.T.to_dict().values())
            # selecting a table name
            table = db[fname[:-4]]
            # dropping table if it already exists
            table.drop()
            try:
                # inserting all data from the file
                table.insert_many(rows, types=must_type.get(fname))
            except Exception as e:
                print(type(e), e)
                exit(-1)
            print(f'{len(rows)} rows inserted')
