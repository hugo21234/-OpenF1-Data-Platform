from bronze.contracts import DataClient
from bronze.extractor.practice import RequestPractice
from bronze.extractor.qualifying import RequestQualifying
from bronze.extractor.race import RequestRace
from bronze.load.contracts import TableLoader
from bronze.storage.contracts import VolumeStorage


class BronzePipeline(RequestRace):
    def __init__(self, client: DataClient, storage: VolumeStorage,
                 table_loader: TableLoader,
                 endpoints: tuple[str, ...] = RequestRace.SESSION_ENDPOINTS) -> None:
        super().__init__(client, storage, table_loader, endpoints)
        self.extractors = (
            RequestPractice(client, storage, table_loader, endpoints),
            RequestQualifying(client, storage, table_loader, endpoints),
            RequestRace(client, storage, table_loader, endpoints),
        )

    def run_extraction(self) -> None:
        for extractor in self.extractors:
            extractor.run_extraction()
