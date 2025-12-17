"""
Complete XLSX Loader Example - Load ALL Excel columns.

This example demonstrates loading EVERY field from customer Excel files,
not just basic CAN data.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from autosar.loader import CompleteXLSXLoader


def main():
    print("=" * 80)
    print("Complete XLSX Loader - ALL Columns Demo")
    print("=" * 80)
    
    # Load file
    excel_file = Path(__file__).parent / 'xlsx' / 'CAN_ECM_FD3.xlsx'
    
    if not excel_file.exists():
        print(f"❌ File not found: {excel_file}")
        return
    
    print(f"\n📁 Loading: {excel_file.name}")
    print(f"   (This will parse ALL 44 columns from Rx/Tx sheets)\n")
    
    # Create loader
    loader = CompleteXLSXLoader()
    
    # Load complete database
    database = loader.load_complete(str(excel_file))
    
    # Show statistics
    print("📊 Database Statistics:")
    print("-" * 80)
    stats = database.get_statistics()
    for key, value in stats.items():
        print(f"   {key.replace('_', ' ').title()}: {value}")
    
    # Show sample RX message with ALL fields
    print("\n" + "=" * 80)
    print("🔽 Sample RX Message with COMPLETE Data")
    print("=" * 80)
    
    if database.rx_messages:
        msg = database.rx_messages[0]
        print(f"\n📨 Message: {msg.message_name} (ID: 0x{msg.message_id:X})")
        print(f"   Direction: {msg.direction.value.upper()}")
        print(f"   Extended Frame: {msg.is_extended}")
        print(f"   Signals: {len(msg.signals)}")
        
        if msg.signals:
            sig = msg.signals[0]
            print(f"\n📶 First Signal: {sig.signal_name}")
            print("-" * 80)
            
            # Core CAN data
            print(f"\n   🔧 Core CAN Data:")
            print(f"      Size: {sig.signal_size} bits")
            print(f"      Start Bit: {sig.start_bit}")
            print(f"      Units: {sig.units}")
            print(f"      Signal Group: {sig.signal_group}")
            print(f"      Has SNA: {sig.has_sna}")
            print(f"      Periodicity: {sig.periodicity} ms")
            
            # Legacy names
            print(f"\n   📜 Legacy Names:")
            legacy = sig.get_legacy_names()
            if legacy:
                for name in legacy:
                    print(f"      - {name}")
            else:
                print(f"      (none)")
            
            # BSW Layer (Raw Data)
            print(f"\n   🔌 BSW Layer (Raw Data):")
            print(f"      Data Element: {sig.data_element_name}")
            print(f"      Data Type: {sig.data_type}")
            print(f"      Type Reference: {sig.type_reference}")
            print(f"      Initial Value: {sig.initial_value}")
            print(f"      Invalid Value: {sig.invalid_value}")
            print(f"      Invalidation Policy: {sig.invalidation_policy}")
            print(f"      Conversion Function: {sig.conversion_function}")
            
            # Application Layer (Scaled Data)
            print(f"\n   🎯 Application Layer (Scaled Data):")
            print(f"      Long Name: {sig.long_name}")
            print(f"      Port Name: {sig.port_name}")
            print(f"      Data Type (Scaled): {sig.data_type_scaled}")
            print(f"      Mapped IDT: {sig.mapped_idt}")
            print(f"      Min Value: {sig.signal_min_value}")
            print(f"      Max Value: {sig.signal_max_value}")
            print(f"      Compu Method: {sig.compu_method_name}")
            print(f"      Units (Scaled): {sig.units_scaled}")
            print(f"      Initial Value (Scaled): {sig.initial_value_scaled}")
            
            # Team responsibilities
            print(f"\n   👥 Team Responsibilities:")
            print(f"      MainFunction: {sig.main_function}")
            print(f"      Consumer SWC: {sig.consumer_swc}")
            print(f"      Status: {sig.status}")
            
            # Other fields
            print(f"\n   📝 Other Fields:")
            print(f"      Timeout: {sig.timeout} ms")
            print(f"      Timeout Value: {sig.timeout_value}")
            print(f"      DBC Comment: {sig.dbc_comment[:60]}..." if sig.dbc_comment else "      DBC Comment: None")
            print(f"      Notes: {sig.notes}")
    
    # Show sample TX message
    print("\n" + "=" * 80)
    print("🔼 Sample TX Message with COMPLETE Data")
    print("=" * 80)
    
    if database.tx_messages:
        msg = database.tx_messages[0]
        print(f"\n📨 Message: {msg.message_name} (ID: 0x{msg.message_id:X})")
        print(f"   Direction: {msg.direction.value.upper()}")
        print(f"   Signals: {len(msg.signals)}")
        
        if msg.signals:
            sig = msg.signals[0]
            print(f"\n📶 First Signal: {sig.signal_name}")
            print("-" * 80)
            
            print(f"\n   🔧 Core Data:")
            print(f"      Size: {sig.signal_size} bits")
            print(f"      Start Bit: {sig.start_bit}")
            print(f"      Signal Group: {sig.signal_group}")
            
            print(f"\n   📜 TX-Specific Legacy Names:")
            print(f"      Legacy SRD DD Name: {sig.legacy_srd_dd_name}")
            print(f"      Legacy TX Accessor: {sig.legacy_tx_accessor_name}")
            
            print(f"\n   👥 TX Team Info:")
            print(f"      Producer SWC: {sig.producer_swc}")
            print(f"      PMBD Phase: {sig.pmbd_phase}")
            print(f"      PMBD COE Producer: {sig.pmbd_coe_producer}")
            
            print(f"\n   🔌 BSW Layer:")
            print(f"      Data Element: {sig.data_element_name}")
            print(f"      Data Type: {sig.data_type}")
            print(f"      Conversion: {sig.conversion_function}")
            
            print(f"\n   🎯 Application Layer:")
            print(f"      Port Name: {sig.port_name}")
            print(f"      Data Type (Scaled): {sig.data_type_scaled}")
            print(f"      Compu Method: {sig.compu_method_scaled}")
    
    # Demonstrate column mapping
    print("\n" + "=" * 80)
    print("🗺️  Column Mapping Reference")
    print("=" * 80)
    
    from autosar.model import RxColumnMapping, TxColumnMapping
    
    print("\n📥 RX Sheet Columns (44 total):")
    print("-" * 80)
    mappings = RxColumnMapping.get_all_mappings()
    for i, (excel_col, field_name) in enumerate(mappings.items(), 1):
        print(f"   {i:2d}. {excel_col:40s} → {field_name}")
    
    print(f"\n📤 TX Sheet Columns (43 total):")
    print("-" * 80)
    mappings = TxColumnMapping.get_all_mappings()
    for i, (excel_col, field_name) in enumerate(mappings.items(), 1):
        print(f"   {i:2d}. {excel_col:40s} → {field_name}")
    
    # Demonstrate querying
    print("\n" + "=" * 80)
    print("🔍 Query Examples")
    print("=" * 80)
    
    print(f"\n1. Find message by ID:")
    msg = database.get_message_by_id(0x5B0)
    if msg:
        print(f"   Found: {msg.message_name} with {len(msg.signals)} signals")
    
    print(f"\n2. Get signals by group:")
    if database.messages:
        msg = database.messages[0]
        groups = msg.get_all_signal_groups()
        if groups:
            first_group = groups[0]
            signals = msg.get_signals_by_group(first_group)
            print(f"   Group '{first_group}': {len(signals)} signals")
    
    print(f"\n3. Filter by direction:")
    print(f"   RX Messages: {len(database.rx_messages)}")
    print(f"   TX Messages: {len(database.tx_messages)}")
    
    print("\n" + "=" * 80)
    print("✅ Complete XLSX Loader Demo Finished!")
    print("=" * 80)
    print(f"\n💡 Key Benefits:")
    print(f"   ✅ ALL {44} columns from RX sheet captured")
    print(f"   ✅ ALL {43} columns from TX sheet captured")
    print(f"   ✅ Complete traceability: Excel ↔ Model ↔ AUTOSAR")
    print(f"   ✅ No data loss - every field preserved")
    print(f"   ✅ Type-safe models with validation")
    print(f"   ✅ Bidirectional column mappings")
    print()


if __name__ == '__main__':
    main()
