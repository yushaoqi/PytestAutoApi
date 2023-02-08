
from utils.read_files_tools.yaml_control import GetYamlData
from common.setting import ensure_path_sep
from utils.other_tools.models import Config


_data = GetYamlData(ensure_path_sep("\\common\\config.yaml")).get_yaml_data()
config = Config(**_data)

