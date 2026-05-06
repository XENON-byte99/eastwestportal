import os
import sys
import django

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from materials.models import Course

courses_data = [
    # Core Courses (Previously added)
    ("EEE 101", "Electrical Circuits I", "3+1=4"),
    ("EEE 102", "Electronic Circuits I", "3+1=4"),
    ("EEE 105", "Computer Programming", "3+1=4"),
    ("EEE 201", "Electrical Circuits II", "3+1=4"),
    ("EEE 202", "Electronic Circuits II", "3+1=4"),
    ("EEE 204", "Numerical Analysis for Electrical Engineering", "3+1=4"),
    ("EEE 205", "Digital Logic Design", "3+1=4"),
    ("EEE 300", "Electrical Services Design", "3+0=3"),
    ("EEE 301", "Electrical Machines", "3+1=4"),
    ("EEE 303", "Signals and Linear Systems", "3+0=3"),
    ("EEE 304", "Electrical Power Systems", "3+1=4"),
    ("EEE 305", "Electromagnetic Fields and Waves", "3+0=3"),
    ("EEE 306", "Fundamentals of Embedded Systems", "3+1=4"),
    ("EEE 307", "Telecommunication Engineering", "3+1=4"),
    ("EEE 308", "Electronic Properties of Materials", "3+0=3"),
    ("EEE 309", "Digital Signal Processing", "3+1=4"),
    ("EEE 402", "Control Systems", "3+1=4"),
    ("EEE 403", "Engineer and Society", ""),

    # New Courses (Electives)
    ("EEE 413", "Fundamentals of Nanotechnology", "3+0=3"),
    ("EEE 414", "Optoelectronics", "3+0=3"),
    ("EEE 415", "Semiconductor Processing and Fabrication", "3+1=4"),
    ("EEE 416", "VLSI Circuits and Systems", "3+1=4"),
    ("EEE 417", "Semiconductor Devices", "3+0=3"),
    ("EEE 418", "Analog Integrated Circuits", "3+1=4"),
    ("EEE 419", "Biomedical Electronics", "3+0=3"),

    ("EEE 421", "RF and Microwave Engineering", "3+1=4"),
    ("EEE 422", "Digital Communications", "3+1=4"),
    ("EEE 423", "Wireless and Mobile Communications", "3+1=4"),
    ("EEE 425", "Digital Image Processing", "3+0=3"),
    ("EEE 426", "Advanced Telecommunication Engineering", "3+0=3"),

    ("EEE 433", "Computer Networks", "3+1=4"),
    ("EEE 434", "Computer Architecture", "3+1=4"),
    ("EEE 435", "Embedded Systems", "3+1=4"),
    ("EEE 436", "Introduction to Machine Learning", "3+0=3"),

    ("EEE 441", "Power Stations", "3+0=3"),
    ("EEE 442", "Switchgear and Protective Relays", "3+1=4"),
    ("EEE 444", "High Voltage Engineering", "3+0=3"),
    ("EEE 445", "Renewable Energy", "3+0=3"),
    ("EEE 446", "Power System Operation and Reliability", "3+0=3"),
    ("EEE 447", "Power Electronics", "3+1=4"),

    ("EEE 450", "Special Topic in Electrical and Electronic Engineering", "3+0=3"),
    ("EEE 490", "Research Project", ""),
]

for code, name, credits in courses_data:
    code = code.replace(" ", "").upper()
    course, created = Course.objects.update_or_create(
        code=code,
        defaults={
            'name': name,
            'credits': credits,
            'department': 'EEE'
        }
    )
    if created:
        print(f"Created course: {code} - {name}")
    else:
        print(f"Updated course: {code} - {name}")

print("Done adding courses.")
