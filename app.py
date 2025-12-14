from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import os
from datetime import datetime
import pandas as pd
import io
from flask import send_file


app = Flask(__name__)
app.secret_key = 'dev-secret-key'

# ---------------- CONFIG ----------------
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processing'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

# ---------------- DATA ----------------
# Initial sample data
districts_data = [
    {
        'id': 1,
        'name': 'Rajanpur',
        'province': 'Punjab',
        'population': 150000,
        'houses': 5000,
        'casualties': 25,
        'date': '2024-08-15',
        'severity': 'High',
        'families': 5000
    },
    {
        'id': 2,
        'name': 'Dadu',
        'province': 'Sindh',
        'population': 200000,
        'houses': 8000,
        'casualties': 40,
        'date': '2024-08-20',
        'severity': 'Critical',
        'families': 8000
    },
]

# Global variable to track next ID
next_id = 3

# ---------------- CSV PROCESSING FUNCTIONS ----------------

def validate_csv(file_path):
    """Check if the CSV file has all required columns and valid data"""
    try:
        if not os.path.exists(file_path):
            return False, "File does not exist"
        
        data = pd.read_csv(file_path)
        
        if data.empty:
            return False, "CSV file is empty"
        
        # Check for required columns
        required_columns = ['District', 'Affected_Population', 'Severity_Level', 'Displaced_Families']
        missing_columns = [col for col in required_columns if col not in data.columns]
        
        if missing_columns:
            return False, f"Missing columns: {', '.join(missing_columns)}"
        
        # Validate numeric columns
        try:
            data['Affected_Population'] = pd.to_numeric(data['Affected_Population'], errors='coerce')
            if data['Affected_Population'].isna().any():
                return False, "Affected_Population must contain valid numbers only"
        except Exception as e:
            return False, f"Error in Affected_Population column: {str(e)}"
        
        try:
            data['Displaced_Families'] = pd.to_numeric(data['Displaced_Families'], errors='coerce')
            if data['Displaced_Families'].isna().any():
                return False, "Displaced_Families must contain valid numbers only"
        except Exception as e:
            return False, f"Error in Displaced_Families column: {str(e)}"
        
        # Validate severity levels
        valid_levels = ['Low', 'Medium', 'High', 'Critical']
        invalid_levels = []
        for idx, level in enumerate(data['Severity_Level']):
            if pd.isna(level) or level not in valid_levels:
                invalid_levels.append(f"Row {idx + 2}: '{level}'")
        
        if invalid_levels:
            return False, f"Invalid Severity_Level values. Must be Low, Medium, High, or Critical"
        
        return True, "CSV is valid"
    
    except Exception as e:
        return False, f"Error reading file: {str(e)}"


def calculate_resources(data):
    """Calculate food packs, tents, medical supplies, water, and blankets needed"""
    
    data['Affected_Population'] = pd.to_numeric(data['Affected_Population'], errors='coerce').fillna(0).astype(int)
    data['Displaced_Families'] = pd.to_numeric(data['Displaced_Families'], errors='coerce').fillna(0).astype(int)
    
    data['Food_Packs'] = 0
    data['Tents'] = 0
    data['Medical_Supplies'] = 0
    data['Water_Bottles'] = 0
    data['Blankets'] = 0
    
    for i in range(len(data)):
        population = data.loc[i, 'Affected_Population']
        families = data.loc[i, 'Displaced_Families']
        severity = data.loc[i, 'Severity_Level']
        
        # Basic calculations
        food = population * 3
        tents = families * 1
        medical = population * 0.15
        water = population * 5
        blankets = population * 1.5
        
        # Severity multipliers
        severity_multipliers = {
            'Low': 1.0,
            'Medium': 1.5,
            'High': 2.0,
            'Critical': 2.5
        }
        
        multiplier = severity_multipliers.get(severity, 1.0)
        
        data.loc[i, 'Food_Packs'] = int(food * multiplier)
        data.loc[i, 'Tents'] = int(tents * multiplier)
        data.loc[i, 'Medical_Supplies'] = int(medical * multiplier)
        data.loc[i, 'Water_Bottles'] = int(water * multiplier)
        data.loc[i, 'Blankets'] = int(blankets * multiplier)
    
    return data


