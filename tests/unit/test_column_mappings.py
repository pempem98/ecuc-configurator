"""
Unit Tests for Column Mapping Classes.

Tests bidirectional Excel column mappings.
"""

import pytest
from autosar.model import (
    RxColumnMapping,
    TxColumnMapping,
    ExcelColumnMapping,
)


class TestRxColumnMapping:
    """Unit tests for RxColumnMapping."""
    
    def test_get_field_for_column(self):
        """Test getting model field for Excel column."""
        # Test valid columns
        assert RxColumnMapping.get_field_for_column('CAN Signal Name') == 'signal_name'
        assert RxColumnMapping.get_field_for_column('CAN Message Name') == 'message_name'
        assert RxColumnMapping.get_field_for_column('Data Element Name') == 'data_element_name'
        assert RxColumnMapping.get_field_for_column('Port Name') == 'port_name'  # Note: actual col has newline
        
        # Test invalid column
        assert RxColumnMapping.get_field_for_column('NonExistent') is None
    
    def test_get_column_for_field(self):
        """Test getting Excel column for model field."""
        # Test valid fields
        assert RxColumnMapping.get_column_for_field('signal_name') == 'CAN Signal Name'
        assert RxColumnMapping.get_column_for_field('message_name') == 'CAN Message Name'
        assert RxColumnMapping.get_column_for_field('data_element_name') == 'Data Element Name'
        
        # Test invalid field
        assert RxColumnMapping.get_column_for_field('nonexistent_field') is None
    
    def test_get_column_index(self):
        """Test getting column index for field."""
        # Test valid fields (0-based index)
        assert RxColumnMapping.get_column_index('message_name') == 0
        assert RxColumnMapping.get_column_index('message_id') == 1
        assert RxColumnMapping.get_column_index('signal_name') == 2
        
        # Test invalid field
        assert RxColumnMapping.get_column_index('nonexistent_field') is None
    
    def test_get_all_mappings(self):
        """Test getting all column mappings."""
        mappings = RxColumnMapping.get_all_mappings()
        
        assert isinstance(mappings, dict)
        assert len(mappings) == 44  # RX sheet has 44 columns
        
        # Check some key mappings
        assert mappings['CAN Signal Name'] == 'signal_name'
        assert mappings['CAN Message Name'] == 'message_name'
        assert mappings['Data Element Name'] == 'data_element_name'
    
    def test_all_columns_defined(self):
        """Test that all 44 RX columns are defined."""
        mappings = RxColumnMapping.get_all_mappings()
        
        expected_fields = [
            'message_name', 'message_id', 'signal_name',
            'legacy_rx_srd_name', 'legacy_impl_name',
            'signal_size', 'units', 'signal_group',
            'has_sna', 'periodicity', 'timeout',
            'dbc_comment', 'notes',
            'start_bit', 'main_function', 'consumer_swc', 'status',
            'data_element_name', 'data_type', 'data_struct_element',
            'data_constraint', 'compu_method', 'invalid_value',
            'type_reference', 'invalidation_policy',
            'initial_value', 'initial_value_const',
            'timeout_value', 'conversion_function',
            'long_name', 'port_name',
            'data_type_scaled', 'data_struct_element_scaled',
            'struct_element_type_ref', 'mapped_idt',
            'data_constraint_name', 'signal_min_value', 'signal_max_value',
            'compu_method_name', 'units_scaled',
            'initial_value_scaled', 'invalid_value_scaled',
            'invalidation_policy_scaled', 'ddf_unit',
        ]
        
        for field in expected_fields:
            assert field in mappings.values(), f"Missing field: {field}"


