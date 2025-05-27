from prometheus_client import Counter, Gauge, Histogram

CARS_ADDED_TOTAL = Counter('cars_added_total', 'Total cars added')
CARS_ADDED_DETAILED = Counter('cars_added_detailed', 'Cars added by model', ['car_model'])
CARS_DELETED = Counter('cars_deleted_total', 'Total cars deleted')
CARS_UPDATED = Counter('cars_updated_total', 'Total cars updated')
CARS_IN_DB = Gauge('cars_in_database', 'Current cars count')
API_LATENCY = Histogram('seller_api_latency_seconds', 'API latency', ['method', 'endpoint'])