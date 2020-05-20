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
        self._warned_once = set()
        self._disable_warnings = False

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
                    extrasaction='ignore')
                self._writer.writeheader()

            if to_csv.keys() != self._fieldnames:
                self._warn('Inconsistent TabularInput keys detected. '
                           'CsvOutput keys: {}. '
                           'TabularInput keys: {}. '
                           'Did you change key sets after your first '
                           'logger.log(TabularInput)?'.format(
                               set(self._fieldnames), set(to_csv.keys())))
                # close existing log file
                logFileName = self._log_file.name
                self._log_file.close()
                self._log_file = None
                self._writer = None
                # Read the existing data from the log file
                f = open(logFileName)
                reader = csv.DictReader(f)
                fileFieldNames = reader.fieldnames
                fileData = []
                for row in reader:
                    fileData.append(row)
                reader = None
                f.close()
                # Clear the old file
                f = open(logFileName, 'w+')
                f.close()
                # Create the new file and writer
                self._log_file = open(logFileName, 'w') # copy from simple_outputs.py line 62
                allFieldnames = set(self._fieldnames | to_csv.keys())
                self._fieldnames = allFieldnames
                self._writer = csv.DictWriter(
                    self._log_file,
                    fieldnames=self._fieldnames,
                    restval='',
                    extrasaction='ignore')
                self._writer.writeheader()
                # Write the fileData
                for dataRow in fileData:
                    self._writer.writerow(dataRow)

            self._writer.writerow(to_csv)

            for k in to_csv.keys():
                data.mark(k)
        else:
            raise ValueError('Unacceptable type.')

    def _warn(self, msg):
        """Warns the user using warnings.warn.

        The stacklevel parameter needs to be 3 to ensure the call to logger.log
        is the one printed.
        """
        if not self._disable_warnings and msg not in self._warned_once:
            warnings.warn(
                colorize(msg, 'yellow'), CsvOutputWarning, stacklevel=3)
        self._warned_once.add(msg)
        return msg

    def disable_warnings(self):
        """Disable logger warnings for testing."""
        self._disable_warnings = True


class CsvOutputWarning(UserWarning):
    """Warning class for CsvOutput."""

    pass