def process_csv(file_path):
    """Read CSV, validate it, and calculate resources"""
    
    is_valid, message = validate_csv(file_path)
    
    if not is_valid:
        return None, message
    
    data = pd.read_csv(file_path)
    processed_data = calculate_resources(data)
    
    return processed_data, "Success"


def update_districts_from_csv(processed_data):
    """Update global districts_data from processed CSV"""
    global districts_data, next_id
    
    # Clear existing data
    districts_data = []
    
    # Convert processed data to districts format
    for idx, row in processed_data.iterrows():
        # Calculate casualties based on severity
        severity_casualties = {
            'Low': int(row['Affected_Population'] * 0.0001),
            'Medium': int(row['Affected_Population'] * 0.0005),
            'High': int(row['Affected_Population'] * 0.001),
            'Critical': int(row['Affected_Population'] * 0.002)
        }
        
        casualties = severity_casualties.get(row['Severity_Level'], 0)
        
        district = {
            'id': next_id,
            'name': row['District'],
            'province': row.get('Province', 'N/A'),  # Optional field
            'population': int(row['Affected_Population']),
            'houses': int(row['Displaced_Families']),
            'casualties': casualties,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'severity': row['Severity_Level'],
            'families': int(row['Displaced_Families']),
            'food_packs': int(row['Food_Packs']),
            'tents': int(row['Tents']),
            'medical_supplies': int(row['Medical_Supplies']),
            'water_bottles': int(row['Water_Bottles']),
            'blankets': int(row['Blankets'])
        }
        
        districts_data.append(district)
        next_id += 1
    
    return True


# ---------------- ROUTES ----------------

@app.route('/')
def index():
    districts = []
    total_population = 0
    total_houses = 0
    total_casualties = 0
    total_relief = 0

    for d in districts_data:
        relief = d['houses'] * 50000

        districts.append({
            'id': d['id'],
            'name': d['name'],
            'population': d['population'],
            'houses': d['houses'],
            'casualties': d['casualties'],
            'relief': relief,
            'date': d['date'],
            'severity': d.get('severity', 'N/A')
        })

        total_population += d['population']
        total_houses += d['houses']
        total_casualties += d['casualties']
        total_relief += relief

    summary = {
        'population': total_population,
        'houses': total_houses,
        'casualties': total_casualties,
        'relief': total_relief
    }

    return render_template(
        'index.html',
        summary=summary,
        districts=districts
    )


@app.route('/districts')
def districts():
    districts = []
    for d in districts_data:
        relief = d['houses'] * 50000
        districts.append({
            'id': d['id'],
            'name': d['name'],
            'population': d['population'],
            'houses': d['houses'],
            'casualties': d['casualties'],
            'relief': relief,
            'date': d['date'],
            'severity': d.get('severity', 'N/A')
        })
    
    return render_template('districts.html', districts=districts)


@app.route('/district/<int:district_id>')
def district_detail(district_id):
    district_found = None
    for d in districts_data:
        if d['id'] == district_id:
            district_found = d
            break
    
    if not district_found:
        flash('District not found', 'error')
        return redirect(url_for('districts'))
    
    relief = district_found['houses'] * 50000
    district = {
        'id': district_found['id'],
        'name': district_found['name'],
        'population': district_found['population'],
        'houses': district_found['houses'],
        'casualties': district_found['casualties'],
        'relief': relief,
        'date': district_found['date'],
        'severity': district_found.get('severity', 'N/A'),
        'food_packs': district_found.get('food_packs', 0),
        'tents': district_found.get('tents', 0),
        'medical_supplies': district_found.get('medical_supplies', 0),
        'water_bottles': district_found.get('water_bottles', 0),
        'blankets': district_found.get('blankets', 0)
    }
    
    return render_template('district-detail.html', district=district)

