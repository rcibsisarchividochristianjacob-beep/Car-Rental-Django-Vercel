import os
import shutil
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ocrs.settings')

# --- ANG SOLUSYON PARA SA DATABASE ---
# Kunin ang path ng original db.sqlite3 sa project folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGINAL_DB_PATH = os.path.join(BASE_DIR, 'db.sqlite3')

# Ito ang target path sa /tmp kung saan tayo may write access
TARGET_DB_PATH = os.path.join('/tmp', 'db.sqlite3')

# Kung may db.sqlite3 ka sa repo, kopyahin ito sa /tmp bago mag-start ang Django
if os.path.exists(ORIGINAL_DB_PATH):
    # Kopyahin lang kung wala pa sa /tmp para hindi ma-overwrite palagi (optional check)
    if not os.path.exists(TARGET_DB_PATH):
        shutil.copy2(ORIGINAL_DB_PATH, TARGET_DB_PATH)
        print("SUCCESS: Database copied to /tmp/db.sqlite3")
else:
    print("WARNING: Original database not found in project root!")
# -------------------------------------

application = get_wsgi_application()
app = application
