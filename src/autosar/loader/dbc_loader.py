"""
DBC (CAN Database) file loader.

Loads and parses DBC files using the cantools library.
"""

from typing import Dict, Any, List, Optional
import logging
from pathlib import Path

try:
    import cantools
except ImportError:
    raise ImportError(
        "cantools is required for DBC loading. "
        "Install with: pip install cantools"
    )

from .base_loader import BaseLoader, ParserError, ValidationError, ConversionError
from ..model import (
    CANDatabase, CANMessage, CANSignal, CANNode,
    ValueTable, ValueTableEntry,
    ByteOrder, ValueType, SignalType
)


class DBCLoader(BaseLoader[CANDatabase]):
    """
    Loader for DBC (CAN Database) files.
    
    Uses cantools library to parse DBC format and converts to CANDatabase model.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize DBC loader."""
        super().__init__(logger)
        self._db: Optional[cantools.database.can.Database] = None
    
    def load(self, file_path: str) -> Dict[str, Any]:
        """
        Load and parse DBC file.
        
        Args:
            file_path: Path to DBC file
            
        Returns:
            Dictionary with parsed database structure
            
        Raises:
            FileNotFoundError: If file does not exist
            ParserError: If DBC parsing fails
        """
        # Validate file exists and has correct extension
        path = self._validate_file_exists(file_path)
        self._validate_file_extension(path, ['.dbc', '.DBC'])
        
        try:
            # Load DBC using cantools
            self.logger.info(f"Parsing DBC file: {path}")
            self._db = cantools.database.load_file(str(path))
            
            # Extract data into dictionary
            data = {
                'version': getattr(self._db, 'version', '1.0'),
                'messages': [self._extract_message(msg) for msg in self._db.messages],
                'nodes': [self._extract_node(node) for node in self._db.nodes],
                'dbc_object': self._db,  # Keep reference for advanced usage
                'file_path': str(path),
            }
            
            self.logger.info(
                f"Loaded {len(data['messages'])} messages, "
                f"{len(data['nodes'])} nodes"
            )
            
            return data
            
        except Exception as e:
            raise ParserError(f"Failed to parse DBC file: {e}") from e
    
    def _extract_message(self, msg: cantools.database.can.Message) -> Dict[str, Any]:
        """Extract message data from cantools Message object."""
        return {
            'name': msg.name,
            'message_id': msg.frame_id,
            'is_extended': msg.is_extended_frame,
            'dlc': msg.length,
            'cycle_time': msg.cycle_time,
            'senders': msg.senders if msg.senders else [],
            'comment': msg.comment,
            'signals': [self._extract_signal(sig) for sig in msg.signals],
        }
    
    def _extract_signal(self, sig: cantools.database.can.Signal) -> Dict[str, Any]:
        """Extract signal data from cantools Signal object."""
        # Determine byte order
        byte_order = ByteOrder.LITTLE_ENDIAN if sig.byte_order == 'little_endian' else ByteOrder.BIG_ENDIAN
        
        # Determine value type
        if sig.is_float:
            value_type = ValueType.FLOAT
        elif sig.is_signed:
            value_type = ValueType.SIGNED
        else:
            value_type = ValueType.UNSIGNED
        
        # Determine signal type
        if sig.is_multiplexer:
            signal_type = SignalType.MULTIPLEXER
        elif sig.multiplexer_ids is not None and len(sig.multiplexer_ids) > 0:
            signal_type = SignalType.MULTIPLEXED
        else:
            signal_type = SignalType.STANDARD
        
        return {
            'name': sig.name,
            'start_bit': sig.start,
            'length': sig.length,
            'byte_order': byte_order,
            'value_type': value_type,
            'signal_type': signal_type,
            'factor': sig.scale,
            'offset': sig.offset,
            'min_value': sig.minimum,
            'max_value': sig.maximum,
            'unit': sig.unit,
            'initial_value': getattr(sig, 'initial_value', None),
            'receivers': sig.receivers if sig.receivers else [],
            'comment': sig.comment,
            'choices': sig.choices,  # Value table
        }
    
    def _extract_node(self, node: cantools.database.can.Node) -> Dict[str, Any]:
        """Extract node data from cantools Node object."""
        return {
            'name': node.name,
            'comment': node.comment,
        }
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """
        Validate parsed DBC data.
        
        Args:
            data: Parsed DBC data
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If validation fails
        """
        # Check required keys
        required_keys = ['messages', 'nodes', 'version']
        for key in required_keys:
            if key not in data:
                raise ValidationError(f"Missing required key: {key}")
        
        # Validate messages
        if not isinstance(data['messages'], list):
            raise ValidationError("'messages' must be a list")
        
        # Validate nodes
        if not isinstance(data['nodes'], list):
            raise ValidationError("'nodes' must be a list")
        
        self.logger.debug("DBC data validation successful")
        return True
    
    def to_model(self, data: Dict[str, Any]) -> CANDatabase:
        """
        Convert parsed DBC data to CANDatabase model.
        
        Args:
            data: Validated DBC data
            
        Returns:
            CANDatabase model object
            
        Raises:
            ConversionError: If conversion fails
        """
        try:
            # Convert messages
            messages = []
            for msg_data in data['messages']:
                # Convert signals first
                signals = []
                for sig_data in msg_data['signals']:
                    # Handle value table (choices)
                    value_table = None
                    if sig_data.get('choices'):
                        entries = [
                            ValueTableEntry(
                                name=f"{sig_data['name']}_entry_{val}",
                                value=val,
                                label=str(label)  # Convert to string (can be NamedSignalValue)
                            )
                            for val, label in sig_data['choices'].items()
                        ]
                        value_table = ValueTable(
                            name=f"{sig_data['name']}_values",
                            entries=entries
                        )
                    
                    signal = CANSignal(
                        name=sig_data['name'],
                        short_name=sig_data['name'],
                        start_bit=sig_data['start_bit'],
                        length=sig_data['length'],
                        byte_order=sig_data['byte_order'],
                        value_type=sig_data['value_type'],
                        signal_type=sig_data['signal_type'],
                        factor=sig_data['factor'],
                        offset=sig_data['offset'],
                        min_value=sig_data.get('min_value'),
                        max_value=sig_data.get('max_value'),
                        unit=sig_data.get('unit'),
                        initial_value=sig_data.get('initial_value'),
                        receivers=sig_data['receivers'],
                        value_table=value_table,
                        description=sig_data.get('comment'),
                    )
                    signals.append(signal)
                
                # Create message
                sender = msg_data['senders'][0] if msg_data['senders'] else None
                message = CANMessage(
                    name=msg_data['name'],
                    short_name=msg_data['name'],
                    message_id=msg_data['message_id'],
                    is_extended=msg_data['is_extended'],
                    dlc=msg_data['dlc'],
                    signals=signals,
                    cycle_time=msg_data.get('cycle_time'),
                    sender=sender,
                    comment=msg_data.get('comment'),
                    description=msg_data.get('comment'),
                )
                messages.append(message)
            
            # Convert nodes
            nodes = []
            for node_data in data['nodes']:
                node = CANNode(
                    name=node_data['name'],
                    short_name=node_data['name'],
                    comment=node_data.get('comment'),
                    description=node_data.get('comment'),
                )
                nodes.append(node)
            
            # Create database
            file_name = Path(data['file_path']).stem if 'file_path' in data else 'database'
            database = CANDatabase(
                name=file_name,
                version=data['version'],
                messages=messages,
                nodes=nodes,
            )
            
            self.logger.info(f"Converted to CANDatabase: {database.name}")
            return database
            
        except Exception as e:
            raise ConversionError(f"Failed to convert to model: {e}") from e