@app.route('/download-sample-csv')
def download_sample_csv():
    """Generate and download a sample CSV file"""
    
    csv_content = """District,Affected_Population,Severity_Level,Displaced_Families,Province
Rajanpur,150000,High,5000,Punjab
Dadu,200000,Critical,8000,Sindh
Jaffarabad,120000,Medium,4500,Balochistan
Qambar Shahdadkot,90000,High,3200,Sindh
Larkana,110000,High,3800,Sindh
Sukkur,85000,Medium,2800,Sindh
Khairpur,95000,Medium,3100,Sindh
Thatta,75000,Low,2500,Sindh
Jamshoro,65000,Low,2200,Sindh
Shikarpur,80000,Medium,2700,Sindh"""
    
    buffer = io.StringIO()
    buffer.write(csv_content)
    buffer.seek(0)
    
    byte_buffer = io.BytesIO(buffer.getvalue().encode('utf-8'))
    
    return send_file(
        byte_buffer,
        mimetype='text/csv',
        as_attachment=True,
        download_name='sample_flood_data.csv'
    )


@app.route('/upload', methods=['GET', 'POST'])
def upload_page():
    if request.method == 'POST':
        if 'file' not in request.files or request.files['file'].filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)

        file = request.files['file']
        
        if not file.filename.endswith('.csv'):
            flash('Please upload a CSV file', 'error')
            return redirect(request.url)
        
        # Save uploaded file
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Process the CSV
        processed_data, message = process_csv(filepath)
        
        if processed_data is None:
            flash(f'Error processing CSV: {message}', 'error')
            return redirect(request.url)
        
        # Save processed data
        processed_filename = f"processed_{filename}"
        processed_filepath = os.path.join(app.config['PROCESSED_FOLDER'], processed_filename)
        processed_data.to_csv(processed_filepath, index=False)
        
        # Update global districts data
        update_districts_from_csv(processed_data)
        
        flash(f'File uploaded and processed successfully! {len(processed_data)} districts loaded.', 'success')
        return redirect(url_for('index'))

    # Calculate summary for upload page
    total_population = sum(d['population'] for d in districts_data)
    total_houses = sum(d['houses'] for d in districts_data)
    total_casualties = sum(d['casualties'] for d in districts_data)
    total_relief = sum(d['houses'] * 50000 for d in districts_data)
    
    top_districts = []
    for d in districts_data[:10]:  # Show top 10
        relief = d['houses'] * 50000
        top_districts.append({
            'id': d['id'],
            'name': d['name'],
            'population': d['population'],
            'houses': d['houses'],
            'relief': relief
        })

    return render_template(
        'upload.html',
        total_population=total_population,
        total_houses=total_houses,
        total_casualties=total_casualties,
        total_relief=total_relief,
        top_districts=top_districts
    )


# ---------------- API ----------------
@app.route('/api/districts')
def get_districts():
    return jsonify(districts_data)


@app.route('/api/summary')
def get_summary():
    """API endpoint for summary statistics"""
    if not districts_data:
        return jsonify({'error': 'No data available'}), 404
    
    total_population = sum(d['population'] for d in districts_data)
    total_families = sum(d.get('families', d['houses']) for d in districts_data)
    total_food = sum(d.get('food_packs', 0) for d in districts_data)
    total_tents = sum(d.get('tents', 0) for d in districts_data)
    total_medical = sum(d.get('medical_supplies', 0) for d in districts_data)
    total_water = sum(d.get('water_bottles', 0) for d in districts_data)
    total_blankets = sum(d.get('blankets', 0) for d in districts_data)
    
    critical_count = len([d for d in districts_data if d.get('severity') == 'Critical'])
    high_count = len([d for d in districts_data if d.get('severity') == 'High'])
    
    summary = {
        'total_population': total_population,
        'total_families': total_families,
        'total_food_packs': total_food,
        'total_tents': total_tents,
        'total_medical_supplies': total_medical,
        'total_water_bottles': total_water,
        'total_blankets': total_blankets,
        'districts_count': len(districts_data),
        'critical_districts': critical_count,
        'high_severity_districts': high_count
    }
    
    return jsonify(summary)


# ---------------- ERROR HANDLERS ----------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)