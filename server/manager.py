from helper import SQLHandler
import json

class Manager:
    def __init__(self,host='localhost',user='root',password='saransh03sharma',db='server_database'):
        self.sql_handler=SQLHandler(host=host,user=user,password=password,db=db)
        
        
    def Config_database(self,config):
        try:
            
            message, status = self.sql_handler.connect()
            
            if status != 200:
                return message, status

            if isinstance(config, str):
                config = json.loads(config)
            
            elif isinstance(config, dict):
                config = config

               
            if 'shards' not in config:
                return "'shards' field missing in request", 400
        
            schema = config.get('schema', {})
            shards = config.get('shards', [])
            columns = schema.get('columns', [])
            dtypes = schema.get('dtypes', [])
            
            if len(columns) != len(dtypes):
                return "Number of columns and dtypes don't match", 400

            if schema and columns and dtypes and shards:    
                for shard in shards:
                    message, status = self.sql_handler.Create_table(shard, columns, dtypes)
                
                if status == 200:
                    return "Tables created successfully", 200
                else: return message, status
            
            else:
                return "Invalid JSON format", 400
        
        except Exception as e:
            return e, 500
    
    def Copy_database(self,json_data):
        
        try:
            if 'shards' not in json_data:
                return "'shards' field missing in request",400
        
            if not self.sql_handler.connected:
                message, status = self.sql_handler.connect()
                if status != 200:
                    return message, status            

            if isinstance(json_data, str):
                schema = json.loads(json_data)
            
            elif isinstance(json_data, dict):
                schema = json_data
            
            database_copy = {}
            for table_name in schema['shards']:   
                
                table_rows,status = self.sql_handler.Get_table_rows(table_name)        
                database_copy[table_name] = table_rows
            
                if status != 200:
                    message = table_rows
                    return message, status
                
            return database_copy,200

        except Exception as e:

            print(f"Error copying database: {str(e)}")
            return e,500
    
    def Read_database(self,request_json):
        try:
            
            if not self.sql_handler.connected:
                message, status = self.sql_handler.connect()
                if status != 200:
                    return message, status
                
            if 'shard' not in request_json:
                return "'shard' field missing in request", 400
    
            stud_id_obj = request_json["Stud_id"]

            if "low" not in stud_id_obj or "high" not in stud_id_obj:
                return "Both low and high values are required", 400
            
            
            table_name = request_json['shard']
            low, high = stud_id_obj["low"], stud_id_obj["high"]

            table_rows,status = self.sql_handler.Get_range(table_name,low,high, "Stud_id")
            if status==200: 
                print(table_rows,status)               
                return table_rows,200
            else:
                message = table_rows
                
                return message,status
        except Exception as e:
            
            print(f"Error reading database: {str(e)}")
            return e,500
        
    
    def Write_database(self,request_json):
        
        try:
            if not self.sql_handler.connected:
                message, status = self.sql_handler.connect()
                if status != 200:
                    return message, status, -1

            if 'shard' not in request_json:
                return "'shard' field missing in request", 400, -1
        
            tablename = request_json.get("shard")
            data = request_json.get("data")
            curr_idx = request_json.get("curr_idx")
            num_entry = len(data)

            res,status = self.sql_handler.query(f"SELECT COUNT(*) FROM {tablename}")
            
            if status != 200:
                return res, status, -1
            
            valid_idx = res[0][0]

            if(curr_idx!=valid_idx+1):                
                return "Invalid index",400,valid_idx+1
            
            schema = '(Stud_id,Stud_name,Stud_marks)'
            message, status = self.sql_handler.Insert(tablename, data,schema)
            
            if status != 200:    
                return message, status,valid_idx+1
            
            return "Data entries added", 200, valid_idx+num_entry
        
        except Exception as e:
            return e, 500, valid_idx
        
    def Update_database(self,request_json):
       
        try:
            if not self.sql_handler.connected:
                message, status = self.sql_handler.connect()
                if status != 200:
                    return message, status

                
            if 'shard' not in request_json:
                return "'shard' field missing in request", 400
            
            if 'Stud_id' not in request_json:
                return "'Stud_id' field missing in request", 400
            
            if 'data' not in request_json:
                return "'data' field missing in request", 400
            
            stud_id = request_json.get("Stud_id")
            data = request_json.get("data")
            tablename = request_json.get("shard")

            # Check if the 'Stud_id' in the payload matches the 'Stud_id' in the 'data' object
            if stud_id == data["Stud_id"]:
                message, status = self.sql_handler.Update_database(tablename, stud_id,data,'Stud_id')
            
                if status==200:
                    if message == []:
                        return "No matching entries found",404
                    return message,200

                else:                    
                    return  message,status
            else:
                return "Stud_id in 'data' does not match Stud_id in payload", 400

        except Exception as e:            
            return e,500
        
    
    def Delete_database(self,request_json):
        try:
            if not self.sql_handler.connected:
                message, status = self.sql_handler.connect()
                if status != 200:
                    return message, status

            if 'shard' not in request_json:
                return "'shard' field missing in request", 400

            if 'Stud_id' not in request_json:
                return "'Stud_id' field missing in request", 400
            
            stud_id = request_json.get("Stud_id")
            tablename = request_json.get("shard")

            message, status = self.sql_handler.Delete_entry(tablename, stud_id,'Stud_id')
            
            return message,status
        
        except Exception as e:    
            return e,500 
    