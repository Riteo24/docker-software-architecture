from core.usecases import CreateOrder, GetOrder, CheckHealth
from adapters.http.routes import create_app
from .settings import Settings

def build_repository(settings: Settings):
    if settings.adapter == 'file':
        from adapters.file.repository import CsvOrderRepository
        return CsvOrderRepository(settings.csv_path)
    from adapters.db.repository import PostgresOrderRepository
    return PostgresOrderRepository(settings.db)

repository = build_repository(Settings.from_env())
app = create_app(CreateOrder(repository), GetOrder(repository), CheckHealth(repository))
