import pickle5 as pickle

class UserInfo:
    def __init__(self):
        self.user_info = self.get_user()
    
    def get_user(self):
        try:
            with open('user_info.pickle', 'rb') as handle:
                user_info = pickle.load(handle)
        except EOFError:
            user_info = {}
            
        return user_info

    def update_user(self, location='', age='', sex=''):
        if location:
            self.user_info['location'] = location
        if age:
            self.user_info['age'] = age
        if sex:
            self.user_info['sex'] = sex

        with open('user_info.pickle', 'wb') as handle:
            pickle.dump(self.user_info, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
    def get_user_location():
        if 'location' in self.user_info:
            return self.user_info['location']
        
        return ''

    def get_user_age():
        if 'age' in self.user_info:
            return self.user_info['age']
        
        return ''

    def get_user_sex():
        if 'sex' in self.user_info:
            return self.user_info['sex']
        
        return ''