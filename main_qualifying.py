import os
import sys
import time

import requests

# Resolve local packages relative to this file, even when launched elsewhere.
try:
    _script_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    _script_dir = os.path.dirname(sys.argv[0]) if sys.argv and sys.argv[0] else os.getcwd()
sys.path.insert(0, os.path.join(_script_dir, "src"))

from clients.openf1 import OpenF1Client
from bronze.extractor.qualifying import RequestQualifying
from bronze.load.table import DatabricksTableLoader
from bronze.storage.volume import DatabricksVolumeStorage


def main() -> None:
    started_at = time.perf_counter()

    print("Iniciando extração Qualifying Bronze...")

    try:
        client = OpenF1Client()
        storage = DatabricksVolumeStorage()
        table_loader = DatabricksTableLoader()
        
        extractor = RequestQualifying(client, storage, table_loader)
        extractor.run_extraction()

    except ValueError as error:
        print(f"Erro de configuração: {error}")
        raise

    except requests.exceptions.RequestException as error:
        print(f"Erro de comunicação com OpenF1 ou Databricks: {error}")
        raise

    else:
        elapsed = time.perf_counter() - started_at
        print(f"Extração Qualifying Bronze concluída em {elapsed:.2f} segundos.")


if __name__ == "__main__":
    main()
