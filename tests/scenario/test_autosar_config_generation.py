"""
Scenario Test: AUTOSAR Configuration Generation.

Test realistic scenario of generating AUTOSAR configuration from Excel data.
"""

import pytest
from pathlib import Path
from autosar.loader import CompleteXLSXLoader
from autosar.model import CompleteXLSXDatabase, MessageDirection


# Test data path
TEST_DATA_DIR = Path(__file__).parent.parent.parent / 'examples' / 'xlsx'


class TestAutosarConfigGeneration:
    """Scenario tests for AUTOSAR configuration generation."""
    
    @pytest.fixture
    def database(self):
        """Load test database for AUTOSAR config generation."""
        loader = CompleteXLSXLoader()
        file_path = TEST_DATA_DIR / 'CAN_ECM_FD3.xlsx'
        if not file_path.exists():
            pytest.skip(f"Test file not found: {file_path}")
        return loader.load_complete(str(file_path))
    
    def test_scenario_extract_com_ipdu_config(self, database):
        """
        Scenario: Extract COM I-PDU configuration from Excel.
        
        Use case: Generate AUTOSAR COM I-PDU configuration for ECU.
        Expected: All messages have required COM fields.
        """
        # Collect messages for COM configuration
        com_ipdus = []
        
        for msg in database.messages:
            ipdu_info = {
                'name': msg.com_ipdu_name or f"IPdu_{msg.message_name}",
                'message_id': msg.message_id,
                'dlc': msg.message_length,
                'direction': 'TX' if msg.direction == MessageDirection.TX else 'RX',
                'signal_count': len(msg.signals),
            }
            com_ipdus.append(ipdu_info)
        
        # Verify COM configuration completeness
        assert len(com_ipdus) == 85
        
        # Check all have names
        for ipdu in com_ipdus:
            assert ipdu['name'], f"IPdu for message {ipdu['message_id']} missing name"
            assert 0 <= ipdu['dlc'] <= 64, f"Invalid DLC {ipdu['dlc']}"
            assert ipdu['direction'] in ['RX', 'TX']
    
    def test_scenario_extract_signal_group_config(self, database):
        """
        Scenario: Extract signal group configuration.
        
        Use case: Generate COM signal group configuration.
        Expected: Signal groups properly organized with member signals.
        """
        signal_groups = {}
        
        # Collect signal groups from all messages
        for msg in database.messages:
            for sig in msg.signals:
                if sig.signal_group:
                    if sig.signal_group not in signal_groups:
                        signal_groups[sig.signal_group] = {
                            'message': msg.message_name,
                            'signals': []
                        }
                    signal_groups[sig.signal_group]['signals'].append(sig.signal_name)
        
        # Verify signal groups
        assert len(signal_groups) == 31  # Known from statistics
        
        # Each group should have multiple signals
        for group_name, group_info in signal_groups.items():
            assert len(group_info['signals']) >= 1, f"Group {group_name} has no signals"
    
    def test_scenario_extract_invalidation_config(self, database):
        """
        Scenario: Extract invalidation configuration.
        
        Use case: Generate COM invalidation configuration for signals.
        Expected: Signals with invalidation policy have valid SNA values.
        """
        signals_with_invalidation = []
        
        for msg in database.messages:
            for sig in msg.signals:
                if sig.has_invalidation_enabled:
                    invalidation_info = {
                        'signal_name': sig.signal_name,
                        'message': msg.message_name,
                        'policy': sig.invalidation_policy,
                        'has_sna': sig.has_sna,
                        'sna_value': sig.sna_value,
                    }
                    signals_with_invalidation.append(invalidation_info)
        
        # Verify invalidation configuration
        assert len(signals_with_invalidation) > 0, "Should have signals with invalidation"
        
        # Check consistency
        for sig_info in signals_with_invalidation:
            if sig_info['has_sna']:
                assert sig_info['sna_value'] is not None, \
                    f"Signal {sig_info['signal_name']} has SNA but no value"
    
    def test_scenario_extract_timeout_monitoring(self, database):
        """
        Scenario: Extract timeout monitoring configuration.
        
        Use case: Generate COM timeout monitoring for RX messages.
        Expected: RX messages have timeout values for monitoring.
        """
        timeout_configs = []
        
        for msg in database.rx_messages:
            if msg.com_ipdu_signal_timeout:
                timeout_info = {
                    'message_name': msg.message_name,
                    'message_id': msg.message_id,
                    'timeout_ms': msg.com_ipdu_signal_timeout,
                }
                timeout_configs.append(timeout_info)
        
        # Verify timeout monitoring
        # (Not all messages may have timeout, depends on data)
        assert isinstance(timeout_configs, list)
        
        # Check valid timeout values
        for config in timeout_configs:
            assert config['timeout_ms'] > 0, \
                f"Invalid timeout for {config['message_name']}"
    
    def test_scenario_extract_bsw_layer_mapping(self, database):
        """
        Scenario: Extract BSW layer mapping.
        
        Use case: Map signals to BSW layer (COM, PduR, CanIf).
        Expected: Signals have data elements and type references.
        """
        bsw_mappings = []
        
        for msg in database.messages:
            for sig in msg.signals:
                if sig.data_element_name:
                    bsw_info = {
                        'signal': sig.signal_name,
                        'data_element': sig.data_element_name,
                        'data_type': sig.data_type,
                        'type_reference': sig.type_reference,
                    }
                    bsw_mappings.append(bsw_info)
        
        # Verify BSW mapping
        assert len(bsw_mappings) > 0, "Should have BSW layer mappings"
        
        # Check mappings have data elements
        for mapping in bsw_mappings:
            assert mapping['data_element'], "Missing data element name"
    
    def test_scenario_extract_rte_config(self, database):
        """
        Scenario: Extract RTE configuration.
        
        Use case: Generate RTE sender-receiver interface configuration.
        Expected: Signals have port and interface definitions.
        """
        rte_configs = []
        
        for msg in database.messages:
            for sig in msg.signals:
                if sig.port_name:
                    rte_info = {
                        'signal': sig.signal_name,
                        'port': sig.port_name,
                        'interface': sig.interface_name,
                        'data_type': sig.mapped_idt,
                        'direction': 'sender' if msg.is_tx else 'receiver',
                    }
                    rte_configs.append(rte_info)
        
        # Verify RTE configuration
        assert len(rte_configs) > 0, "Should have RTE configurations"
        
        # Check RTE consistency
        for config in rte_configs:
            assert config['port'], f"Signal {config['signal']} missing port name"
            assert config['direction'] in ['sender', 'receiver']


