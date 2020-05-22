"""A `dowel.logger.LogOutput` for CSV files."""
import csv
import warnings

from dowel import TabularInput
from dowel.simple_outputs import FileOutput
from dowel.utils import colorize


class CsvOutput(FileOutput):
    """CSV file output for logger.

    :param file_name: The file this output should log to.
    """

    def __init__(self, file_name):
        super().__init__(file_name)
        self._writer = None
        self._fieldnames = None

    @property
    def types_accepted(self):
        """Accept TabularInput objects only."""
        return (TabularInput, )

    def record(self, data, prefix=''):
        """Log tabular data to CSV."""
        if isinstance(data, TabularInput):
            to_csv = data.as_primitive_dict

            if not to_csv.keys() and not self._writer:
                return

            if not self._writer:
                self._fieldnames = set(to_csv.keys())
                self._writer = csv.DictWriter(
                    self._log_file,
                    fieldnames=self._fieldnames,
                    restval='',
                    extrasaction='raise')
                self._writer.writeheader()

            if to_csv.keys() != self._fieldnames:
                # Inconsistent TabularInput keys detected
                # close existing log file
                log_filename = self._log_file.name
                self._log_file.close()
                self._log_file = None
                self._writer = None
                # Read the existing data from the log file
                f = open(log_filename)
                reader = csv.DictReader(f)
                file_fieldnames = reader.fieldnames
                file_data = list(reader)
                reader = None
                f.close()
                # Clear the old file
                f = open(log_filename, 'w+')
                f.close()
                # Create the new file and writer
                self._log_file = open(log_filename, 'w') # copy from simple_outputs.py line 62
                all_fieldnames = set(self._fieldnames | to_csv.keys())
                self._fieldnames = all_fieldnames
                self._writer = csv.DictWriter(
                    self._log_file,
                    fieldnames=self._fieldnames,
                    restval='',
                    extrasaction='ignore')
                self._writer.writeheader()
                # Write the fileData
                for data_row in file_data:
                    self._writer.writerow(data_row)

            self._writer.writerow(to_csv)

            for k in to_csv.keys():
                data.mark(k)
        else:
            raise ValueError('Unacceptable type.')
