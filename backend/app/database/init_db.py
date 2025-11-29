from app.database.database import Base, engine
import importlib
import pkgutil
import app.models

def import_all_models():
    package = app.models
    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        full_module = f"app.models.{module_name}"
        try:
            importlib.import_module(full_module)
        except Exception as e:
            print(f"Failed to import model module {full_module}: {e}")

def init_db():
    print("init_db() Importing model modules...")
    import_all_models()
    print("Creating tables (if not exist)...")
    Base.metadata.create_all(bind=engine)
    print("Database initialization complete.")
