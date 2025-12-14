import pandas as pd
import os

# Function to check if CSV file is valid
def validate_csv(file_path):
    """Check if the CSV file has all required columns and valid data"""
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            return False, "File does not exist"
        
        # Read the CSV file
        data = pd.read_csv(file_path)
        
        # Check if file is empty
        if data.empty:
            return False, "CSV file is empty"
        
        # List of required columns
        required_columns = ['District', 'Affected_Population', 'Severity_Level', 'Displaced_Families']
        
        # Check if all required columns exist
        missing_columns = []
        for column in required_columns:
            if column not in data.columns:
                missing_columns.append(column)
        
        if missing_columns:
            return False, f"Missing columns: {', '.join(missing_columns)}"
        
        # Check if Affected_Population has numbers only
        try:
            data['Affected_Population'] = pd.to_numeric(data['Affected_Population'], errors='coerce')
            if data['Affected_Population'].isna().any():
                return False, "Affected_Population must contain valid numbers only"
        except Exception as e:
            return False, f"Error in Affected_Population column: {str(e)}"
        
        # Check if Displaced_Families has numbers only
        try:
            data['Displaced_Families'] = pd.to_numeric(data['Displaced_Families'], errors='coerce')
            if data['Displaced_Families'].isna().any():
                return False, "Displaced_Families must contain valid numbers only"
        except Exception as e:
            return False, f"Error in Displaced_Families column: {str(e)}"
        
        # Check if Severity_Level has valid values
        valid_levels = ['Low', 'Medium', 'High', 'Critical']
        invalid_levels = []
        for idx, level in enumerate(data['Severity_Level']):
            if pd.isna(level) or level not in valid_levels:
                invalid_levels.append(f"Row {idx + 2}: '{level}'")
        
        if invalid_levels:
            return False, f"Invalid Severity_Level values. Must be Low, Medium, High, or Critical. Found: {', '.join(invalid_levels[:3])}"
        
        return True, "CSV is valid"
    
    except pd.errors.EmptyDataError:
        return False, "CSV file is empty or corrupted"
    except pd.errors.ParserError:
        return False, "Error parsing CSV file. Please check the file format"
    except Exception as e:
        return False, f"Error reading file: {str(e)}"


# Function to calculate required resources
def calculate_resources(data):
    """Calculate food packs, tents, medical supplies, water, and blankets needed"""
    
    # Ensure numeric columns are properly typed
    data['Affected_Population'] = pd.to_numeric(data['Affected_Population'], errors='coerce').fillna(0).astype(int)
    data['Displaced_Families'] = pd.to_numeric(data['Displaced_Families'], errors='coerce').fillna(0).astype(int)
    
    # Create new columns for resources
    data['Food_Packs'] = 0
    data['Tents'] = 0
    data['Medical_Supplies'] = 0
    data['Water_Bottles'] = 0
    data['Blankets'] = 0
    
    # Calculate resources for each district (row by row)
    for i in range(len(data)):
        population = data.loc[i, 'Affected_Population']
        families = data.loc[i, 'Displaced_Families']
        severity = data.loc[i, 'Severity_Level']
        
        # Basic calculations
        food = population * 3  # 3 meals per person per day
        tents = families * 1  # 1 tent per family
        medical = population * 0.15  # 15% need medical help
        water = population * 5  # 5 bottles per person per day
        blankets = population * 1.5  # 1.5 blankets per person
        
        # Multiply based on severity level
        severity_multipliers = {
            'Low': 1.0,
            'Medium': 1.5,
            'High': 2.0,
            'Critical': 2.5
        }
        
        multiplier = severity_multipliers.get(severity, 1.0)
        
        # Apply multiplier and save to dataframe
        data.loc[i, 'Food_Packs'] = int(food * multiplier)
        data.loc[i, 'Tents'] = int(tents * multiplier)
        data.loc[i, 'Medical_Supplies'] = int(medical * multiplier)
        data.loc[i, 'Water_Bottles'] = int(water * multiplier)
        data.loc[i, 'Blankets'] = int(blankets * multiplier)
    
    return data


# Main function to process the CSV file
def process_csv(file_path):
    """Read CSV, validate it, and calculate resources"""
    
    # Step 1: Validate the CSV
    is_valid, message = validate_csv(file_path)
    
    if not is_valid:
        print(f"Validation Error: {message}")
        return None, message
    
    # Step 2: Read the CSV file
    data = pd.read_csv(file_path)
    
    # Step 3: Calculate resources
    processed_data = calculate_resources(data)
    
    print("CSV processed successfully!")
    return processed_data, "Success"


# Function to get summary statistics
def get_summary(data):
    """Calculate summary statistics from processed data"""
    if data is None or data.empty:
        return None
    
    summary = {
        'total_population': int(data['Affected_Population'].sum()),
        'total_families': int(data['Displaced_Families'].sum()),
        'total_food_packs': int(data['Food_Packs'].sum()),
        'total_tents': int(data['Tents'].sum()),
        'total_medical_supplies': int(data['Medical_Supplies'].sum()),
        'total_water_bottles': int(data['Water_Bottles'].sum()),
        'total_blankets': int(data['Blankets'].sum()),
        'districts_count': len(data),
        'critical_districts': len(data[data['Severity_Level'] == 'Critical']),
        'high_severity_districts': len(data[data['Severity_Level'] == 'High'])
    }
    
    return summary


# Function to save processed data
def save_processed_data(data, output_path):
    """Save processed data to CSV file"""
    try:
        data.to_csv(output_path, index=False)
        return True, f"Data saved successfully to {output_path}"
    except Exception as e:
        return False, f"Error saving file: {str(e)}"


# Example usage
if __name__ == "__main__":
    # Test the processor
    test_file = "sample_flood_data.csv"
    
    if os.path.exists(test_file):
        result, message = process_csv(test_file)
        
        if result is not None:
            print("\n=== Processed Data ===")
            print(result)
            
            print("\n=== Summary Statistics ===")
            summary = get_summary(result)
            for key, value in summary.items():
                print(f"{key}: {value:,}")
            
            # Save processed data
            output_file = "processed_flood_data.csv"
            success, msg = save_processed_data(result, output_file)
            print(f"\n{msg}")
        else:
            print(f"Processing failed: {message}")
    else:
        print(f"Test file '{test_file}' not found")

