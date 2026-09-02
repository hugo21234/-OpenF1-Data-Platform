import os
import sys
import time

import requests

# Ensure src/ is in path when running as a Job (serverless doesn't auto-add it)
# On serverless compute, __file__ is not defined in the exec() context
try:
    _script_dir = os.path.dirname(__file__)
except NameError:
    _script_dir = os.path.dirname(sys.argv[0]) if sys.argv and sys.argv[0] else os.getcwd()
sys.path.insert(0, os.path.join(_script_dir, "src"))

# Auto-configure Databricks credentials and settings for serverless compute
# The bronze code reads these via os.getenv(); on serverless they aren't set by default
try:
    from databricks.sdk.core import Config as _SdkConfig
    _cfg = _SdkConfig()
    _auth = _cfg.authenticate()
    _token = _auth.get("Authorization", "")
    if _token.startswith("Bearer "):
        os.environ.setdefault("access_token", _token[len("Bearer "):])
    os.environ.setdefault("databricks_host", _cfg.host)
except Exception:
    pass  # Fall back to whatever env vars are already set
os.environ.setdefault("warehouse_id", "9a656b2ebd364e50")
os.environ.setdefault("path_volume_databricks", "/Volumes/f1_plataform_data/bronze/raw")
os.environ.setdefault("prefix_databricks_files", "/api/2.0/fs/files")
os.environ.setdefault("prefix_databricks", "/api/2.0/fs/directories")

from clients.openf1 import OpenF1Client
from bronze.extractor.extractor import BronzePipeline
from bronze.load.table import DatabricksTableLoader
from bronze.storage.volume import DatabricksVolumeStorage


def main() -> None:
    started_at = time.perf_counter()

    print("Iniciando teste da camada Bronze...")

    try:
        bronze_pipeline = BronzePipeline(
            client=OpenF1Client(),
            storage=DatabricksVolumeStorage(),
            table_loader=DatabricksTableLoader(),
        )
        bronze_pipeline.run_extraction()

    except ValueError as error:
        print(f"Erro de configuração: {error}")
        raise

    except requests.exceptions.RequestException as error:
        print(f"Erro de comunicação com OpenF1 ou Databricks: {error}")
        raise

    else:
        elapsed = time.perf_counter() - started_at
        print(f"Teste da camada Bronze concluído em {elapsed:.2f} segundos.")


if __name__ == "__main__":
    main()