class TestTxColumnMapping:
    """Unit tests for TxColumnMapping."""
    
    def test_get_field_for_column(self):
        """Test getting model field for Excel column."""
        # Test valid columns
        assert TxColumnMapping.get_field_for_column('CAN Signal Name') == 'signal_name'
        assert TxColumnMapping.get_field_for_column('CAN Message Name') == 'message_name'
        assert TxColumnMapping.get_field_for_column('Producer SWC') == 'producer_swc'
        
        # Test invalid column
        assert TxColumnMapping.get_field_for_column('NonExistent') is None
    
    def test_get_column_for_field(self):
        """Test getting Excel column for model field."""
        # Test valid fields
        assert TxColumnMapping.get_column_for_field('signal_name') == 'CAN Signal Name'
        assert TxColumnMapping.get_column_for_field('message_name') == 'CAN Message Name'
        assert TxColumnMapping.get_column_for_field('producer_swc') == 'Producer SWC'
        
        # Test invalid field
        assert TxColumnMapping.get_column_for_field('nonexistent_field') is None
    
    def test_get_column_index(self):
        """Test getting column index for field."""
        # Test valid fields (0-based index)
        assert TxColumnMapping.get_column_index('message_name') == 0
        assert TxColumnMapping.get_column_index('message_id') == 1
        assert TxColumnMapping.get_column_index('signal_name') == 2
        
        # Test invalid field
        assert TxColumnMapping.get_column_index('nonexistent_field') is None
    
    def test_get_all_mappings(self):
        """Test getting all column mappings."""
        mappings = TxColumnMapping.get_all_mappings()
        
        assert isinstance(mappings, dict)
        assert len(mappings) == 43  # TX sheet has 43 columns
        
        # Check some key mappings
        assert mappings['CAN Signal Name'] == 'signal_name'
        assert mappings['CAN Message Name'] == 'message_name'
        assert mappings['Producer SWC'] == 'producer_swc'
    
    def test_all_columns_defined(self):
        """Test that all 43 TX columns are defined."""
        mappings = TxColumnMapping.get_all_mappings()
        
        expected_fields = [
            'message_name', 'message_id', 'signal_name',
            'signal_group', 'signal_size', 'units',
            'has_sna', 'periodicity', 'dbc_comment', 'notes',
            'start_bit', 'main_function',
            'legacy_srd_dd_name', 'legacy_tx_accessor_name',
            'pmbd_phase', 'pmbd_coe_producer',
            'producer_swc', 'status',
            'data_element_name', 'data_type', 'data_struct_element',
            'type_reference', 'data_constraint', 'compu_method',
            'invalid_value', 'initial_value', 'initial_value_const',
            'invalidation_policy', 'conversion_function',
            'long_name', 'port_name',
            'data_type_scaled', 'data_struct_element_scaled',
            'struct_element_type_ref', 'mapped_idt',
            'data_constraint_scaled', 'signal_min_value', 'signal_max_value',
            'compu_method_scaled', 'units_scaled',
            'initial_value_scaled', 'invalid_value_scaled',
            'invalidation_policy_scaled',
        ]
        
        for field in expected_fields:
            assert field in mappings.values(), f"Missing field: {field}"
    
    def test_tx_specific_fields(self):
        """Test TX-specific fields not in RX."""
        mappings = TxColumnMapping.get_all_mappings()
        
        # TX-specific fields
        tx_only_fields = [
            'legacy_srd_dd_name',
            'legacy_tx_accessor_name',
            'pmbd_phase',
            'pmbd_coe_producer',
            'producer_swc',
        ]
        
        for field in tx_only_fields:
            assert field in mappings.values(), f"Missing TX-specific field: {field}"


class TestColumnMappingConsistency:
    """Tests for consistency between RX and TX mappings."""
    
    def test_common_fields_exist_in_both(self):
        """Test that common fields exist in both RX and TX."""
        rx_mappings = RxColumnMapping.get_all_mappings()
        tx_mappings = TxColumnMapping.get_all_mappings()
        
        common_fields = [
            'message_name',
            'message_id',
            'signal_name',
            'signal_size',
            'units',
            'signal_group',
            'has_sna',
            'periodicity',
            'dbc_comment',
            'notes',
            'start_bit',
            'main_function',
            'status',
            'data_element_name',
            'data_type',
            'conversion_function',
        ]
        
        for field in common_fields:
            assert field in rx_mappings.values(), f"Missing common field in RX: {field}"
            assert field in tx_mappings.values(), f"Missing common field in TX: {field}"
    
    def test_rx_specific_fields(self):
        """Test RX-specific fields not in TX."""
        rx_mappings = RxColumnMapping.get_all_mappings()
        tx_mappings = TxColumnMapping.get_all_mappings()
        
        rx_only_fields = [
            'legacy_rx_srd_name',
            'legacy_impl_name',
            'consumer_swc',
            'timeout',
            'timeout_value',
            'ddf_unit',
            'data_constraint_name',  # RX has data_constraint_name, TX has data_constraint_scaled
            'compu_method_name',     # RX has compu_method_name, TX has compu_method_scaled
        ]
        
        for field in rx_only_fields:
            assert field in rx_mappings.values(), f"Missing RX-specific field: {field}"
            assert field not in tx_mappings.values(), f"RX-specific field found in TX: {field}"
    
    def test_column_indices_are_sequential(self):
        """Test that column indices are sequential and start from 0."""
        # Test RX
        rx_indices = []
        for attr_name in dir(RxColumnMapping):
            attr = getattr(RxColumnMapping, attr_name)
            if isinstance(attr, tuple) and len(attr) == 3:
                _, _, idx = attr
                rx_indices.append(idx)
        
        rx_indices.sort()
        assert rx_indices == list(range(44)), "RX column indices not sequential"
        
        # Test TX
        tx_indices = []
        for attr_name in dir(TxColumnMapping):
            attr = getattr(TxColumnMapping, attr_name)
            if isinstance(attr, tuple) and len(attr) == 3:
                _, _, idx = attr
                tx_indices.append(idx)
        
        tx_indices.sort()
        assert tx_indices == list(range(43)), "TX column indices not sequential"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
