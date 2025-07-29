# Copyright 2024 The TensorFlow Authors. All Rights Reserved.
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
"""Generate comprehensive TensorFlow Java reference docs for TensorFlow.org.

This script generates documentation for the complete TensorFlow Java ecosystem,
including the main TensorFlow Java library (currently v1.1.0) and related
components. This addresses issue #96799 by ensuring the documentation reflects
the current state of TensorFlow Java rather than outdated versions.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import pathlib
import shutil
import tempfile
import subprocess
import os
try:
  from git import Repo
  HAS_GITPYTHON = True
except ImportError:
  HAS_GITPYTHON = False
  print("Warning: GitPython not available. Will use subprocess for git operations.")

from absl import app
from absl import flags

from tensorflow_docs.api_generator import gen_java

FLAGS = flags.FLAGS

# Current versions - Updated to reflect TensorFlow Java 1.1.0
TENSORFLOW_JAVA_VERSION = 'v1.1.0'
NDARRAY_VERSION = 'v1.0.0'

# These flags are required by infrastructure, not all of them are used.
flags.DEFINE_string('output_dir', '/tmp/java_api/',
                    ("Use this branch as the root version and don't"
                     ' create in version directory'))

flags.DEFINE_string('site_path', 'java/api_docs/java',
                    'Path prefix in the _toc.yaml')

flags.DEFINE_string('code_url_prefix', None,
                    '[UNUSED] The url prefix for links to code.')

flags.DEFINE_bool(
    'search_hints', True,
    '[UNUSED] Include metadata search hints in the generated files')

flags.DEFINE_bool('gen_ops', True, 'enable/disable bazel-generated ops')

flags.DEFINE_string('tensorflow_java_repo', None,
                    'Path to local TensorFlow Java repository. If not provided, '
                    'will clone from GitHub.')

# __file__ is the path to this file
TOOLS_DIR = pathlib.Path(__file__).resolve().parent
REPO_ROOT = TOOLS_DIR.parents[2]
TF_JAVA_SOURCE_PATH = REPO_ROOT / 'tensorflow/java/src/main/java'


def clone_or_update_repo(repo_url, local_path, version_tag):
  """Clone or update a git repository to a specific version."""
  if not pathlib.Path(local_path).exists():
    print(f"Cloning {repo_url} to {local_path}")
    if HAS_GITPYTHON:
      local_repo = Repo.clone_from(repo_url, local_path)
      print(f"Checking out {version_tag}")
      local_repo.git.checkout(version_tag)
    else:
      # Fallback to subprocess
      subprocess.check_call(['git', 'clone', repo_url, str(local_path)])
      subprocess.check_call(['git', 'checkout', version_tag], cwd=local_path)
  else:
    print(f"Using existing repository at {local_path}")
    if HAS_GITPYTHON:
      local_repo = Repo(local_path)
      local_repo.remotes['origin'].fetch()
      print(f"Checking out {version_tag}")
      local_repo.git.checkout(version_tag)
    else:
      # Fallback to subprocess
      subprocess.check_call(['git', 'fetch', 'origin'], cwd=local_path)
      subprocess.check_call(['git', 'checkout', version_tag], cwd=local_path)
  
  return local_path


def checkout_tensorflow_java():
  """Clone and checkout the TensorFlow Java repository."""
  if FLAGS.tensorflow_java_repo:
    return pathlib.Path(FLAGS.tensorflow_java_repo)
  
  repo_url = 'https://github.com/tensorflow/java'
  local_repo_path = REPO_ROOT / 'tensorflow-java'
  clone_or_update_repo(repo_url, local_repo_path, TENSORFLOW_JAVA_VERSION)
  return local_repo_path


def checkout_ndarray():
  """Clone and checkout the TensorFlow Java NDArray repository."""
  repo_url = 'https://github.com/tensorflow/java-ndarray'
  local_repo_path = REPO_ROOT / 'ndarray'
  clone_or_update_repo(repo_url, local_repo_path, NDARRAY_VERSION)
  return local_repo_path


def overlay(from_root, to_root):
  """Overlay files from one directory to another, creating directories as needed."""
  for from_path in pathlib.Path(from_root).rglob('*'):
    relpath = from_path.relative_to(from_root)
    to_path = to_root / relpath
    if from_path.is_file():
      if to_path.exists():
        print(f"Warning: Overwriting {to_path}")
      else:
        to_path.parent.mkdir(parents=True, exist_ok=True)
      shutil.copyfile(from_path, to_path)
    else:
      to_path.mkdir(exist_ok=True)


def build_traditional_tensorflow_java_docs(merged_source):
  """Build docs for the traditional TensorFlow Java API (from this repo)."""
  print("Building traditional TensorFlow Java API documentation...")
  
  # Copy the traditional TensorFlow Java sources
  if TF_JAVA_SOURCE_PATH.exists():
    shutil.copytree(TF_JAVA_SOURCE_PATH, merged_source / 'java')
    
    if FLAGS.gen_ops:
      # Generate ops documentation if requested
      print("Generating ops documentation...")
      try:
        # Configure and build ops
        yes = subprocess.Popen(['yes', ''], stdout=subprocess.PIPE)
        configure = subprocess.Popen([REPO_ROOT / 'configure'],
                                     stdin=yes.stdout,
                                     cwd=REPO_ROOT)
        configure.communicate()

        subprocess.check_call(
            ['bazel', 'build', '//tensorflow/java:java_op_gen_sources'],
            cwd=REPO_ROOT)
        
        op_source_path = (REPO_ROOT / 
                         'bazel-bin/tensorflow/java/ops/src/main/java/org/tensorflow/op')
        if op_source_path.exists():
          shutil.copytree(op_source_path, merged_source / 'java/org/tensorflow/ops')
      except subprocess.CalledProcessError as e:
        print(f"Warning: Failed to build ops documentation: {e}")


def build_comprehensive_java_docs(merged_source):
  """Build comprehensive TensorFlow Java documentation including external repos."""
  print("Building comprehensive TensorFlow Java documentation...")
  
  # Create the base Java directory structure
  (merged_source / 'java/org').mkdir(parents=True, exist_ok=True)
  
  # Checkout external repositories
  tensorflow_java_repo = checkout_tensorflow_java()
  ndarray_repo = checkout_ndarray()
  
  # Copy TensorFlow Java sources
  tf_java_core_api = tensorflow_java_repo / 'tensorflow-core/tensorflow-core-api/src/main/java/org/tensorflow'
  if tf_java_core_api.exists():
    shutil.copytree(tf_java_core_api, merged_source / 'java/org/tensorflow')
  
  # Overlay generated sources
  tf_java_gen_api = tensorflow_java_repo / 'tensorflow-core/tensorflow-core-api/src/gen/java/org/tensorflow'
  if tf_java_gen_api.exists():
    overlay(tf_java_gen_api, merged_source / 'java/org/tensorflow')
  
  # Copy native sources
  tf_java_native_proto = tensorflow_java_repo / 'tensorflow-core/tensorflow-core-native/src/gen/java/org/tensorflow/proto'
  if tf_java_native_proto.exists():
    shutil.copytree(tf_java_native_proto, merged_source / 'java/org/tensorflow/proto')
  
  tf_java_exceptions = tensorflow_java_repo / 'tensorflow-core/tensorflow-core-native/src/main/java/org/tensorflow/exceptions'
  if tf_java_exceptions.exists():
    shutil.copytree(tf_java_exceptions, merged_source / 'java/org/tensorflow/exceptions')
  
  tf_java_c_api = tensorflow_java_repo / 'tensorflow-core/tensorflow-core-native/src/gen/java/org/tensorflow/internal/c_api'
  if tf_java_c_api.exists():
    shutil.copytree(tf_java_c_api, merged_source / 'java/org/tensorflow/internal/c_api')
  
  # Copy framework sources
  tf_java_framework = tensorflow_java_repo / 'tensorflow-framework/src/main/java/org/tensorflow/framework'
  if tf_java_framework.exists():
    shutil.copytree(tf_java_framework, merged_source / 'java/org/tensorflow/framework')
  
  # Copy NDArray sources
  ndarray_source = ndarray_repo / 'ndarray/src/main/java/org/tensorflow/ndarray'
  if ndarray_source.exists():
    shutil.copytree(ndarray_source, merged_source / 'java/org/tensorflow/ndarray')


def main(unused_argv):
  """Main function to generate comprehensive TensorFlow Java documentation."""
  print(f"Generating TensorFlow Java documentation (version {TENSORFLOW_JAVA_VERSION})")
  
  merged_source = pathlib.Path(tempfile.mkdtemp())
  print(f"Working in temporary directory: {merged_source}")
  
  try:
    # First try to build comprehensive docs with external repos
    build_comprehensive_java_docs(merged_source)
  except Exception as e:
    print(f"Warning: Failed to build comprehensive docs: {e}")
    print("Falling back to traditional TensorFlow Java docs...")
    # Clean up and try traditional approach
    shutil.rmtree(merged_source)
    merged_source = pathlib.Path(tempfile.mkdtemp())
    build_traditional_tensorflow_java_docs(merged_source)
  
  # Generate the documentation
  print(f"Generating documentation to {FLAGS.output_dir}")
  gen_java.gen_java_docs(
      package='org.tensorflow',
      source_path=merged_source / 'java',
      output_dir=pathlib.Path(FLAGS.output_dir),
      site_path=pathlib.Path(FLAGS.site_path),
      # Uncomment for local testing:
      # script_path=pathlib.Path(REPO_ROOT/'tools/run-javadoc-for-tf-local.sh'),
  )
  
  print("Documentation generation completed successfully!")


if __name__ == '__main__':
  flags.mark_flags_as_required(['output_dir'])
  app.run(main)
