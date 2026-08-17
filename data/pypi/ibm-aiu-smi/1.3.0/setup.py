# Copyright 2026 The Torch-Spyre Authors.
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

from setuptools import setup

setup(
    data_files=[
        ("bin", [
            "aiu_smi/aiu-smi",
        ]),
        ("lib", [
            "aiu_smi/aiu_smi_main.py",
            "aiu_smi/aiu_smi_helper.py",
            "aiu_smi/metric_state_helper.py",
            "aiu_smi/pt_active_models.json",
        ]),
        ("etc", [
            "configs/senlib_config_aiusmi.json",
        ]),
        ("share/aiu-smi", [
            "README.md",
        ]),
        ("share/aiu-smi/docs", [
            "docs/aiusmi_overview_pub2.png",
            "docs/vfmode_output_comparison_pub1.png",
        ]),
        ("lib/llm_calc", [
            "llm_calc/README.md",
            "llm_calc/llm_memory_calculator.py",
        ]),
        ("lib/pt_active_model", [
            "pt_active_model/README.md",
            "pt_active_model/requirements.txt",
            "pt_active_model/smi_pt_training_1_split_jobs.py",
            "pt_active_model/smi_pt_training_2_process_job.py",
            "pt_active_model/smi_pt_training_3_subtract_idle_power.py",
            "pt_active_model/smi_pt_training_4_modeling.py",
        ]),
    ],
)