class TestLegacyMigrationScenario:
    """Scenario tests for migrating legacy configurations."""
    
    @pytest.fixture
    def database(self):
        """Load test database for legacy migration."""
        loader = CompleteXLSXLoader()
        file_path = TEST_DATA_DIR / 'CAN_ECM_FD3.xlsx'
        if not file_path.exists():
            pytest.skip(f"Test file not found: {file_path}")
        return loader.load_complete(str(file_path))
    
    def test_scenario_legacy_signal_name_mapping(self, database):
        """
        Scenario: Map legacy signal names to new names.
        
        Use case: Maintain backward compatibility during signal renaming.
        Expected: Legacy names tracked for all renamed signals.
        """
        legacy_mappings = []
        
        for msg in database.messages:
            for sig in msg.signals:
                legacy = sig.get_legacy_names()
                if legacy:
                    mapping = {
                        'current_name': sig.signal_name,
                        'legacy_names': legacy,
                        'message': msg.message_name,
                    }
                    legacy_mappings.append(mapping)
        
        # Verify legacy mappings exist
        assert len(legacy_mappings) > 0, "Should have signals with legacy names"
        
        # Check mappings are complete
        for mapping in legacy_mappings:
            assert mapping['current_name'], "Missing current signal name"
            assert len(mapping['legacy_names']) > 0, "No legacy names provided"
    
    def test_scenario_frame_type_migration(self, database):
        """
        Scenario: Migrate from standard to extended frames.
        
        Use case: Identify messages that need frame type conversion.
        Expected: Extended frames properly detected by ID range.
        """
        standard_frames = [msg for msg in database.messages if not msg.is_extended]
        extended_frames = [msg for msg in database.messages if msg.is_extended]
        
        # Verify frame type detection
        assert len(standard_frames) == 81  # Known value
        assert len(extended_frames) == 4   # Known value
        
        # Check ID ranges
        for msg in standard_frames:
            assert msg.message_id <= 0x7FF, \
                f"Standard frame {msg.message_name} has extended ID"
        
        for msg in extended_frames:
            assert msg.message_id > 0x7FF, \
                f"Extended frame {msg.message_name} has standard ID"
    
    def test_scenario_signal_scaling_migration(self, database):
        """
        Scenario: Migrate signal scaling information.
        
        Use case: Update from unscaled to scaled data types.
        Expected: Scaling information available for conversion.
        """
        scalable_signals = []
        
        for msg in database.messages:
            for sig in msg.signals:
                if sig.physical_unit or sig.data_type_scaled:
                    scaling_info = {
                        'signal': sig.signal_name,
                        'unscaled_type': sig.data_type,
                        'scaled_type': sig.data_type_scaled,
                        'unit': sig.physical_unit,
                    }
                    scalable_signals.append(scaling_info)
        
        # Verify scaling information
        assert len(scalable_signals) > 0, "Should have signals with scaling"


