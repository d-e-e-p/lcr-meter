# regmap_parser.py
import yaml

class RegisterMap:
    """
    A custom class to load and manage a register map from a YAML file.
    The YAML file can group registers, and this class will flatten them
    for easy access.
    """
    def __init__(self, register_data):
        self._data = register_data
        self.registers = self._flatten_registers(register_data)

    @classmethod
    def from_yaml_file(cls, file_path):
        """Creates a RegisterMap instance from a YAML file."""
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        return cls(data)

    def _flatten_registers(self, data):
        """
        Flattens the grouped register structure into a single dictionary
        for easy lookup by register name. This allows the rest of the
        application to work without needing to know about the groups.
        """
        flat_map = {}
        for group_name, group_data in data.items():
            for register_name, register_info in group_data.items():
                flat_map[register_name] = register_info
        return flat_map

    def get_register(self, name):
        """Retrieves a single register's information by name."""
        return self.registers.get(name)

    def get_all_registers(self):
        """Returns the entire flattened register map."""
        return self.registers
