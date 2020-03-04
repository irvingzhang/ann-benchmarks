from __future__ import absolute_import

from ann_benchmarks.algorithms.lucene_ivf import LuceneIVFFlat

class LuceneGraph(LuceneIVFFlat):
    def __init__(self, metric):
        LuceneIVFFlat.__init__(self, metric)

    def fit(self, X):
        LuceneIVFFlat.fit(self, X)

    def query(self, v, n):
        query_vector = LuceneIVFFlat.prepare_vector(v)
        return self.gateway.entry_point.search(query_vector, n, self.ef)

    def set_query_arguments(self, ef):
        self.ef = ef

    def __str__(self):
        return 'LuceneGraph(M=6, ef_const=50, ef={})'.format(self.ef)
