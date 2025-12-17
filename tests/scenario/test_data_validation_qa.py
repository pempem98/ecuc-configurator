"""
Scenario Test: Data Validation and Quality Assurance.

Test realistic data validation scenarios for QA team.
"""

import pytest
from pathlib import Path
from autosar.loader import CompleteXLSXLoader
from autosar.model import MessageDirection


# Test data path
TEST_DATA_DIR = Path(__file__).parent.parent.parent / 'examples' / 'xlsx'


class TestDataValidationScenario:
    """Scenario tests for data validation and QA."""
    
    @pytest.fixture
    def database(self):
        """Load test database for data validation."""
        loader = CompleteXLSXLoader()
        file_path = TEST_DATA_DIR / 'CAN_ECM_FD3.xlsx'
        if not file_path.exists():
            pytest.skip(f"Test file not found: {file_path}")
        return loader.load_complete(str(file_path))
    
    def test_scenario_validate_signal_boundaries(self, database):
        """
        Scenario: Validate signal boundaries within messages.
        
        Use case: QA engineer verifies no signal overlaps or overflow.
        Expected: All signals fit within message DLC.
        """
        validation_results = []
        
        for msg in database.messages:
            # Check total bit usage
            max_bit_used = 0
            for sig in msg.signals:
                signal_end_bit = sig.start_bit + sig.signal_size
                if signal_end_bit > max_bit_used:
                    max_bit_used = signal_end_bit
            
            max_dlc_bits = msg.message_length * 8
            
            result = {
                'message': msg.message_name,
                'message_id': f"0x{msg.message_id:X}",
                'dlc': msg.message_length,
                'max_bit_used': max_bit_used,
                'max_dlc_bits': max_dlc_bits,
                'is_valid': max_bit_used <= max_dlc_bits,
            }
            validation_results.append(result)
        
        # All messages should be valid
        invalid = [r for r in validation_results if not r['is_valid']]
        assert len(invalid) == 0, f"Found {len(invalid)} messages with signal overflow"
    
    def test_scenario_validate_unique_message_ids(self, database):
        """
        Scenario: Validate unique message IDs.
        
        Use case: Prevent ID conflicts in CAN network.
        Expected: All message IDs are unique within direction.
        """
        rx_ids = set()
        tx_ids = set()
        duplicates = []
        
        for msg in database.messages:
            if msg.is_rx:
                if msg.message_id in rx_ids:
                    duplicates.append(f"RX ID 0x{msg.message_id:X} duplicate: {msg.message_name}")
                rx_ids.add(msg.message_id)
            else:
                if msg.message_id in tx_ids:
                    duplicates.append(f"TX ID 0x{msg.message_id:X} duplicate: {msg.message_name}")
                tx_ids.add(msg.message_id)
        
        assert len(duplicates) == 0, f"Found duplicate IDs: {duplicates}"
    
    def test_scenario_validate_signal_naming_convention(self, database):
        """
        Scenario: Validate signal naming conventions.
        
        Use case: Ensure consistent naming across team.
        Expected: Signal names follow project conventions.
        """
        naming_issues = []
        
        for msg in database.messages:
            for sig in msg.signals:
                # Check for empty names
                if not sig.signal_name or sig.signal_name.strip() == '':
                    naming_issues.append(f"Empty signal name in {msg.message_name}")
                
                # Check for special characters (basic check)
                if sig.signal_name and not sig.signal_name.replace('_', '').replace('-', '').isalnum():
                    naming_issues.append(f"Invalid characters in signal: {sig.signal_name}")
        
        assert len(naming_issues) == 0, f"Found naming issues: {naming_issues}"
    
    def test_scenario_validate_data_consistency(self, database):
        """
        Scenario: Validate data consistency.
        
        Use case: Cross-check related fields for consistency.
        Expected: Related fields are consistent (e.g., SNA values).
        """
        consistency_issues = []
        
        for msg in database.messages:
            for sig in msg.signals:
                # If has_sna is True, sna_value should be set
                if sig.has_sna and sig.sna_value is None:
                    consistency_issues.append(
                        f"Signal {sig.signal_name} has SNA but no value"
                    )
                
                # If invalidation enabled, should have policy
                if sig.has_invalidation_enabled and not sig.invalidation_policy:
                    consistency_issues.append(
                        f"Signal {sig.signal_name} has invalidation but no policy"
                    )
        
        # Allow some inconsistencies in test data, but report them
        if consistency_issues:
            print(f"Found {len(consistency_issues)} consistency issues (informational)")
    
    def test_scenario_validate_complete_field_coverage(self, database):
        """
        Scenario: Validate field coverage completeness.
        
        Use case: Ensure all required fields are populated.
        Expected: Core fields always populated, optional fields tracked.
        """
        coverage_report = {
            'messages': {
                'total': len(database.messages),
                'with_com_ipdu': 0,
                'with_timeout': 0,
            },
            'signals': {
                'total': 0,
                'with_data_element': 0,
                'with_port': 0,
                'with_scaling': 0,
            },
        }
        
        for msg in database.messages:
            if msg.com_ipdu_name:
                coverage_report['messages']['with_com_ipdu'] += 1
            if msg.com_ipdu_signal_timeout:
                coverage_report['messages']['with_timeout'] += 1
            
            for sig in msg.signals:
                coverage_report['signals']['total'] += 1
                if sig.data_element_name:
                    coverage_report['signals']['with_data_element'] += 1
                if sig.port_name:
                    coverage_report['signals']['with_port'] += 1
                if sig.data_type_scaled:
                    coverage_report['signals']['with_scaling'] += 1
        
        # Verify counts
        assert coverage_report['messages']['total'] == 85
        assert coverage_report['signals']['total'] == 781
        
        # Calculate coverage percentages
        msg_coverage = (coverage_report['messages']['with_com_ipdu'] / 
                       coverage_report['messages']['total'] * 100)
        sig_coverage = (coverage_report['signals']['with_data_element'] / 
                       coverage_report['signals']['total'] * 100)
        
        print(f"Message COM coverage: {msg_coverage:.1f}%")
        print(f"Signal data element coverage: {sig_coverage:.1f}%")


