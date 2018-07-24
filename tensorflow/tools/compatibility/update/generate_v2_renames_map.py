# Copyright 2018 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
# pylint: disable=line-too-long
"""Script for updating tensorflow/tools/compatibility/renames_v2.py.

To update renames_v2.py, run:
  bazel build tensorflow/tools/compatibility/update:generate_v2_renames_map
  bazel-bin/tensorflow/tools/compatibility/update/generate_v2_renames_map
"""
# pylint: enable=line-too-long

import tensorflow as tf

from tensorflow.python.lib.io import file_io
from tensorflow.python.util import tf_decorator
from tensorflow.python.util import tf_export
from tensorflow.tools.common import public_api
from tensorflow.tools.common import traverse


_OUTPUT_FILE_PATH = 'third_party/tensorflow/tools/compatibility/renames_v2.py'
_FILE_HEADER = """# Copyright 2018 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
# pylint: disable=line-too-long
\"\"\"List of renames to apply when converting from TF 1.0 to TF 2.0.

THIS FILE IS AUTOGENERATED: To update, please run:
  bazel build tensorflow/tools/compatibility/update:generate_v2_renames_map
  bazel-bin/tensorflow/tools/compatibility/update/generate_v2_renames_map
This file should be updated whenever endpoints are deprecated.
\"\"\"
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

"""


def update_renames_v2(output_file_path):
  """Writes a Python dictionary mapping deprecated to canonical API names.

  Args:
    output_file_path: File path to write output to. Any existing contents
      would be replaced.
  """
  # Set of rename lines to write to output file in the form:
  #   'tf.deprecated_name': 'tf.canonical_name'
  rename_line_set = set()
  # _tf_api_names attribute name
  tensorflow_api_attr = tf_export.API_ATTRS[tf_export.TENSORFLOW_API_NAME].names

  def visit(unused_path, unused_parent, children):
    """Visitor that collects rename strings to add to rename_line_set."""
    for child in children:
      _, attr = tf_decorator.unwrap(child[1])
      if not hasattr(attr, '__dict__'):
        continue
      api_names = attr.__dict__.get(tensorflow_api_attr, [])
      deprecated_api_names = attr.__dict__.get('_tf_deprecated_api_names', [])
      canonical_name = tf_export.get_canonical_name(
          api_names, deprecated_api_names)
      for name in deprecated_api_names:
        rename_line_set.add('    \'tf.%s\': \'tf.%s\'' % (name, canonical_name))

  visitor = public_api.PublicAPIVisitor(visit)
  visitor.do_not_descend_map['tf'].append('contrib')
  traverse.traverse(tf, visitor)

  renames_file_text = '%srenames = {\n%s\n}\n' % (
      _FILE_HEADER, ',\n'.join(sorted(rename_line_set)))
  file_io.write_string_to_file(output_file_path, renames_file_text)


def main(unused_argv):
  update_renames_v2(_OUTPUT_FILE_PATH)


if __name__ == '__main__':
  tf.app.run(main=main)