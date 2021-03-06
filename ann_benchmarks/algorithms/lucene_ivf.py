from __future__ import absolute_import
import array
import sys

from ann_benchmarks.algorithms.base import BaseANN

from py4j.java_collections import ListConverter
from py4j.java_gateway import JavaGateway

class LuceneIVFFlat(BaseANN):
    INDEX_BATCH_SIZE = 200000

    def __init__(self, metric):
        if metric not in ('angular', 'euclidean'):
            raise NotImplementedError(
                "LuceneGraph doesn't support metric %s" % metric)
        self._metric = metric
        self.gateway = JavaGateway()

    def fit(self, X):
        function = 'EUCLIDEAN' if self._metric is 'euclidean' else 'COSINE'
        self.gateway.entry_point.prepareIndex(function)

        start = 0
        while start < X.shape[0]:
            end = min(start + self.INDEX_BATCH_SIZE, X.shape[0])
            batch = self.prepare_vectors(X[start:end])
            self.gateway.entry_point.indexBatch(start, batch)
            start = end

        self.gateway.entry_point.commit()
        self.gateway.entry_point.forceMerge()
        self.gateway.entry_point.openReader()

    def create_java_object(self, numpy_matrix):
        header = array.array('i', list(numpy_matrix.shape))
        body = array.array('f', numpy_matrix.flatten().tolist());
        if sys.byteorder != 'big':
            header.byteswap()
            body.byteswap()
        return bytearray(header.tostring() + body.tostring())

    def query(self, v, n):
        query_vector = self.prepare_vector(v)
        return self.gateway.entry_point.search(query_vector, n, self.nprobe)

    def set_query_arguments(self, nprobe):
        self.nprobe = nprobe
        self.name = 'LuceneIVFFlat(num_probes={} )'.format(nprobe)

    def __str__(self):
        return 'LuceneIVFFlat(numCentroids=4*sqrt(N), iter=10, nprobe={})'.format(self.nprobe)

    def prepare_vectors(self, vectors):
        return self.create_java_object(vectors)

    def prepare_vector(self, vector):
        return ListConverter().convert(vector.tolist(), self.gateway._gateway_client)

