"""
Example: Load CAN configuration from XLSX file.

This example demonstrates how to use XLSXLoader to load CAN message
and signal definitions from Excel files.
"""

from pathlib import Path
import sys

# Add src to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from autosar.loader import XLSXLoader
from autosar.model import CANDatabase


def main():
    """Load and display XLSX CAN configuration."""
    
    # Path to example XLSX file
    examples_dir = Path(__file__).parent
    xlsx_files = [
        "xlsx/CAN_ECM_FD3.xlsx",
        "xlsx/CAN_ECM_FD14.xlsx",
        "xlsx/CAN_ECM_FD16.xlsx",
    ]
    
    # Create loader
    loader = XLSXLoader()
    
    for xlsx_file in xlsx_files:
        xlsx_path = examples_dir / xlsx_file
        
        if not xlsx_path.exists():
            print(f"⚠️  File not found: {xlsx_path}")
            continue
        
        print(f"\n{'='*80}")
        print(f"Loading: {xlsx_path.name}")
        print(f"{'='*80}")
        
        try:
            # Step 1: Load file
            print("\n📂 Loading XLSX file...")
            data = loader.load(str(xlsx_path))
            
            print(f"✅ Loaded successfully!")
            print(f"   - RX messages: {data['rx_count']}")
            print(f"   - TX messages: {data['tx_count']}")
            print(f"   - Total messages: {len(data['messages'])}")
            print(f"   - Nodes: {len(data['nodes'])}")
            
            # Step 2: Validate
            print("\n🔍 Validating data...")
            loader.validate(data)
            print("✅ Validation passed!")
            
            # Step 3: Convert to model
            print("\n🔄 Converting to CANDatabase model...")
            database = loader.to_model(data)
            print(f"✅ Converted to model: {database.name}")
            
            # Display summary
            print(f"\n📊 Database Summary:")
            print(f"   Name: {database.name}")
            print(f"   Version: {database.version}")
            print(f"   Messages: {len(database.messages)}")
            
            # Calculate total signals
            total_signals = sum(len(msg.signals) for msg in database.messages)
            print(f"   Total Signals: {total_signals}")
            
            # Display RX/TX breakdown
            rx_messages = [m for m in data['messages'] if m.get('direction') == 'rx']
            tx_messages = [m for m in data['messages'] if m.get('direction') == 'tx']
            
            print(f"\n📥 RX Messages: {len(rx_messages)}")
            if rx_messages:
                print("   Top 5:")
                for i, msg in enumerate(rx_messages[:5], 1):
                    print(f"     {i}. {msg['name']} (0x{msg['message_id']:03X}) - {len(msg['signals'])} signals")
            
            print(f"\n📤 TX Messages: {len(tx_messages)}")
            if tx_messages:
                print("   Top 5:")
                for i, msg in enumerate(tx_messages[:5], 1):
                    print(f"     {i}. {msg['name']} (0x{msg['message_id']:03X}) - {len(msg['signals'])} signals")
            
            # Display sample message details
            if database.messages:
                print(f"\n📋 Sample Message Details:")
                sample_msg = database.messages[0]
                print(f"   Message: {sample_msg.name}")
                print(f"   ID: 0x{sample_msg.message_id:03X} ({sample_msg.message_id})")
                print(f"   DLC: {sample_msg.dlc} bytes")
                print(f"   Cycle Time: {sample_msg.cycle_time} ms" if sample_msg.cycle_time else "   Cycle Time: N/A")
                print(f"   Signals: {len(sample_msg.signals)}")
                
                if sample_msg.signals:
                    print(f"\n   📊 Signals:")
                    for i, signal in enumerate(sample_msg.signals[:5], 1):
                        print(f"      {i}. {signal.name}")
                        print(f"         - Length: {signal.length} bits")
                        print(f"         - Unit: {signal.unit if signal.unit else 'N/A'}")
                        print(f"         - Receivers: {', '.join(signal.receivers) if signal.receivers else 'N/A'}")
                    
                    if len(sample_msg.signals) > 5:
                        print(f"      ... and {len(sample_msg.signals) - 5} more signals")
            
            # Display nodes
            if data['nodes']:
                print(f"\n🖥️  Nodes ({len(data['nodes'])}):")
                for node in data['nodes'][:10]:
                    print(f"   - {node['name']}")
                if len(data['nodes']) > 10:
                    print(f"   ... and {len(data['nodes']) - 10} more nodes")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print(f"\n{'='*80}")
    print("✅ All files processed!")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