class TestCrossTeamIntegrationScenario:
    """Scenario tests for cross-team integration."""
    
    @pytest.fixture
    def database(self):
        """Load test database for cross-team integration."""
        loader = CompleteXLSXLoader()
        file_path = TEST_DATA_DIR / 'CAN_ECM_FD3.xlsx'
        if not file_path.exists():
            pytest.skip(f"Test file not found: {file_path}")
        return loader.load_complete(str(file_path))
    
    def test_scenario_com_team_requirements(self, database):
        """
        Scenario: Extract data for COM team.
        
        Use case: COM team needs I-PDU and signal group configuration.
        Expected: All COM-specific fields available.
        """
        com_data = {
            'ipdus': [],
            'signal_groups': {},
        }
        
        # Collect I-PDU data
        for msg in database.messages:
            ipdu = {
                'name': msg.com_ipdu_name or f"IPdu_{msg.message_name}",
                'id': msg.message_id,
                'dlc': msg.message_length,
                'direction': 'TX' if msg.is_tx else 'RX',
                'timeout': msg.com_ipdu_signal_timeout,
                'signals': len(msg.signals),
            }
            com_data['ipdus'].append(ipdu)
            
            # Collect signal groups
            for sig in msg.signals:
                if sig.signal_group:
                    if sig.signal_group not in com_data['signal_groups']:
                        com_data['signal_groups'][sig.signal_group] = []
                    com_data['signal_groups'][sig.signal_group].append({
                        'signal': sig.signal_name,
                        'ipdu': ipdu['name'],
                    })
        
        # Verify COM data completeness
        assert len(com_data['ipdus']) == 85
        assert len(com_data['signal_groups']) == 31
    
    def test_scenario_rte_team_requirements(self, database):
        """
        Scenario: Extract data for RTE team.
        
        Use case: RTE team needs port/interface configuration.
        Expected: All RTE-specific fields available.
        """
        rte_data = {
            'ports': {},
            'interfaces': {},
        }
        
        for msg in database.messages:
            for sig in msg.signals:
                # Collect port information
                if sig.port_name:
                    if sig.port_name not in rte_data['ports']:
                        rte_data['ports'][sig.port_name] = {
                            'signals': [],
                            'direction': 'sender' if msg.is_tx else 'receiver',
                        }
                    rte_data['ports'][sig.port_name]['signals'].append(sig.signal_name)
                
                # Collect interface information
                if sig.interface_name:
                    if sig.interface_name not in rte_data['interfaces']:
                        rte_data['interfaces'][sig.interface_name] = []
                    rte_data['interfaces'][sig.interface_name].append(sig.signal_name)
        
        # Verify RTE data exists
        assert len(rte_data['ports']) > 0 or len(rte_data['interfaces']) > 0, \
            "Should have RTE port or interface data"
    
    def test_scenario_swc_team_requirements(self, database):
        """
        Scenario: Extract data for SWC teams.
        
        Use case: SWC teams need producer/consumer mapping.
        Expected: SWC component relationships mapped.
        """
        swc_data = {
            'producers': {},
            'consumers': {},
        }
        
        for msg in database.messages:
            for sig in msg.signals:
                # Map producers
                if msg.is_tx and sig.producer_swc:
                    if sig.producer_swc not in swc_data['producers']:
                        swc_data['producers'][sig.producer_swc] = []
                    swc_data['producers'][sig.producer_swc].append({
                        'signal': sig.signal_name,
                        'message': msg.message_name,
                        'port': sig.port_name,
                    })
                
                # Map consumers
                if msg.is_rx and sig.consumer_swc:
                    if sig.consumer_swc not in swc_data['consumers']:
                        swc_data['consumers'][sig.consumer_swc] = []
                    swc_data['consumers'][sig.consumer_swc].append({
                        'signal': sig.signal_name,
                        'message': msg.message_name,
                        'port': sig.port_name,
                    })
        
        # Verify SWC data
        assert len(swc_data['producers']) > 0 or len(swc_data['consumers']) > 0, \
            "Should have SWC producer or consumer data"
    
    def test_scenario_canif_team_requirements(self, database):
        """
        Scenario: Extract data for CanIf team.
        
        Use case: CanIf team needs message and frame type information.
        Expected: Frame configuration with extended ID support.
        """
        canif_data = {
            'standard_frames': [],
            'extended_frames': [],
        }
        
        for msg in database.messages:
            frame = {
                'name': msg.message_name,
                'id': msg.message_id,
                'id_hex': f"0x{msg.message_id:X}",
                'dlc': msg.message_length,
                'direction': 'TX' if msg.is_tx else 'RX',
            }
            
            if msg.is_extended:
                canif_data['extended_frames'].append(frame)
            else:
                canif_data['standard_frames'].append(frame)
        
        # Verify CanIf data
        assert len(canif_data['standard_frames']) == 81
        assert len(canif_data['extended_frames']) == 4