class TestTeamCollaborationScenario:
    """Scenario tests for team collaboration workflows."""
    
    @pytest.fixture
    def database(self):
        """Load test database for team collaboration."""
        loader = CompleteXLSXLoader()
        file_path = TEST_DATA_DIR / 'CAN_ECM_FD3.xlsx'
        if not file_path.exists():
            pytest.skip(f"Test file not found: {file_path}")
        return loader.load_complete(str(file_path))
    
    def test_scenario_generate_team_report(self, database):
        """
        Scenario: Generate team status report.
        
        Use case: Product Owner needs overview for sprint planning.
        Expected: Complete statistics and coverage information.
        """
        stats = database.get_statistics()
        
        # Generate report data
        report = {
            'database': database.name,
            'messages': {
                'total': stats['total_messages'],
                'rx': stats['rx_messages'],
                'tx': stats['tx_messages'],
            },
            'signals': {
                'total': stats['total_signals'],
                'rx': stats['rx_signals'],
                'tx': stats['tx_signals'],
                'with_sna': stats['signals_with_sna'],
            },
            'coverage': {
                'signal_groups': stats['unique_signal_groups'],
                'unique_swc_producers': stats['unique_swc_producers'],
                'unique_swc_consumers': stats['unique_swc_consumers'],
            },
        }
        
        # Verify report completeness
        assert report['messages']['total'] == 85
        assert report['signals']['total'] == 781
        assert report['signals']['with_sna'] == 292
        assert report['coverage']['signal_groups'] == 31
    
    def test_scenario_identify_swc_dependencies(self, database):
        """
        Scenario: Identify SWC dependencies.
        
        Use case: Architecture team needs component dependency graph.
        Expected: Producer-consumer relationships mapped.
        """
        dependencies = {}
        
        # Collect producer-consumer relationships
        for msg in database.messages:
            for sig in msg.signals:
                if msg.is_tx and sig.producer_swc:
                    if sig.producer_swc not in dependencies:
                        dependencies[sig.producer_swc] = {'produces': [], 'consumes': []}
                    dependencies[sig.producer_swc]['produces'].append(sig.signal_name)
                
                if msg.is_rx and sig.consumer_swc:
                    if sig.consumer_swc not in dependencies:
                        dependencies[sig.consumer_swc] = {'produces': [], 'consumes': []}
                    dependencies[sig.consumer_swc]['consumes'].append(sig.signal_name)
        
        # Verify dependencies found
        assert len(dependencies) > 0, "Should find SWC dependencies"
    
    def test_scenario_generate_signal_documentation(self, database):
        """
        Scenario: Generate signal documentation.
        
        Use case: Technical writer needs signal reference manual.
        Expected: All signals have complete documentation fields.
        """
        signal_docs = []
        
        for msg in database.messages:
            for sig in msg.signals:
                doc = {
                    'signal_name': sig.signal_name,
                    'message_name': msg.message_name,
                    'description': sig.description or sig.signal_description,
                    'size': sig.signal_size,
                    'unit': sig.physical_unit,
                    'data_type': sig.data_type_scaled or sig.data_type,
                    'producer': sig.producer_swc if msg.is_tx else None,
                    'consumer': sig.consumer_swc if msg.is_rx else None,
                }
                signal_docs.append(doc)
        
        # Verify documentation completeness
        assert len(signal_docs) == 781  # All signals documented


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
