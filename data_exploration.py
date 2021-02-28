import pandas as pd

class VaccinationsData:
    def __init__(self, data_path):
        self.dataset = pd.read_csv(data_path)

class CaseSurveillanceData:
    def __init__(self, data_path):
        self.dataset = pd.read_csv(data_path)

class USData:
    def __init__(self, data_path):
        self.dataset = pd.read_csv(data_path)


if __name__ == "__main__":
    vaccine_dataset = VaccinationsData('data/country_vaccinations.csv')
    print(vaccine_dataset.dataset[0])