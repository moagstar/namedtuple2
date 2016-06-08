import csv
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from namedtuple3 import namedtuple


class NamedTupleReader:
    """
    Read named tuples from a csv file.
    """

    def __init__(self, *args, **kwargs):
        self._reader = csv.reader(*args, **kwargs)
        self._field_names = next(self._reader)
        self._row_factory = self._init_row_factory()

    def _init_row_factory(self):
        @namedtuple(self._field_names, rename=True)
        def Row():
            pass
        return Row

    def __iter__(self):
        return self

    def next(self):
        return self._row_factory(*next(self._reader))


def example():

    # For example we have some csv data source, we know that there will be a
    # column url, but possible additional columns we do not know about. We want
    # to sort records by url. This could be done with DictReader, but then we
    # create a dict for each row returned, and access the url value by looking
    # up in the dict, which is more expensive and a little less readable, e.g.
    # row.url vs row['url']

    reader = NamedTupleReader(StringIO(
        'url,publication_date,author\n'
        'http://www.pdf995.com/samples/pdf.pdf,2016-05-15,pdf995\n'
        'http://www.publishers.org.uk/_resources/assets/attachment/full/0/2091.pdf,2016-06-03,Example Author\n'
        'http://www.pdf995.com/samples/pdf.pdf,2016-01-15,pdf995\n'
    ))

    result = StringIO()
    writer = csv.writer(result, lineterminator='\n')
    writer.writerows(sorted(reader, key=lambda r: r.url))

    expected = (
        'http://www.pdf995.com/samples/pdf.pdf,2016-05-15,pdf995\n'
        'http://www.pdf995.com/samples/pdf.pdf,2016-01-15,pdf995\n'
        'http://www.publishers.org.uk/_resources/assets/attachment/full/0/2091.pdf,2016-06-03,Example Author\n'
    )
    assert result.getvalue() == expected


if __name__ == '__main__':
    example()