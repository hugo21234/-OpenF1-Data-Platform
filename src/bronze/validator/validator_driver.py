from bronze.validator.validator import Validator

class ValidatorDriver(Validator):
    def validate(self, data: list[dict]) -> bool:
        drivers_name_none = {}
        Session_Key_none = {}
        
        if not data:
            print("No data to validate.")
            return False, Session_Key_none, drivers_name_none
                
        for driver in data:
        
            name = driver.get('full_name')  
            driver_number = driver.get('driver_number')
            Session_Key = driver.get('session_key')
            meeting_key = driver.get('meeting_key')
        
            if name is None or not isinstance(name, str) or name.strip() == "":
                        
                print(f"Invalid driver name: {name}")
        
                drivers_name_none['Number'] = driver.get('driver_number')
                drivers_name_none['Session_Key'] = driver.get('session_key')
        
                continue 
                   
            if Session_Key is None or str(Session_Key).strip() == "":
                    
                print(f"Invalid Session_Key: {Session_Key}")
                Session_Key_none['Session_Key'] = driver.get('session_key')
        
                continue
        
            if meeting_key is None or str(meeting_key).strip() == "":
                    
                print(f"Invalid meeting_key: {meeting_key}")
                Session_Key_none['Session_Key'] = driver.get('session_key')
        
                continue
            if driver_number is None or str(driver_number).strip() == "":
                    
                print(f"Invalid driver_number: {driver_number}")
                Session_Key_none['Session_Key'] = driver.get('session_key')
        
                continue   
                    
        if drivers_name_none or Session_Key_none:
            print("Validation failed. Invalid data found.")
            return False, Session_Key_none, drivers_name_none
        
        
        return True, Session_Key_none,drivers_name_none
