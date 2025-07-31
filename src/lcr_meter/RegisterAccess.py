# 
import os

from .RegisterMap import RegisterMap


class RegisterAccess:
    """
    """
    def __init__(self, dev):
        # Initialize a dictionary to act as the register memory
        self.dev = dev
        # Load the register map from the YAML file
        yaml_file = os.path.join(os.path.dirname(__file__),  'ad5940_registers.yaml')
        self.ad5940_map = RegisterMap.from_yaml_file(yaml_file)

    def read_register(self, register_name):
        """
        Reads a register from the device, decodes its value into bitfields,
        and prints the result in a table.
        Args:
            register_name (str): The name of the register to decode (e.g., "AFECON").
        """
        if register_name not in self.ad5940_map.registers:
            print(f"Error: Register '{register_name}' not found in the map.")
            return

        reg_info = self.ad5940_map.registers[register_name]
        address = reg_info["address"]
        reset_val = reg_info.get("reset", 0)  # Get the reset value for the register
        bitfields_info = reg_info["bitfields"]

        reg_val = self.dev.reg_read(address)

        print(f"\nDecoding Register: {register_name} (Address: 0x{address:04X})")
        print(f"Current Value: 0x{reg_val:08X} (Reset: 0x{reset_val:08X})")
        print("-" * 80)
        print(f"{'Bitfield':<20} {'Value (Hex)':<15} {'Decoded Description':<40}")
        print("-" * 80)

        sorted_bitfields = sorted(bitfields_info.items(), key=lambda item: item[1]['start_bit'])
        changed_values_exist = False

        for name, info in sorted_bitfields:
            start_bit = info["start_bit"]
            num_bits = info["num_bits"]
            mask = (1 << num_bits) - 1

            # Get current value and reset value for the bitfield
            field_val = (reg_val >> start_bit) & mask
            reset_field_val = (reset_val >> start_bit) & mask

            # Check if the value has changed from reset
            changed_marker = "*" if field_val != reset_field_val else ""
            if changed_marker:
                changed_values_exist = True

            desc = f"Raw value: 0x{field_val:X}"
            if "value_map" in info:
                desc = info["value_map"].get(field_val, f"Unknown value (0x{field_val:X})")

            # Add the marker to the description if it has changed
            print(f"{name:<20} {f'0x{field_val:X}':<15} {desc:<38} {changed_marker}")

        print("-" * 80)
        if changed_values_exist:
            print("* - Value differs from reset")



    def write_register(self, register_name, bitfield_name, new_value):
        """
        Sets a specific bitfield in a register to a new value by performing a
        read-modify-write operation.

        Args:
            register_name (str): The name of the register to modify.
            bitfield_name (str): The name of the bitfield to set.
            new_value (int): The new integer value for the bitfield.
        """
        if register_name not in self.ad5940_map.registers:
            print(f"Error: Register '{register_name}' not found in the map.")
            return

        reg_info = self.ad5940_map.registers[register_name]
        address = reg_info["address"]

        if bitfield_name not in reg_info["bitfields"]:
            print(f"Error: Bitfield '{bitfield_name}' not found in register '{register_name}'.")
            return

        bitfield_info = reg_info["bitfields"][bitfield_name]
        start_bit = bitfield_info["start_bit"]
        num_bits = bitfield_info["num_bits"]

        # 1. Read the current register value
        current_reg_val = self.dev.reg_read(address)
        print(f"Read current value of {register_name}: 0x{current_reg_val:08X}")

        # 2. Modify the value
        # Create a mask to clear only the bits for the target bitfield
        mask = (1 << num_bits) - 1
        # Clear the bits in the register value
        cleared_reg_val = current_reg_val & ~(mask << start_bit)
        # Shift the new value to the correct bit position and OR it with the register value
        new_reg_val = cleared_reg_val | (new_value << start_bit)

        print(f"Setting bitfield '{bitfield_name}' to {new_value} (0x{new_value:X})")
        print(f"New value for {register_name} will be: 0x{new_reg_val:08X}")

        # 3. Write the new value back to the register
        self.dev.reg_write(address, new_reg_val)


if __name__ == '__main__':
    # --- Example Usage ---
    # This block demonstrates how to use the functions.

    dev = None
    register_access = RegisterAccess(dev)

    print("--- Initial State ---")
    # 1. Decode the initial state of AFECON.
    register_access.read_register("AFECON")

    print("\n--- Modifying a Register ---")
    # 3. Set the SINC2EN bit in AFECON to 1.
    register_access.write_register("AFECON", "SINC2EN", 1)

    # 4. Decode AFECON again to see the change.
    register_access.read_register("AFECON")

    print("\n--- Handling Errors ---")
    # 5. Try to set an invalid bitfield.
    register_access.write_register("AFECON", "INVALID_BIT", 1)

    print("\n--- Modifying Another Register ---")
    # 6. Set CTIASEL to 32pF (which has a value of 0b00100000 = 32).
    # ad_set_register("CTIACON", "CTIASEL", 0b00100000)
    # read_register("CTIACON")