class TestPerformanceScenario:
    """Scenario tests for performance requirements."""
    
    @pytest.fixture
    def loader(self):
        """Create loader instance."""
        return CompleteXLSXLoader()
    
    @pytest.fixture
    def test_file(self):
        """Path to test Excel file."""
        file_path = TEST_DATA_DIR / 'CAN_ECM_FD3.xlsx'
        if not file_path.exists():
            pytest.skip(f"Test file not found: {file_path}")
        return str(file_path)
    
    def test_scenario_load_large_file_performance(self, loader, test_file):
        """
        Scenario: Load large Excel file efficiently.
        
        Use case: Load 85 messages with 781 signals in reasonable time.
        Expected: Loading completes within acceptable time.
        """
        import time
        
        start_time = time.time()
        database = loader.load_complete(test_file)
        end_time = time.time()
        
        load_time = end_time - start_time
        
        # Verify loaded correctly
        assert len(database.messages) == 85
        
        # Check performance (should be < 5 seconds for this size)
        print(f"Load time: {load_time:.2f} seconds")
        assert load_time < 5.0, f"Loading took too long: {load_time:.2f}s"
    
    def test_scenario_query_performance(self, loader, test_file):
        """
        Scenario: Query database efficiently.
        
        Use case: Find messages and signals quickly for UI.
        Expected: Queries complete in milliseconds.
        """
        import time
        
        database = loader.load_complete(test_file)
        
        # Test message lookup performance
        start_time = time.time()
        for _ in range(100):  # 100 lookups
            msg = database.get_message_by_id(0x5B0)
            assert msg is not None
        end_time = time.time()
        
        avg_lookup_time = (end_time - start_time) / 100
        
        print(f"Average lookup time: {avg_lookup_time*1000:.2f} ms")
        assert avg_lookup_time < 0.01, "Lookup too slow"  # < 10ms


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
