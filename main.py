import time

import requests

from Request.OpenF1_Client import OpenF1Client
from bronze.extrator.extractor import BronzeExtractor
from bronze.ingestion.storage import DatabricksBronzeStorage


def main() -> None:
    started_at = time.perf_counter()
    print("Iniciando teste da camada Bronze...")

    try:
        bronze_extractor = BronzeExtractor(
            client=OpenF1Client(),
            storage=DatabricksBronzeStorage(),
        )
        bronze_extractor.run_extraction()
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
