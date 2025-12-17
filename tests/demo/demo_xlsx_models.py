"""
Example: Use XLSX-specific models to access Excel data.

This example demonstrates how to use XLSXDatabase, XLSXMessage, and XLSXSignal
models to access Excel-specific fields like signal groups, legacy names, SNA, etc.
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from autosar.loader import XLSXLoader
from autosar.model import XLSXDatabase, MessageDirection


def print_section(title: str, width: int = 80):
    """Print a section header."""
    print(f"\n{'='*width}")
    print(f"{title:^{width}}")
    print(f"{'='*width}\n")


def main():
    """Demonstrate XLSX model usage."""
    
    # Load file
    xlsx_path = Path(__file__).parent / "xlsx" / "CAN_ECM_FD3.xlsx"
    
    if not xlsx_path.exists():
        print(f"File not found: {xlsx_path}")
        return
    
    print(f"Loading: {xlsx_path.name}")
    
    # Create loader
    loader = XLSXLoader()
    
    # Load and convert to XLSX model
    data = loader.load(str(xlsx_path))
    loader.validate(data)
    
    # Use XLSX-specific model to preserve all Excel fields
    xlsx_db = loader.to_xlsx_model(data)
    
    # ==================== Database Statistics ====================
    print_section("Database Statistics")
    
    stats = xlsx_db.get_statistics()
    print(f"Database Name: {xlsx_db.name}")
    print(f"Source File: {xlsx_db.source_file}")
    print(f"Version: {xlsx_db.version}")
    print()
    print(f"Messages:")
    print(f"  - Total: {stats['total_messages']}")
    print(f"  - RX: {stats['rx_messages']}")
    print(f"  - TX: {stats['tx_messages']}")
    print(f"  - Standard Frames: {stats['standard_frames']}")
    print(f"  - Extended Frames: {stats['extended_frames']}")
    print()
    print(f"Signals:")
    print(f"  - Total: {stats['total_signals']}")
    print(f"  - With SNA: {stats['signals_with_sna']}")
    print(f"  - Signal Groups: {stats['signal_groups']}")
    print()
    print(f"Nodes: {stats['nodes']}")
    
    # ==================== RX Messages ====================
    print_section("RX Messages (Top 5)")
    
    for i, msg in enumerate(xlsx_db.rx_messages[:5], 1):
        frame_type = "Extended" if msg.is_extended else "Standard"
        print(f"{i}. {msg.name}")
        print(f"   ID: 0x{msg.message_id:03X} ({msg.message_id}) - {frame_type}")
        print(f"   DLC: {msg.dlc} bytes")
        print(f"   Cycle Time: {msg.cycle_time} ms" if msg.cycle_time else "   Cycle Time: N/A")
        print(f"   Signals: {len(msg.signals)}")
        print(f"   Signal Groups: {', '.join(msg.get_signal_groups()) if msg.get_signal_groups() else 'None'}")
        print()
    
    # ==================== TX Messages ====================
    print_section("TX Messages (Top 5)")
    
    for i, msg in enumerate(xlsx_db.tx_messages[:5], 1):
        frame_type = "Extended" if msg.is_extended else "Standard"
        print(f"{i}. {msg.name}")
        print(f"   ID: 0x{msg.message_id:03X} ({msg.message_id}) - {frame_type}")
        print(f"   DLC: {msg.dlc} bytes")
        print(f"   Cycle Time: {msg.cycle_time} ms" if msg.cycle_time else "   Cycle Time: N/A")
        print(f"   Senders: {', '.join(msg.senders)}")
        print(f"   Signals: {len(msg.signals)}")
        print(f"   Signal Groups: {', '.join(msg.get_signal_groups()) if msg.get_signal_groups() else 'None'}")
        print()
    
    # ==================== Signal Groups ====================
    print_section("Signal Groups")
    
    all_groups = xlsx_db.get_all_signal_groups()
    print(f"Total Signal Groups: {len(all_groups)}")
    print()
    
    for i, group in enumerate(all_groups[:10], 1):
        messages_with_group = xlsx_db.get_messages_with_signal_group(group)
        total_signals = sum(
            len(msg.get_signals_by_group(group))
            for msg in messages_with_group
        )
        print(f"{i}. {group}")
        print(f"   Messages: {len(messages_with_group)}")
        print(f"   Signals: {total_signals}")
    
    if len(all_groups) > 10:
        print(f"\n... and {len(all_groups) - 10} more groups")
    
    # ==================== Extended Frames ====================
    if xlsx_db.extended_messages:
        print_section("Extended Frame Messages")
        
        for msg in xlsx_db.extended_messages:
            print(f"- {msg.name}")
            print(f"  ID: 0x{msg.message_id:08X}")
            print(f"  Direction: {msg.direction.value.upper()}")
            print(f"  Signals: {len(msg.signals)}")
            print()
    
    # ==================== Signal Details with Excel-specific Fields ====================
    print_section("Signal Details (First Message)")
    
    first_msg = xlsx_db.messages[0]
    print(f"Message: {first_msg.name} (0x{first_msg.message_id:03X})")
    print(f"Direction: {first_msg.direction.value.upper()}")
    print()
    
    for i, signal in enumerate(first_msg.signals[:5], 1):
        print(f"{i}. {signal.name}")
        print(f"   Length: {signal.length} bits")
        print(f"   Unit: {signal.unit if signal.unit else 'N/A'}")
        print(f"   Signal Group: {signal.signal_group if signal.signal_group else 'None'}")
        print(f"   Has SNA: {'Yes' if signal.has_sna else 'No'}")
        print(f"   Periodicity: {signal.periodicity} ms" if signal.periodicity else "   Periodicity: N/A")
        
        # Show Excel-specific fields for RX signals
        if first_msg.is_rx:
            if signal.legacy_srd_name:
                print(f"   Legacy SRD Name: {signal.legacy_srd_name}")
            if signal.legacy_impl_name:
                print(f"   Legacy Impl Name: {signal.legacy_impl_name}")
        
        # Show notes for TX signals
        if first_msg.is_tx and signal.notes:
            print(f"   Notes: {signal.notes}")
        
        print()
    
    if len(first_msg.signals) > 5:
        print(f"... and {len(first_msg.signals) - 5} more signals")
    
    # ==================== Query Examples ====================
    print_section("Query Examples")
    
    # Find message by ID
    test_id = 0x5B0
    msg = xlsx_db.get_message_by_id(test_id)
    if msg:
        print(f"1. Find message by ID (0x{test_id:03X}):")
        print(f"   Found: {msg.name}")
        print(f"   Direction: {msg.direction.value.upper()}")
        print(f"   Signals: {len(msg.signals)}")
    print()
    
    # Find message by name
    test_name = xlsx_db.messages[0].name
    msg = xlsx_db.get_message_by_name(test_name)
    if msg:
        print(f"2. Find message by name ('{test_name}'):")
        print(f"   ID: 0x{msg.message_id:03X}")
        print(f"   Frame Type: {'Extended' if msg.is_extended else 'Standard'}")
    print()
    
    # Get signals by group
    if first_msg.get_signal_groups():
        group_name = first_msg.get_signal_groups()[0]
        signals_in_group = first_msg.get_signals_by_group(group_name)
        print(f"3. Get signals in group '{group_name}':")
        print(f"   Signals: {len(signals_in_group)}")
        for sig in signals_in_group[:3]:
            print(f"   - {sig.name}")
        if len(signals_in_group) > 3:
            print(f"   ... and {len(signals_in_group) - 3} more")
    print()
    
    # Count signals with SNA
    signals_with_sna = [
        sig for msg in xlsx_db.messages
        for sig in msg.signals
        if sig.has_sna
    ]
    print(f"4. Signals with SNA indicator:")
    print(f"   Total: {len(signals_with_sna)}")
    if signals_with_sna:
        print(f"   Examples:")
        for sig in signals_with_sna[:5]:
            print(f"   - {sig.name}")
    
    # ==================== Convert to Standard CAN Model ====================
    print_section("Convert to Standard CAN Model")
    
    # XLSXDatabase can be converted to standard CANDatabase
    can_db = xlsx_db.to_can_database()
    
    print(f"Original XLSX Database:")
    print(f"  - Name: {xlsx_db.name}")
    print(f"  - Messages: {len(xlsx_db.messages)}")
    print(f"  - RX/TX info: Preserved")
    print(f"  - Signal groups: Preserved")
    print(f"  - Legacy names: Preserved")
    print()
    print(f"Converted CAN Database:")
    print(f"  - Name: {can_db.name}")
    print(f"  - Messages: {len(can_db.messages)}")
    print(f"  - RX/TX info: Lost (not in CAN model)")
    print(f"  - Signal groups: Lost (not in CAN model)")
    print(f"  - Legacy names: Lost (not in CAN model)")
    print()
    print("Use XLSXDatabase when you need Excel-specific fields!")
    print("Use CANDatabase for standard AUTOSAR workflows.")
    
    print_section("Done!")


if __name__ == "__main__":
    main()
