# Copyright (c) 2020, MD2K Center of Excellence
# All rights reserved.
# Md Azim Ullah (mullah@memphis.edu)
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from pyspark.sql.types import StructField, StructType, DoubleType,MapType, StringType,ArrayType, FloatType, TimestampType, IntegerType
from pyspark.sql.functions import pandas_udf, PandasUDFType
import numpy as np
import pandas as pd
from cerebralcortex.core.datatypes import DataStream
from cerebralcortex.core.metadata_manager.stream.metadata import Metadata, DataDescriptor, \
    ModuleMetadata
import numpy as np
from pyspark.sql import functions as F
from scipy.stats import iqr
from scipy import interpolate, signal
import matplotlib.pyplot as plt
from matplotlib import style
import matplotlib.patches as mpatches
from collections import OrderedDict



import math
def weighted_avg_and_std(values, weights):
    """
    Return the weighted average and standard deviation.

    values, weights -- Numpy ndarrays with the same shape.
    """
    average = np.average(values, weights=weights)
    # Fast and numerically precise:
    variance = np.average((values-average)**2, weights=weights)
    return average, math.sqrt(variance)

def normalize_features(data,
                       lower_percentile=20,
                       higher_percentile=99,
                       minimum_minutes_in_day=60,
                       no_features=11,
                       epsilon = 1e-8,
                       input_feature_array_name='features'):
    data_day = data.withColumn('day',F.date_format('localtime','YYYYMMdd'))
    stream_metadata = data.metadata
    stream_metadata.add_dataDescriptor(
        DataDescriptor()
            .set_name("features_normalized")
            .set_type("array")
            .set_attribute("description","All features normalized daywise"))
    data_day = data_day.withColumn('features_normalized',F.col(input_feature_array_name))
    if 'window' in data.columns:
        data_day = data_day.withColumn('start',F.col('window').start).withColumn('end',F.col('window').end).drop(*['window'])
    schema = data_day._data.schema
    @pandas_udf(schema, PandasUDFType.GROUPED_MAP)
    def normalize_features(a):
        if len(a)<minimum_minutes_in_day:
            return pd.DataFrame([],columns=a.columns)
        quals1 = np.array([1]*a.shape[0])
        feature_matrix = np.array(list(a[input_feature_array_name])).reshape(-1,no_features)
        ss = np.repeat(feature_matrix[:,2],np.int64(np.round(100*quals1)))
        rr_70th = np.percentile(ss,lower_percentile)
        rr_95th = np.percentile(ss,higher_percentile)
        index = np.where((feature_matrix[:,2]>rr_70th)&(feature_matrix[:,2]<rr_95th))[0]
        for i in range(feature_matrix.shape[1]):
            m,s = weighted_avg_and_std(feature_matrix[index,i], quals1[index])
            s+=epsilon
            feature_matrix[:,i]  = (feature_matrix[:,i] - m)/s
        a['features_normalized']  = list([np.array(b) for b in feature_matrix])
        return a
    data_normalized = data_day._data.groupby(['user','day','version']).apply(normalize_features)
    if 'window' in data.columns:
        data_normalized = data_normalized.withColumn('window',F.struct('start', 'end')).drop(*['start','end','day'])
    else:
        data_normalized = data_normalized.drop(*['day'])
    features = DataStream(data=data_normalized,metadata=stream_metadata)
    return features