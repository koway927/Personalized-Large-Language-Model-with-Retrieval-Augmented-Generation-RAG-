import lancedb

def get_all_data_from_table(table_name):
    # Connect to the LanceDB database
    db = lancedb.connect("db")
    
    # Open the specified table
    table = db.open_table(table_name)
    
    # Convert the table to a Pandas DataFrame
    data = table.to_pandas()
    
    return data

# Example usage
if __name__ == "__main__":
    table_name = "personal_info"  
    all_data = get_all_data_from_table(table_name)
    print(all_data)