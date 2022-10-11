 """Batch data processing with memory-efficient chunking."""
import logging
import pandas as pd
from typing import Callable, Optional

logger = logging.getLogger(__name__)

class BatchProcessor:
    """Process large datasets in memory-efficient chunks."""

    def __init__(self, chunk_size: int = 10000):
        self.chunk_size = chunk_size

    def process_file(self, filepath: str, process_fn: Callable,
                     output_path: Optional[str] = None) -> pd.DataFrame:
        """Process a large file in chunks."""
        results = []
        total_rows = 0
        for chunk in pd.read_csv(filepath, chunksize=self.chunk_size):
            processed = process_fn(chunk)
            results.append(processed)
            total_rows += len(chunk)
            logger.debug("Processed chunk: %d rows (total: %d)", len(chunk), total_rows)
        if results:
            final_df = pd.concat(results, ignore_index=True)
            if output_path:
                final_df.to_csv(output_path, index=False)
                logger.info("Saved processed data to %s (%d rows)", output_path, len(final_df))
            return final_df
        return pd.DataFrame()

    def process_dataframe(self, df: pd.DataFrame, process_fn: Callable) -> pd.DataFrame:
        """Process a DataFrame in chunks."""
        results = []
        for i in range(0, len(df), self.chunk_size):
            chunk = df.iloc[i:i + self.chunk_size]
            processed = process_fn(chunk)
            results.append(processed)
        return pd.concat(results, ignore_index=True) if results else df
