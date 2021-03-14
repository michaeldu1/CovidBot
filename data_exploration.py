import pandas as pd

class VaccinationsData:
    def __init__(self):
        self.dataset = pd.read_csv('data/country_vaccinations.csv')
        self.us_vaccinations = self.dataset.loc[self.dataset['country'] == 'United States'].iloc[-1]
        self.date = self.us_vaccinations['date']

    def get_total_vaccinations(self):
      return self.us_vaccinations['total_vaccinations']

    def get_total_vaccinations_100k(self):
      return self.us_vaccinations['total_vaccinations_per_hundred']

    def get_daily_vaccinations(self):
      return self.us_vaccinations['daily_vaccinations']
    
    def get_people_fully_vaccinate(self):
      return self.us_vaccinations['people_fully_vaccinated']

    def get_people_fully_vaccinate_100k(self):
      return self.us_vaccinations['people_fully_vaccinated_per_hundred']

    def get_people_vaccinated(self):
      return self.us_vaccinations['people_vaccinated']

class CaseSurveillanceData:
    def __init__(self):
        self.dataset = pd.read_csv(data_path)

class USData:
    def __init__(self, county, state):
        self.counties_dataset = pd.read_csv('data/USData/us_counties_covid19_daily.csv')
        self.states_dataset = pd.read_csv('data/USData/us_states_covid19_daily.csv')
        self.country_dataset = pd.read_csv('data/USData/us_covid19_daily.csv')
        self.county_data = self.counties_dataset.loc[self.counties_dataset['county'] == county]

class USCountiesData:
    def __init__(self, county, state):
        self.dataset = pd.read_csv('data/us-counties.csv')
        self.county_data = self.dataset.loc[(self.dataset['county'] == county) & (self.dataset['state'] == state)]
    
    def get_cases_trend(self):
        previous = self.county_data.iloc[-1]['cases'] - self.county_data.iloc[-30]['cases']
        print(previous)


    def get_daily_cases(self):
        return self.county_data.iloc[-1]['cases'] - self.county_data.iloc[-2]['cases']
    
    def get_daily_deaths(self):
        return self.county_data.iloc[-1]['deaths'] - self.county_data.iloc[-2]['deaths']

    def get_cumulative_cases(self):
        return self.county_data.iloc[-1]['cases']
    
    def get_cumulative_deaths(self):
        return self.county_data.iloc[-1]['deaths']



if __name__ == "__main__":
    vaccine_dataset = VaccinationsData()
    us_counties = USCounties('Harris', 'Texas')
    print(us_counties.get_cases_trend())
