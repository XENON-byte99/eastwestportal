import os
import sys
import django

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django.setup()

from materials.models import MaterialType

categories = [
    ("Curriculum", "fa-scroll"),
    ("Lecture Slides", "fa-chalkboard"),
    ("Lecture Videos", "fa-video"),
    ("Lab Reports", "fa-flask"),
    ("Questions", "fa-question-circle"),
    ("Solutions", "fa-check-double"),
    ("PDFs of Books", "fa-book"),
    ("Hand Notes", "fa-pen-fancy"),
    ("Homeworks", "fa-tasks"),
    ("Projects", "fa-project-diagram"),
    ("Open Ended Labs", "fa-flask-vial"),
    ("Courses", "fa-graduation-cap"),
]

print("Populating Material Categories...")
for name, icon in categories:
    obj, created = MaterialType.objects.get_or_create(name=name, defaults={'icon': icon})
    if not created and obj.icon != icon:
        obj.icon = icon
        obj.save()
        print(f"Updated: {name}")
    elif created:
        print(f"Created: {name}")
    else:
        print(f"Exists: {name}")

print("Done!")
