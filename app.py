from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

DATA_FILE = 'attendance_data.json'

def load_data():
    """Load attendance data from JSON file"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {'students': [], 'attendance': []}

def save_data(data):
    """Save attendance data to JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/students', methods=['GET', 'POST'])
def manage_students():
    """Get all students or add a new student"""
    data = load_data()
    
    if request.method == 'POST':
        student_name = request.json.get('name', '').strip()
        if student_name and student_name not in data['students']:
            data['students'].append(student_name)
            save_data(data)
            return jsonify({'success': True, 'message': 'Student added successfully'})
        return jsonify({'success': False, 'message': 'Invalid or duplicate student name'}), 400
    
    return jsonify({'students': sorted(data['students'])})

@app.route('/api/attendance', methods=['GET', 'POST'])
def manage_attendance():
    """Get attendance records or mark attendance"""
    data = load_data()
    
    if request.method == 'POST':
        student_name = request.json.get('student')
        status = request.json.get('status')
        date = request.json.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        if student_name not in data['students']:
            return jsonify({'success': False, 'message': 'Invalid student'}), 400
        
        # Remove existing record for this student on this date
        data['attendance'] = [
            record for record in data['attendance'] 
            if not (record['student'] == student_name and record['date'] == date)
        ]
        
        # Add new record
        data['attendance'].append({
            'student': student_name,
            'date': date,
            'status': status
        })
        save_data(data)
        return jsonify({'success': True, 'message': 'Attendance recorded'})
    
    return jsonify({'attendance': data['attendance']})

@app.route('/api/attendance/<student_name>', methods=['GET'])
def get_student_attendance(student_name):
    """Get attendance records for a specific student"""
    data = load_data()
    student_records = [record for record in data['attendance'] if record['student'] == student_name]
    return jsonify({'attendance': student_records})

@app.route('/api/delete-student/<student_name>', methods=['DELETE'])
def delete_student(student_name):
    """Delete a student and their attendance records"""
    data = load_data()
    if student_name in data['students']:
        data['students'].remove(student_name)
        data['attendance'] = [record for record in data['attendance'] if record['student'] != student_name]
        save_data(data)
        return jsonify({'success': True, 'message': 'Student deleted'})
    return jsonify({'success': False, 'message': 'Student not found'}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)