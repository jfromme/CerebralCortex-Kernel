# Copyright (c) 2019, MD2K Center of Excellence
# - Nasir Ali <nasir.ali08@gmail.com>
# All rights reserved.
#
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

from datetime import datetime, timedelta

from cerebralcortex.core.metadata_manager.stream.metadata import Metadata, DataDescriptor, ModuleMetadata
from cerebralcortex.core.util.spark_helper import get_or_create_sc


def gen_phone_battery_data(user_id)->object:
    """
    Create pyspark dataframe with some sample phone battery data
    Returns:
        DataFrame: pyspark dataframe object with columns: ["timestamp", "offset", "battery_level", "ver", "user"]

    """
    column_name = ["timestamp", "offset", "battery_level", "version", "user"]
    sample_data = []
    timestamp = datetime(2019, 1, 9, 11, 34, 59)
    tmp = 1
    sample = 100
    sqlContext = get_or_create_sc("sqlContext")
    for row in range(1000, 1, -1):
        tmp += 1
        if tmp == 100:
            sample = sample - 1
            tmp = 1
        timestamp = timestamp + timedelta(0, 1)
        sample_data.append((timestamp, "21600000", sample, 1, user_id))
    df = sqlContext.createDataFrame(sample_data, column_name)
    return df


def gen_phone_battery_metadata(stream_name)->Metadata:
    """
    Create Metadata object with some sample metadata of phone battery data
    Returns:
        Metadata: metadata of phone battery stream
    """
    stream_metadata = Metadata()
    stream_metadata.set_name(stream_name).set_version(1) \
        .add_dataDescriptor(
        DataDescriptor().name("level").type("float").set_attribute("description", "current battery charge")) \
        .add_module(
        ModuleMetadata().name("battery").version("1.2.4").set_attribute("attribute_key", "attribute_value").set_author(
            "test_user", "test_user@test_email.com"))
    stream_metadata.is_valid()
    return stream_metadata
